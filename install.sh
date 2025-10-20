#!/bin/bash

###############################################################################
# Script de Instalación Automática - Aplicación de Gestión de Taller
# Para Ubuntu 20.04+
# 
# Uso: sudo bash install.sh
###############################################################################

set -e  # Salir si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # Sin color

# Variables globales
INSTALL_DIR="/var/www/taller-app"
LOG_FILE="/var/log/taller-install.log"
BACKUP_DIR="/var/backups/taller-db"
APP_USER="www-data"

###############################################################################
# FUNCIONES AUXILIARES
###############################################################################

print_header() {
    echo ""
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}============================================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ ERROR: $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "Este script debe ejecutarse como root (sudo)"
        exit 1
    fi
}

check_ubuntu() {
    if [ ! -f /etc/os-release ]; then
        print_error "No se puede determinar el sistema operativo"
        exit 1
    fi
    
    . /etc/os-release
    if [[ "$ID" != "ubuntu" ]]; then
        print_error "Este script solo funciona en Ubuntu"
        exit 1
    fi
    
    print_success "Sistema operativo: Ubuntu $VERSION"
}

###############################################################################
# FUNCIONES DE INSTALACIÓN
###############################################################################

install_dependencies() {
    print_header "Instalando Dependencias del Sistema"
    
    log "Actualizando sistema..."
    apt update >> "$LOG_FILE" 2>&1
    print_success "Repositorios actualizados"
    
    log "Instalando dependencias básicas..."
    apt install -y curl wget git software-properties-common \
        apt-transport-https ca-certificates gnupg lsb-release netcat-openbsd >> "$LOG_FILE" 2>&1
    print_success "Dependencias básicas instaladas"
}

install_python() {
    print_header "Instalando Python 3"
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | awk '{print $2}')
        print_info "Python $PYTHON_VERSION ya está instalado"
    else
        log "Instalando Python3..."
        apt install -y python3 python3-pip python3-venv python3-dev >> "$LOG_FILE" 2>&1
        print_success "Python3 instalado"
    fi
}

install_nodejs() {
    print_header "Instalando Node.js y Yarn"
    
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_info "Node.js $NODE_VERSION ya está instalado"
    else
        log "Instalando Node.js 18.x..."
        curl -fsSL https://deb.nodesource.com/setup_18.x | bash - >> "$LOG_FILE" 2>&1
        apt install -y nodejs >> "$LOG_FILE" 2>&1
        print_success "Node.js instalado"
    fi
    
    if command -v yarn &> /dev/null; then
        print_info "Yarn ya está instalado"
    else
        log "Instalando Yarn..."
        npm install -g yarn >> "$LOG_FILE" 2>&1
        print_success "Yarn instalado"
    fi
}

install_mongodb() {
    print_header "Verificando MongoDB"
    
    # Verificar si MongoDB está en Docker
    if command -v docker &> /dev/null; then
        if docker ps | grep -q mongo; then
            print_success "MongoDB detectado en Docker"
            
            # Verificar que el puerto 27017 está accesible
            if nc -z localhost 27017 2>/dev/null || timeout 2 bash -c 'cat < /dev/null > /dev/tcp/localhost/27017' 2>/dev/null; then
                print_success "MongoDB accesible en puerto 27017"
                
                # Configurar contenedor para auto-inicio
                MONGO_CONTAINER=$(docker ps --filter "ancestor=mongo" --format "{{.Names}}" | head -1)
                if [ ! -z "$MONGO_CONTAINER" ]; then
                    docker update --restart unless-stopped "$MONGO_CONTAINER" > /dev/null 2>&1
                    print_success "MongoDB configurado para auto-inicio"
                fi
                
                return
            else
                print_error "MongoDB en Docker no está accesible en puerto 27017"
                print_info "Verifica que el contenedor expone el puerto: docker ps"
                exit 1
            fi
        fi
    fi
    
    # Verificar si MongoDB está instalado nativamente
    if command -v mongod &> /dev/null; then
        MONGO_VERSION=$(mongod --version | head -1 || echo "desconocida")
        print_info "MongoDB instalado nativamente: $MONGO_VERSION"
        
        # Verificar si está corriendo
        if systemctl is-active --quiet mongod; then
            print_success "MongoDB está corriendo"
            return
        else
            print_info "Iniciando MongoDB existente..."
            systemctl start mongod
            systemctl enable mongod >> "$LOG_FILE" 2>&1
            sleep 3
            
            if systemctl is-active --quiet mongod; then
                print_success "MongoDB iniciado correctamente"
                return
            else
                print_warning "No se pudo iniciar MongoDB automáticamente"
                print_info "Intenta iniciarlo manualmente: sudo systemctl start mongod"
                exit 1
            fi
        fi
    fi
    
    # Si no está instalado de ninguna forma
    print_error "MongoDB no está instalado"
    print_info "La aplicación requiere MongoDB para funcionar"
    print_info ""
    print_info "Opciones:"
    print_info "1. Instalar en Docker (recomendado para CPUs sin AVX):"
    print_info "   sudo docker pull mongo:4.4"
    print_info "   sudo docker run -d --name mongodb --restart unless-stopped -p 27017:27017 mongo:4.4"
    print_info ""
    print_info "2. Instalar nativamente (requiere AVX):"
    print_info "   sudo apt install mongodb-org"
    print_info ""
    print_info "Luego vuelve a ejecutar este script"
    exit 1
}

