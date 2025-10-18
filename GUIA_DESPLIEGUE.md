# Guía de Despliegue - Aplicación de Gestión de Taller
## Ubuntu Server + Apache2 + MongoDB

Esta guía te ayudará a instalar y configurar la aplicación en un servidor Ubuntu desde cero.

---

## 📋 REQUISITOS PREVIOS

- Servidor Ubuntu 20.04 o superior
- Acceso root o sudo
- Conexión a Internet
- Dominio (opcional, pero recomendado)

---

## 🚀 PARTE 1: INSTALACIÓN DE DEPENDENCIAS

### 1.1 Actualizar el Sistema

```bash
sudo apt update
sudo apt upgrade -y
```

### 1.2 Instalar Python 3.11+

```bash
# Instalar Python y pip
sudo apt install python3 python3-pip python3-venv -y

# Verificar versión
python3 --version  # Debe ser 3.8 o superior
```

### 1.3 Instalar Node.js y Yarn

```bash
# Instalar Node.js 18.x
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Instalar Yarn
npm install -g yarn

# Verificar versiones
node --version  # Debe ser v18.x o superior
yarn --version
```

### 1.4 Instalar MongoDB

```bash
# Importar clave pública de MongoDB
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor

# Agregar repositorio MongoDB
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
   sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Actualizar e instalar
sudo apt update
sudo apt install mongodb-org -y

# Iniciar y habilitar MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Verificar que MongoDB está corriendo
sudo systemctl status mongod
```

### 1.5 Instalar Apache2

```bash
# Instalar Apache2
sudo apt install apache2 -y

# Habilitar módulos necesarios
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod rewrite
sudo a2enmod ssl
sudo a2enmod headers

# Reiniciar Apache
sudo systemctl restart apache2
sudo systemctl enable apache2
```

---

## 📦 PARTE 2: PREPARAR LA APLICACIÓN

### 2.1 Crear Directorios y Copiar Archivos

```bash
# Crear directorio para la aplicación
sudo mkdir -p /var/www/taller-app
cd /var/www/taller-app

# Crear estructura de carpetas
sudo mkdir -p backend frontend
```

**Ahora debes copiar tus archivos:**
- Copia todo el contenido de `/app/backend/` a `/var/www/taller-app/backend/`
- Copia todo el contenido de `/app/frontend/` a `/var/www/taller-app/frontend/`

Puedes usar SCP, SFTP, o cualquier método de transferencia de archivos:

```bash
# Desde tu máquina local (ejemplo con SCP):
scp -r /ruta/local/backend/* usuario@tu-servidor:/var/www/taller-app/backend/
scp -r /ruta/local/frontend/* usuario@tu-servidor:/var/www/taller-app/frontend/
```

### 2.2 Configurar el Backend

```bash
cd /var/www/taller-app/backend

# Crear entorno virtual de Python
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env de producción
sudo nano .env
```

**Contenido del archivo `.env`:**

```bash
MONGO_URL=mongodb://localhost:27017
DB_NAME=taller_production
CORS_ORIGINS=http://tu-dominio.com,https://tu-dominio.com
JWT_SECRET=cambia-este-secreto-por-uno-muy-seguro-y-largo-12345678
```

**Importante:** Cambia `tu-dominio.com` por tu dominio real y genera un JWT_SECRET seguro.

### 2.3 Configurar la Base de Datos

```bash
# Conectar a MongoDB
mongosh

# Dentro de MongoDB shell:
use taller_production

# Crear usuario administrador para la base de datos (RECOMENDADO)
db.createUser({
  user: "taller_admin",
  pwd: "tu_password_seguro",
  roles: [{ role: "readWrite", db: "taller_production" }]
})

# Salir de MongoDB
exit
```

Si creaste un usuario, actualiza el `.env`:

```bash
MONGO_URL=mongodb://taller_admin:tu_password_seguro@localhost:27017
```

### 2.4 Poblar Datos Iniciales

```bash
cd /var/www/taller-app/backend

# Activar entorno virtual si no está activo
source venv/bin/activate

# Crear script para poblar modelos iniciales
python3 << 'EOF'
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
        print(f'✓ {len(models)} modelos insertados')
    else:
        print(f'✓ Ya existen {count} modelos')
    
    client.close()

asyncio.run(seed_data())
EOF
```

### 2.5 Construir el Frontend

```bash
cd /var/www/taller-app/frontend

# Instalar dependencias
yarn install

# Crear archivo .env de producción
sudo nano .env
```

**Contenido del archivo `.env` del frontend:**

```bash
REACT_APP_BACKEND_URL=http://tu-dominio.com
```

**Construir la aplicación para producción:**

