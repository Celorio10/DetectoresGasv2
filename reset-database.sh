#!/bin/bash

###############################################################################
# Script de Limpieza de Base de Datos - Gestión de Taller
# Vacía la base de datos para empezar de cero
#
# Uso: sudo bash reset-database.sh
###############################################################################

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Variables
MONGO_URL="mongodb://localhost:27017"
DB_NAME="taller_production"
BACKUP_DIR="/var/backups/taller-db"
BACKEND_DIR="/var/www/taller-app/backend"

###############################################################################
# FUNCIONES
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

check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "Este script debe ejecutarse como root (sudo)"
        exit 1
    fi
}

check_mongodb() {
    if ! systemctl is-active --quiet mongod; then
        print_error "MongoDB no está corriendo"
        print_info "Inicia MongoDB con: sudo systemctl start mongod"
        exit 1
    fi
    print_success "MongoDB está corriendo"
}

create_backup() {
    print_header "Creando Backup de Seguridad"
    
    DATE=$(date +%Y%m%d_%H%M%S)
    mkdir -p "$BACKUP_DIR"
    
    print_info "Creando backup en: $BACKUP_DIR/backup-before-reset-$DATE"
    
    if mongodump --db "$DB_NAME" --out "$BACKUP_DIR/backup-before-reset-$DATE" > /dev/null 2>&1; then
        print_success "Backup creado correctamente"
        echo "$BACKUP_DIR/backup-before-reset-$DATE" > /tmp/last_backup.txt
    else
        print_warning "No se pudo crear backup (la base de datos podría estar vacía)"
    fi
}

reset_complete() {
    print_header "Vaciando Base de Datos Completamente"
    
    print_warning "Esto eliminará TODOS los datos incluyendo:"
    echo "  • Usuarios"
    echo "  • Equipos"
    echo "  • Marcas"
    echo "  • Modelos"
    echo "  • Clientes"
    echo "  • Técnicos"
    echo ""
    
    mongosh "$MONGO_URL/$DB_NAME" --quiet --eval "
        db.users.deleteMany({});
        db.equipment.deleteMany({});
        db.brands.deleteMany({});
        db.models.deleteMany({});
        db.clients.deleteMany({});
        db.technicians.deleteMany({});
        print('Base de datos vaciada completamente');
    " > /dev/null 2>&1
    
    print_success "Base de datos vaciada completamente"
}

reset_keep_config() {
    print_header "Vaciando Datos de Trabajo"
    
    print_info "Se eliminarán:"
    echo "  • Equipos"
    echo "  • Clientes (excepto de prueba)"
    echo "  • Técnicos (excepto admin)"
    echo ""
    print_info "Se mantendrán:"
    echo "  • Usuario admin"
    echo "  • Modelos iniciales (Altair, etc.)"
    echo "  • Marcas"
    echo ""
    
    mongosh "$MONGO_URL/$DB_NAME" --quiet --eval "
        db.equipment.deleteMany({});
        db.clients.deleteMany({});
        db.technicians.deleteMany({});
        print('Datos de trabajo eliminados');
    " > /dev/null 2>&1
    
    print_success "Datos de trabajo eliminados"
}

reset_only_equipment() {
    print_header "Vaciando Solo Equipos"
    
    print_info "Se eliminarán:"
    echo "  • Todos los equipos registrados"
    echo ""
    print_info "Se mantendrán:"
    echo "  • Usuarios"
    echo "  • Modelos"
    echo "  • Marcas"
    echo "  • Clientes"
    echo "  • Técnicos"
    echo ""
    
    mongosh "$MONGO_URL/$DB_NAME" --quiet --eval "
        db.equipment.deleteMany({});
        print('Equipos eliminados');
    " > /dev/null 2>&1
    
    print_success "Equipos eliminados"
}

reinitialize_database() {
    print_header "Reinicializando Base de Datos"
    
    # Verificar que el directorio del backend existe
    if [ ! -d "$BACKEND_DIR" ]; then
        print_error "Directorio del backend no encontrado: $BACKEND_DIR"
        return
    fi
    
    cd "$BACKEND_DIR"
    
    # Activar entorno virtual
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        print_error "Entorno virtual no encontrado"
        return
    fi
    
    print_info "Insertando modelos iniciales..."
    python3 << 'PYEOF'
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
    
    print_info "Creando usuario admin..."
    python3 << 'PYEOF'
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
    
    print_success "Base de datos reinicializada"
}

show_database_stats() {
    print_header "Estadísticas de Base de Datos"
    
    mongosh "$MONGO_URL/$DB_NAME" --quiet --eval "
        const users = db.users.countDocuments();
        const equipment = db.equipment.countDocuments();
        const brands = db.brands.countDocuments();
        const models = db.models.countDocuments();
        const clients = db.clients.countDocuments();
        const technicians = db.technicians.countDocuments();
        
        print('Usuarios:        ' + users);
        print('Equipos:         ' + equipment);
        print('Marcas:          ' + brands);
        print('Modelos:         ' + models);
        print('Clientes:        ' + clients);
        print('Técnicos:        ' + technicians);
    " 2>/dev/null || echo "No se pueden obtener estadísticas"
}