install_apache() {
    print_header "Instalando Apache2"
    
    log "Instalando Apache2..."
    apt install -y apache2 >> "$LOG_FILE" 2>&1
    
    # Habilitar módulos necesarios
    log "Habilitando módulos de Apache..."
    a2enmod proxy >> "$LOG_FILE" 2>&1
    a2enmod proxy_http >> "$LOG_FILE" 2>&1
    a2enmod rewrite >> "$LOG_FILE" 2>&1
    a2enmod ssl >> "$LOG_FILE" 2>&1
    a2enmod headers >> "$LOG_FILE" 2>&1
    
    systemctl restart apache2
    systemctl enable apache2 >> "$LOG_FILE" 2>&1
    
    print_success "Apache2 instalado y configurado"
}

setup_application_structure() {
    print_header "Configurando Estructura de la Aplicación"
    
    log "Creando directorios..."
    mkdir -p "$INSTALL_DIR"/{backend,frontend}
    mkdir -p "$BACKUP_DIR"
    
    # Verificar que los archivos de la aplicación existen
    if [ ! -d "/app/backend" ] || [ ! -d "/app/frontend" ]; then
        print_error "No se encuentran los archivos de la aplicación en /app"
        print_info "Asegúrate de que los archivos estén en /app/backend y /app/frontend"
        exit 1
    fi
    
    log "Copiando archivos de backend..."
    cp -r /app/backend/* "$INSTALL_DIR/backend/" >> "$LOG_FILE" 2>&1
    
    log "Copiando archivos de frontend..."
    cp -r /app/frontend/* "$INSTALL_DIR/frontend/" >> "$LOG_FILE" 2>&1
    
    print_success "Estructura de aplicación creada"
}

setup_backend() {
    print_header "Configurando Backend (FastAPI)"
    
    cd "$INSTALL_DIR/backend"
    
    log "Creando entorno virtual de Python..."
    python3 -m venv venv >> "$LOG_FILE" 2>&1
    
    log "Instalando dependencias de Python..."
    source venv/bin/activate
    pip install --upgrade pip >> "$LOG_FILE" 2>&1
    pip install -r requirements.txt >> "$LOG_FILE" 2>&1
    
    # Generar JWT secret seguro
    JWT_SECRET=$(openssl rand -hex 32)
    
    log "Creando archivo .env..."
    cat > .env << EOF
MONGO_URL=mongodb://localhost:27017
DB_NAME=taller_production
CORS_ORIGINS=*
JWT_SECRET=$JWT_SECRET
EOF
    
    chmod 600 .env
    
    print_success "Backend configurado"
}

setup_database() {
    print_header "Configurando Base de Datos"
    
    cd "$INSTALL_DIR/backend"
    source venv/bin/activate
    
    log "Poblando modelos iniciales..."
    python3 << 'PYEOF' >> "$LOG_FILE" 2>&1
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def seed_data():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['taller_production']
    
    models = [
        {'id': 'model-1', 'name': 'Altair'},
        {'id': 'model-2', 'name': 'Altair Pro'},
        {'id': 'model-3', 'name': 'Altair 2X'},
        {'id': 'model-4', 'name': 'Altair 4X'},
        {'id': 'model-5', 'name': 'Altair 4XR'},
        {'id': 'model-6', 'name': 'Altair 5X'},
        {'id': 'model-7', 'name': 'Altair IO4'}
    ]
    
    count = await db.models.count_documents({})
    if count == 0:
        await db.models.insert_many(models)
        print(f'{len(models)} modelos insertados')
    else:
        print(f'Ya existen {count} modelos')
    
    client.close()

asyncio.run(seed_data())
PYEOF
    
    log "Creando usuario administrador..."
    python3 << 'PYEOF' >> "$LOG_FILE" 2>&1
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime, timezone

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['taller_production']
    
    admin_user = {
        'id': 'admin-001',
        'username': 'admin',
        'full_name': 'Administrador',
        'hashed_password': pwd_context.hash('admin123'),
        'created_at': datetime.now(timezone.utc).isoformat()
    }
    
    existing = await db.users.find_one({'username': 'admin'})
    if not existing:
        await db.users.insert_one(admin_user)
        print('Usuario admin creado')
    else:
        print('Usuario admin ya existe')
    
    client.close()

asyncio.run(create_admin())
PYEOF
    
    print_success "Base de datos configurada"
}

setup_frontend() {
    print_header "Configurando Frontend (React)"
    
    cd "$INSTALL_DIR/frontend"
    
    # Pedir dominio al usuario
    read -p "Ingresa tu dominio (ej: midominio.com) o presiona Enter para usar 'localhost': " DOMAIN
    DOMAIN=${DOMAIN:-localhost}
    
    if [ "$DOMAIN" = "localhost" ]; then
        BACKEND_URL="http://localhost"
    else
        BACKEND_URL="http://$DOMAIN"
    fi
    
    log "Creando archivo .env para frontend..."
    cat > .env << EOF
REACT_APP_BACKEND_URL=$BACKEND_URL
EOF
    
    log "Instalando dependencias de Node.js (esto puede tardar varios minutos)..."
    yarn install >> "$LOG_FILE" 2>&1
    
    log "Construyendo aplicación de producción..."
    yarn build >> "$LOG_FILE" 2>&1
    
    print_success "Frontend configurado"
    
    # Guardar dominio para usarlo después
    echo "$DOMAIN" > /tmp/taller_domain.txt
}

setup_systemd_service() {
    print_header "Configurando Servicio Systemd"
    
    log "Creando servicio taller-backend..."
    cat > /etc/systemd/system/taller-backend.service << EOF
[Unit]
Description=Taller Backend FastAPI
After=network.target mongod.service

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$INSTALL_DIR/backend
Environment="PATH=$INSTALL_DIR/backend/venv/bin"
ExecStart=$INSTALL_DIR/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --workers 4

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable taller-backend >> "$LOG_FILE" 2>&1
    systemctl start taller-backend
    
    sleep 3
    
    if systemctl is-active --quiet taller-backend; then
        print_success "Servicio backend iniciado"
    else
        print_error "El servicio backend no pudo iniciarse"
        journalctl -u taller-backend -n 20
        exit 1
    fi
}

setup_apache_vhost() {
    print_header "Configurando Apache Virtual Host"
    
    # Leer dominio guardado
    DOMAIN=$(cat /tmp/taller_domain.txt)
    
    log "Creando configuración de Apache..."
    cat > /etc/apache2/sites-available/taller-app.conf << EOF
<VirtualHost *:80>
    ServerName $DOMAIN
    ServerAlias www.$DOMAIN
    
    ErrorLog \${APACHE_LOG_DIR}/taller-error.log
    CustomLog \${APACHE_LOG_DIR}/taller-access.log combined
    
    DocumentRoot $INSTALL_DIR/frontend/build
    
    <Directory $INSTALL_DIR/frontend/build>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
        
        RewriteEngine On
        RewriteBase /
        RewriteRule ^index\.html$ - [L]
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteRule . /index.html [L]
    </Directory>
    
    ProxyPreserveHost On
    ProxyRequests Off
    
    <Location /api>
        ProxyPass http://localhost:8001/api
        ProxyPassReverse http://localhost:8001/api
    </Location>
</VirtualHost>
EOF
    
    # Deshabilitar sitio por defecto
    a2dissite 000-default.conf >> "$LOG_FILE" 2>&1
    
    # Habilitar nuestro sitio
    a2ensite taller-app.conf >> "$LOG_FILE" 2>&1
    
    # Verificar configuración
    apache2ctl configtest >> "$LOG_FILE" 2>&1
    
    # Reiniciar Apache
    systemctl restart apache2
    
    print_success "Apache configurado"
}

setup_permissions() {
    print_header "Configurando Permisos"
    
    log "Estableciendo permisos correctos..."
    chown -R $APP_USER:$APP_USER "$INSTALL_DIR"
    chmod -R 755 "$INSTALL_DIR"
    chmod 600 "$INSTALL_DIR/backend/.env"
    chmod 600 "$INSTALL_DIR/frontend/.env"
    
    print_success "Permisos configurados"
}

setup_firewall() {
    print_header "Configurando Firewall"
    
    if command -v ufw &> /dev/null; then
        log "Configurando UFW..."
        
        # Permitir SSH
        ufw allow ssh >> "$LOG_FILE" 2>&1
        
        # Permitir HTTP y HTTPS
        ufw allow 80/tcp >> "$LOG_FILE" 2>&1
        ufw allow 443/tcp >> "$LOG_FILE" 2>&1
        
        # Habilitar UFW si no está habilitado
        if ! ufw status | grep -q "Status: active"; then
            echo "y" | ufw enable >> "$LOG_FILE" 2>&1
        fi
        
        print_success "Firewall configurado"
    else
        print_warning "UFW no está instalado, saltando configuración de firewall"
    fi
}

setup_ssl() {
    print_header "Configuración SSL (Opcional)"
    
    DOMAIN=$(cat /tmp/taller_domain.txt)
    
    if [ "$DOMAIN" = "localhost" ]; then
        print_info "Saltando configuración SSL (usando localhost)"
        return
    fi
    
    echo ""
    read -p "¿Deseas instalar certificado SSL gratuito con Let's Encrypt? (s/n): " INSTALL_SSL
    
    if [ "$INSTALL_SSL" = "s" ] || [ "$INSTALL_SSL" = "S" ]; then
        log "Instalando Certbot..."
        apt install -y certbot python3-certbot-apache >> "$LOG_FILE" 2>&1
        
        print_info "Obteniendo certificado SSL..."
        print_warning "Asegúrate de que tu dominio apunte a este servidor"
        
        read -p "Ingresa tu email para Let's Encrypt: " EMAIL
        
        certbot --apache -d "$DOMAIN" -d "www.$DOMAIN" \
            --non-interactive --agree-tos --email "$EMAIL" \
            >> "$LOG_FILE" 2>&1
        
        if [ $? -eq 0 ]; then
            # Actualizar .env del frontend para usar HTTPS
            cd "$INSTALL_DIR/frontend"
            sed -i "s|http://|https://|g" .env
            yarn build >> "$LOG_FILE" 2>&1
            
            print_success "SSL configurado correctamente"
        else
            print_warning "No se pudo obtener el certificado SSL"
            print_info "Puedes intentarlo manualmente después con: sudo certbot --apache"
        fi
    else
        print_info "Saltando configuración SSL"
    fi
}

create_maintenance_scripts() {
    print_header "Creando Scripts de Mantenimiento"
    
    log "Creando script de backup..."
    cat > /usr/local/bin/taller-backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/taller-db"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"
mongodump --db taller_production --out "$BACKUP_DIR/backup-$DATE"
# Mantener solo los últimos 7 backups
find "$BACKUP_DIR" -type d -name "backup-*" -mtime +7 -exec rm -rf {} \;
echo "Backup completado: $DATE"
EOF
    
    chmod +x /usr/local/bin/taller-backup.sh
    
    # Agregar cron job para backup diario
    (crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/taller-backup.sh >> /var/log/taller-backup.log 2>&1") | crontab -
    
    print_success "Scripts de mantenimiento creados"
}

verify_installation() {
    print_header "Verificando Instalación"
    
    # Verificar MongoDB
    if systemctl is-active --quiet mongod; then
        print_success "MongoDB: Corriendo"
    else
        print_error "MongoDB: No está corriendo"
    fi
    
    # Verificar Backend
    if systemctl is-active --quiet taller-backend; then
        print_success "Backend: Corriendo"
    else
        print_error "Backend: No está corriendo"
    fi
    
    # Verificar Apache
    if systemctl is-active --quiet apache2; then
        print_success "Apache2: Corriendo"
    else
        print_error "Apache2: No está corriendo"
    fi
    
    # Probar API
    sleep 2
    if curl -s http://localhost:8001/api/ > /dev/null; then
        print_success "API: Respondiendo correctamente"
    else
        print_warning "API: No responde (puede necesitar más tiempo)"
    fi
}

print_final_info() {
    DOMAIN=$(cat /tmp/taller_domain.txt)
    SSL_ENABLED=false
    
    if [ -f "/etc/letsencrypt/live/$DOMAIN/cert.pem" ]; then
        SSL_ENABLED=true
    fi
    
    clear
    print_header "¡INSTALACIÓN COMPLETADA!"
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    INFORMACIÓN DE ACCESO                       ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    if [ "$SSL_ENABLED" = true ]; then
        echo -e "  🌐 URL de la aplicación: ${BLUE}https://$DOMAIN${NC}"
    else
        if [ "$DOMAIN" = "localhost" ]; then
            echo -e "  🌐 URL de la aplicación: ${BLUE}http://localhost${NC}"
            echo -e "  🌐 URL alternativa: ${BLUE}http://$(hostname -I | awk '{print $1}')${NC}"
        else
            echo -e "  🌐 URL de la aplicación: ${BLUE}http://$DOMAIN${NC}"
        fi
    fi
    
    echo ""
    echo -e "${YELLOW}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║                  CREDENCIALES POR DEFECTO                      ║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  👤 Usuario: ${BLUE}admin${NC}"
    echo -e "  🔑 Contraseña: ${BLUE}admin123${NC}"
    echo ""
    echo -e "  ${RED}⚠️  ¡IMPORTANTE! Cambia esta contraseña después del primer login${NC}"
    echo ""
    
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                      COMANDOS ÚTILES                           ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  📊 Ver estado de servicios:"
    echo -e "     ${GREEN}sudo systemctl status taller-backend${NC}"
    echo -e "     ${GREEN}sudo systemctl status apache2${NC}"
    echo -e "     ${GREEN}sudo systemctl status mongod${NC}"
    echo ""
    echo -e "  🔄 Reiniciar servicios:"
    echo -e "     ${GREEN}sudo systemctl restart taller-backend${NC}"
    echo -e "     ${GREEN}sudo systemctl restart apache2${NC}"
    echo ""
    echo -e "  📝 Ver logs:"
    echo -e "     ${GREEN}sudo journalctl -u taller-backend -f${NC}"
    echo -e "     ${GREEN}sudo tail -f /var/log/apache2/taller-error.log${NC}"
    echo ""
    echo -e "  💾 Hacer backup manual:"
    echo -e "     ${GREEN}sudo /usr/local/bin/taller-backup.sh${NC}"
    echo ""
    
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                         ARCHIVOS                               ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  📁 Aplicación: ${BLUE}$INSTALL_DIR${NC}"
    echo -e "  📋 Log de instalación: ${BLUE}$LOG_FILE${NC}"
    echo -e "  💾 Backups: ${BLUE}$BACKUP_DIR${NC}"
    echo ""
    
    if [ "$SSL_ENABLED" = false ] && [ "$DOMAIN" != "localhost" ]; then
        echo -e "${YELLOW}╔════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${YELLOW}║                  CONFIGURAR SSL DESPUÉS                        ║${NC}"
        echo -e "${YELLOW}╚════════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo -e "  Para habilitar HTTPS ejecuta:"
        echo -e "  ${GREEN}sudo certbot --apache -d $DOMAIN -d www.$DOMAIN${NC}"
        echo ""
    fi
    
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo ""
    print_success "¡Todo listo! La aplicación está corriendo 🚀"
    echo ""
}

###############################################################################
# FUNCIÓN PRINCIPAL
###############################################################################

main() {
    clear
    print_header "INSTALADOR AUTOMÁTICO - GESTIÓN DE TALLER"
    
    echo ""
    echo "Este script instalará:"
    echo "  • MongoDB"
    echo "  • Python 3 + FastAPI"
    echo "  • Node.js + React"
    echo "  • Apache2"
    echo "  • Aplicación de Gestión de Taller"
    echo ""
    echo -e "${YELLOW}El proceso tomará entre 10-20 minutos dependiendo de tu conexión.${NC}"
    echo ""
    
    read -p "¿Deseas continuar? (s/n): " CONTINUE
    if [ "$CONTINUE" != "s" ] && [ "$CONTINUE" != "S" ]; then
        echo "Instalación cancelada."
        exit 0
    fi
    
    # Crear log file
    touch "$LOG_FILE"
    log "=== Iniciando instalación ==="
    
    # Verificaciones iniciales
    check_root
    check_ubuntu
    
    # Instalaciones
    install_dependencies
    install_python
    install_nodejs
    install_mongodb
    install_apache
    
    # Configuración de la aplicación
    setup_application_structure
    setup_backend
    setup_database
    setup_frontend
    
    # Configuración de servicios
    setup_systemd_service
    setup_apache_vhost
    setup_permissions
    
    # Seguridad y extras
    setup_firewall
    setup_ssl
    create_maintenance_scripts
    
    # Verificación final
    verify_installation
    
    # Limpiar archivos temporales
    rm -f /tmp/taller_domain.txt
    
    log "=== Instalación completada ==="
    
    # Mostrar información final
    print_final_info
}

###############################################################################
# EJECUTAR
###############################################################################

main "$@"
