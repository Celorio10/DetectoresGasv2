#!/bin/bash

###############################################################################
# Script para Actualizar GitHub
# Para el repositorio: https://github.com/Celorio10/DetectoresGas
###############################################################################

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

clear
print_header "Actualizar GitHub - DetectoresGas"

cd /app

echo ""
print_info "Repositorio: https://github.com/Celorio10/DetectoresGas"
echo ""

# Verificar git
if ! command -v git &> /dev/null; then
    print_error "Git no está instalado"
    exit 1
fi

# Ver estado
print_info "Estado actual del repositorio:"
echo ""
git status
echo ""

# Ver últimos commits
print_info "Últimos commits:"
echo ""
git log --oneline -5
echo ""

# Verificar remote
print_info "Verificando configuración remota..."
git remote -v

# Configurar remote si no existe
if ! git remote | grep -q origin; then
    print_info "Configurando remote..."
    git remote add origin https://github.com/Celorio10/DetectoresGas.git
    print_success "Remote configurado"
fi

echo ""
print_header "Opciones para Subir a GitHub"
echo ""
echo "1️⃣  Usar Personal Access Token (Recomendado)"
echo "    - Más seguro"
echo "    - No expone tu contraseña"
echo ""
echo "2️⃣  Usar usuario y contraseña"
echo "    - Más simple"
echo "    - GitHub puede requerir token"
echo ""
echo "3️⃣  Configurar SSH (Avanzado)"
echo "    - Más seguro y conveniente"
echo "    - Requiere configuración"
echo ""
echo "4️⃣  Hacerlo manualmente desde tu máquina"
echo ""

read -p "Selecciona una opción [1-4]: " OPTION

case $OPTION in
    1)
        print_header "Opción 1: Personal Access Token"
        echo ""
        echo "Pasos para crear un Personal Access Token:"
        echo ""
        echo "1. Ve a: https://github.com/settings/tokens"
        echo "2. Clic en 'Generate new token' > 'Generate new token (classic)'"
        echo "3. Nombre: 'DetectoresGas Deploy'"
        echo "4. Expiration: 90 days (o lo que prefieras)"
        echo "5. Selecciona scope: ✅ repo (todos los sub-items)"
        echo "6. Clic en 'Generate token'"
        echo "7. COPIA el token (empieza con 'ghp_...')"
        echo ""
        read -p "¿Ya tienes tu token? (s/n): " HAS_TOKEN
        
        if [ "$HAS_TOKEN" = "s" ]; then
            echo ""
            read -sp "Pega tu token aquí: " TOKEN
            echo ""
            
            print_info "Intentando push..."
            if git push https://Celorio10:$TOKEN@github.com/Celorio10/DetectoresGas.git main; then
                print_success "¡Código subido exitosamente a GitHub!"
            else
                print_error "Error al subir código"
                exit 1
            fi
        else
            print_info "Crea tu token y vuelve a ejecutar este script"
            exit 0
        fi
        ;;
        
    2)
        print_header "Opción 2: Usuario y Contraseña"
        echo ""
        print_info "Usuario de GitHub: Celorio10"
        read -sp "Contraseña o Personal Access Token: " PASSWORD
        echo ""
        
        print_info "Intentando push..."
        if git push https://Celorio10:$PASSWORD@github.com/Celorio10/DetectoresGas.git main; then
            print_success "¡Código subido exitosamente a GitHub!"
        else
            print_error "Error al subir código"
            print_info "GitHub ahora requiere Personal Access Token en lugar de contraseña"
            print_info "Usa la Opción 1"
            exit 1
        fi
        ;;
        
    3)
        print_header "Opción 3: Configurar SSH"
        echo ""
        print_info "Pasos para configurar SSH:"
        echo ""
        echo "1. Generar clave SSH (si no tienes):"
        echo "   ssh-keygen -t ed25519 -C 'tu-email@ejemplo.com'"
        echo ""
        echo "2. Ver tu clave pública:"
        echo "   cat ~/.ssh/id_ed25519.pub"
        echo ""
        echo "3. Agregar a GitHub:"
        echo "   - Ve a: https://github.com/settings/keys"
        echo "   - Clic en 'New SSH key'"
        echo "   - Pega tu clave pública"
        echo ""
        echo "4. Cambiar remote a SSH:"
        echo "   git remote set-url origin git@github.com:Celorio10/DetectoresGas.git"
        echo ""
        echo "5. Hacer push:"
        echo "   git push origin main"
        echo ""
        ;;
        
    4)
        print_header "Opción 4: Hacerlo Manualmente"
        echo ""
        print_info "En tu máquina local:"
        echo ""
        echo "1. Clona o actualiza el repositorio:"
        echo "   git clone https://github.com/Celorio10/DetectoresGas.git"
        echo "   cd DetectoresGas"
        echo ""
        echo "2. Copia los archivos actualizados desde este servidor"
        echo ""
        echo "3. Agrega y commitea los cambios:"
        echo "   git add ."
        echo "   git commit -m 'Actualizar con tabla de equipos pendientes'"
        echo ""
        echo "4. Sube a GitHub:"
        echo "   git push origin main"
        echo ""
        print_info "Archivos que debes actualizar:"
        echo "  - backend/server.py"
        echo "  - frontend/src/pages/EquipmentReview.js"
        echo ""
        ;;
        
    *)
        print_error "Opción inválida"
        exit 1
        ;;
esac

echo ""
print_header "Información Importante"
echo ""
print_info "Cambios que se subirán:"
echo "  ✅ Nuevo endpoint: /api/equipment/pending"
echo "  ✅ Tabla de equipos pendientes en Revisión"
echo "  ✅ Función de selección directa de equipos"
echo "  ✅ Scripts de instalación actualizados"
echo ""
print_success "Una vez subido a GitHub, ejecuta en tu servidor:"
echo "  ${GREEN}sudo bash install-github.sh${NC}"
echo ""