```bash
# Build de producción
yarn build

# Esto creará una carpeta 'build' con los archivos estáticos
```

---

## ⚙️ PARTE 3: CONFIGURAR SERVICIOS

### 3.1 Crear Servicio Systemd para el Backend

```bash
sudo nano /etc/systemd/system/taller-backend.service
```

**Contenido del archivo:**

```ini
[Unit]
Description=Taller Backend FastAPI
After=network.target mongod.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/taller-app/backend
Environment="PATH=/var/www/taller-app/backend/venv/bin"
ExecStart=/var/www/taller-app/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --workers 4

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Activar y iniciar el servicio:**

```bash
# Recargar systemd
sudo systemctl daemon-reload

# Habilitar el servicio
sudo systemctl enable taller-backend

# Iniciar el servicio
sudo systemctl start taller-backend

# Verificar estado
sudo systemctl status taller-backend
```

---

## 🌐 PARTE 4: CONFIGURAR APACHE2

### 4.1 Crear VirtualHost para la Aplicación

```bash
sudo nano /etc/apache2/sites-available/taller-app.conf
```

**Contenido del archivo:**

```apache
<VirtualHost *:80>
    ServerName tu-dominio.com
    ServerAlias www.tu-dominio.com
    
    # Logs
    ErrorLog ${APACHE_LOG_DIR}/taller-error.log
    CustomLog ${APACHE_LOG_DIR}/taller-access.log combined
    
    # Frontend - Archivos estáticos de React
    DocumentRoot /var/www/taller-app/frontend/build
    
    <Directory /var/www/taller-app/frontend/build>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
        
        # React Router - todas las rutas van a index.html
        RewriteEngine On
        RewriteBase /
        RewriteRule ^index\.html$ - [L]
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteRule . /index.html [L]
    </Directory>
    
    # Backend API - Proxy reverso a FastAPI
    ProxyPreserveHost On
    ProxyRequests Off
    
    <Location /api>
        ProxyPass http://localhost:8001/api
        ProxyPassReverse http://localhost:8001/api
    </Location>
</VirtualHost>
```

**Activar el sitio:**

```bash
# Deshabilitar sitio por defecto
sudo a2dissite 000-default.conf

# Habilitar nuestro sitio
sudo a2ensite taller-app.conf

# Verificar configuración
sudo apache2ctl configtest

# Reiniciar Apache
sudo systemctl restart apache2
```

### 4.2 Configurar SSL/HTTPS (Recomendado)

**Instalar Certbot para certificados gratuitos de Let's Encrypt:**

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-apache -y

# Obtener certificado SSL (reemplaza tu-dominio.com)
sudo certbot --apache -d tu-dominio.com -d www.tu-dominio.com

# Certbot configurará automáticamente HTTPS
```

Certbot creará automáticamente una configuración SSL y programará renovaciones automáticas.

**Actualizar el `.env` del frontend para usar HTTPS:**

```bash
cd /var/www/taller-app/frontend
sudo nano .env
```

Cambiar a:

```bash
REACT_APP_BACKEND_URL=https://tu-dominio.com
```

**Reconstruir el frontend:**

```bash
yarn build
sudo systemctl restart apache2
```

---

## 🔒 PARTE 5: SEGURIDAD Y PERMISOS

### 5.1 Configurar Permisos de Archivos

```bash
# Cambiar propietario de archivos
sudo chown -R www-data:www-data /var/www/taller-app

# Permisos correctos
sudo chmod -R 755 /var/www/taller-app
sudo chmod 600 /var/www/taller-app/backend/.env
sudo chmod 600 /var/www/taller-app/frontend/.env
```

### 5.2 Configurar Firewall

```bash
# Habilitar UFW
sudo ufw enable

# Permitir SSH
sudo ufw allow ssh

# Permitir HTTP y HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Verificar reglas
sudo ufw status
```

### 5.3 Seguridad de MongoDB

```bash
# Editar configuración de MongoDB
sudo nano /etc/mongod.conf
```

**Habilitar autenticación (descomenta o agrega):**

```yaml
security:
  authorization: enabled

net:
  bindIp: 127.0.0.1
```

**Reiniciar MongoDB:**

```bash
sudo systemctl restart mongod
```

---

## 📊 PARTE 6: VERIFICACIÓN Y PRUEBAS

### 6.1 Verificar que Todo Está Corriendo

```bash
# Verificar MongoDB
sudo systemctl status mongod

# Verificar Backend
sudo systemctl status taller-backend

# Ver logs del backend si hay errores
sudo journalctl -u taller-backend -f

# Verificar Apache2
sudo systemctl status apache2

# Ver logs de Apache
sudo tail -f /var/log/apache2/taller-error.log
```