restore_from_backup() {
    print_header "Restaurar desde Backup"
    
    if [ ! -d "$BACKUP_DIR" ] || [ -z "$(ls -A $BACKUP_DIR 2>/dev/null)" ]; then
        print_error "No hay backups disponibles"
        return
    fi
    
    echo "Backups disponibles:"
    echo ""
    ls -lht "$BACKUP_DIR" | grep "^d" | head -10
    echo ""
    
    read -p "Ingresa el nombre del backup a restaurar (o 'cancelar'): " BACKUP_NAME
    
    if [ "$BACKUP_NAME" = "cancelar" ] || [ -z "$BACKUP_NAME" ]; then
        print_info "Restauración cancelada"
        return
    fi
    
    BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME/$DB_NAME"
    
    if [ ! -d "$BACKUP_PATH" ]; then
        print_error "Backup no encontrado: $BACKUP_PATH"
        return
    fi
    
    print_warning "Esto sobrescribirá todos los datos actuales"
    read -p "¿Estás seguro? (escribe 'SI' en mayúsculas): " CONFIRM
    
    if [ "$CONFIRM" != "SI" ]; then
        print_info "Restauración cancelada"
        return
    fi
    
    print_info "Restaurando desde backup..."
    if mongorestore --db "$DB_NAME" --drop "$BACKUP_PATH" > /dev/null 2>&1; then
        print_success "Base de datos restaurada correctamente"
    else
        print_error "Error al restaurar backup"
    fi
}

###############################################################################
# MENÚ PRINCIPAL
###############################################################################

show_menu() {
    clear
    print_header "LIMPIEZA DE BASE DE DATOS - GESTIÓN DE TALLER"
    
    echo ""
    show_database_stats
    echo ""
    
    echo -e "${YELLOW}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║                      OPCIONES DISPONIBLES                      ║${NC}"
    echo -e "${YELLOW}╚════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "  1) Vaciar TODO (Reset completo)"
    echo "     └─ Elimina usuarios, equipos, marcas, modelos, clientes, técnicos"
    echo ""
    echo "  2) Vaciar datos de trabajo (Mantener configuración)"
    echo "     └─ Elimina equipos, clientes, técnicos"
    echo "     └─ Mantiene usuario admin, modelos, marcas"
    echo ""
    echo "  3) Vaciar solo equipos"
    echo "     └─ Elimina todos los equipos"
    echo "     └─ Mantiene todo lo demás"
    echo ""
    echo "  4) Reset completo + Reinicializar"
    echo "     └─ Vacía TODO y vuelve a crear modelos y usuario admin"
    echo ""
    echo "  5) Restaurar desde backup"
    echo "     └─ Restaura la base de datos desde un backup anterior"
    echo ""
    echo "  6) Ver estadísticas y salir"
    echo ""
    echo "  0) Cancelar y salir"
    echo ""
    echo -e "${YELLOW}════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

###############################################################################
# FUNCIÓN PRINCIPAL
###############################################################################

main() {
    check_root
    check_mongodb
    
    show_menu
    
    read -p "Selecciona una opción [0-6]: " OPTION
    
    case $OPTION in
        1)
            echo ""
            print_warning "¡ATENCIÓN! Vas a vaciar TODA la base de datos"
            print_warning "Esto incluye usuarios, equipos, configuración, TODO"
            echo ""
            read -p "¿Estás completamente seguro? (escribe 'SI' en mayúsculas): " CONFIRM
            
            if [ "$CONFIRM" != "SI" ]; then
                print_info "Operación cancelada"
                exit 0
            fi
            
            create_backup
            reset_complete
            
            echo ""
            read -p "¿Deseas reinicializar (crear modelos y admin)? (s/n): " REINIT
            if [ "$REINIT" = "s" ] || [ "$REINIT" = "S" ]; then
                reinitialize_database
            fi
            ;;
            
        2)
            echo ""
            print_warning "Vas a vaciar los datos de trabajo"
            echo ""
            read -p "¿Continuar? (s/n): " CONFIRM
            
            if [ "$CONFIRM" != "s" ] && [ "$CONFIRM" != "S" ]; then
                print_info "Operación cancelada"
                exit 0
            fi
            
            create_backup
            reset_keep_config
            ;;
            
        3)
            echo ""
            print_warning "Vas a eliminar TODOS los equipos"
            echo ""
            read -p "¿Continuar? (s/n): " CONFIRM
            
            if [ "$CONFIRM" != "s" ] && [ "$CONFIRM" != "S" ]; then
                print_info "Operación cancelada"
                exit 0
            fi
            
            create_backup
            reset_only_equipment
            ;;
            
        4)
            echo ""
            print_warning "¡ATENCIÓN! Reset completo + reinicialización"
            echo ""
            read -p "¿Estás seguro? (escribe 'SI' en mayúsculas): " CONFIRM
            
            if [ "$CONFIRM" != "SI" ]; then
                print_info "Operación cancelada"
                exit 0
            fi
            
            create_backup
            reset_complete
            reinitialize_database
            ;;
            
        5)
            restore_from_backup
            ;;
            
        6)
            show_database_stats
            exit 0
            ;;
            
        0)
            print_info "Operación cancelada"
            exit 0
            ;;
            
        *)
            print_error "Opción inválida"
            exit 1
            ;;
    esac
    
    echo ""
    print_header "RESUMEN FINAL"
    show_database_stats
    
    if [ -f /tmp/last_backup.txt ]; then
        LAST_BACKUP=$(cat /tmp/last_backup.txt)
        echo ""
        print_success "Backup disponible en: $LAST_BACKUP"
        rm /tmp/last_backup.txt
    fi
    
    echo ""
    print_success "Operación completada exitosamente"
    echo ""
    print_info "Credenciales por defecto:"
    echo "  Usuario: admin"
    echo "  Contraseña: admin123"
    echo ""
}

###############################################################################
# EJECUTAR
###############################################################################

main "$@"