### 6.2 Probar la Aplicación

1. Abre tu navegador y ve a: `http://tu-dominio.com`
2. Deberías ver la página de login
3. Registra un usuario nuevo
4. Prueba todas las funcionalidades

### 6.3 Crear Usuario Administrador

```bash
cd /var/www/taller-app/backend
source venv/bin/activate

python3 << 'EOF'
import asyncio
import sys
sys.path.insert(0, '/var/www/taller-app/backend')
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['taller_production']
    
    admin_user = {
        'id': 'admin-001',
        'username': 'admin',
        'full_name': 'Administrador',
        'hashed_password': pwd_context.hash('admin123'),
        'created_at': '2025-01-01T00:00:00'
    }
    
    existing = await db.users.find_one({'username': 'admin'})
    if not existing:
        await db.users.insert_one(admin_user)
        print('✓ Usuario admin creado (usuario: admin, contraseña: admin123)')
    else:
        print('✓ Usuario admin ya existe')
    
    client.close()

asyncio.run(create_admin())
EOF
```

---

## 🔧 PARTE 7: MANTENIMIENTO

### 7.1 Comandos Útiles

```bash
# Reiniciar servicios
sudo systemctl restart taller-backend
sudo systemctl restart apache2
sudo systemctl restart mongod

# Ver logs en tiempo real
sudo journalctl -u taller-backend -f
sudo tail -f /var/log/apache2/taller-error.log

# Detener servicios
sudo systemctl stop taller-backend
sudo systemctl stop apache2

# Actualizar aplicación después de cambios
cd /var/www/taller-app/backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart taller-backend

cd /var/www/taller-app/frontend
yarn install
yarn build
sudo systemctl restart apache2
```

### 7.2 Backup de la Base de Datos

```bash
# Crear directorio para backups
sudo mkdir -p /var/backups/taller-db

# Backup manual
sudo mongodump --db taller_production --out /var/backups/taller-db/backup-$(date +%Y%m%d)

# Automatizar backup diario (crear cron job)
sudo crontab -e

# Agregar esta línea para backup diario a las 2 AM:
0 2 * * * mongodump --db taller_production --out /var/backups/taller-db/backup-$(date +\%Y\%m\%d)
```

### 7.3 Restaurar Base de Datos

```bash
# Restaurar desde backup
sudo mongorestore --db taller_production /var/backups/taller-db/backup-YYYYMMDD/taller_production
```

---

## ❗ SOLUCIÓN DE PROBLEMAS

### Problema: El backend no inicia

```bash
# Ver logs detallados
sudo journalctl -u taller-backend -n 50

# Verificar que el puerto 8001 no esté en uso
sudo netstat -tulpn | grep 8001

# Probar manualmente
cd /var/www/taller-app/backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001
```

### Problema: MongoDB no conecta

```bash
# Verificar que MongoDB está corriendo
sudo systemctl status mongod

# Verificar logs de MongoDB
sudo tail -f /var/log/mongodb/mongod.log

# Probar conexión
mongosh
```

### Problema: Apache no sirve la aplicación

```bash
# Verificar sintaxis de configuración
sudo apache2ctl configtest

# Ver logs de error
sudo tail -f /var/log/apache2/error.log

# Verificar que los módulos están habilitados
sudo apache2ctl -M | grep proxy
```

### Problema: CORS errors

Edita `/var/www/taller-app/backend/.env` y asegúrate de que CORS_ORIGINS incluya tu dominio:

```bash
CORS_ORIGINS=http://tu-dominio.com,https://tu-dominio.com,http://localhost:3000
```

Luego reinicia el backend:

```bash
sudo systemctl restart taller-backend
```

---

## 📝 NOTAS IMPORTANTES

1. **Cambia todas las contraseñas por defecto** antes de ir a producción
2. **Configura HTTPS** con Certbot - es gratuito y fácil
3. **Haz backups regulares** de la base de datos
4. **Monitorea los logs** regularmente para detectar problemas
5. **Actualiza el sistema** regularmente: `sudo apt update && sudo apt upgrade`

---

## 🎉 ¡LISTO!

Tu aplicación de Gestión de Taller debería estar funcionando en:
- **Frontend:** `http://tu-dominio.com` (o `https://` si configuraste SSL)
- **Backend API:** `http://tu-dominio.com/api`

**Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: `admin123`

**¡IMPORTANTE!** Cambia esta contraseña después del primer login.

---

## 📞 SOPORTE

Si encuentras problemas:
1. Revisa los logs con los comandos de la sección 7.1
2. Verifica que todos los servicios estén corriendo
3. Consulta la sección de Solución de Problemas

¡Buena suerte con tu aplicación! 🚀
