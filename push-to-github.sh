#!/bin/bash

###############################################################################
# Script Helper - Subir Proyecto a GitHub
# Este script te ayuda a subir tu proyecto a GitHub fácilmente
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

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

clear
print_header "Helper - Subir Proyecto a GitHub"

# Verificar que estamos en el directorio correcto
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    print_error "Debes ejecutar este script en el directorio que contiene 'backend' y 'frontend'"
    exit 1
fi

print_success "Estructura de proyecto encontrada"

# Verificar si git está instalado
if ! command -v git &> /dev/null; then
    print_error "Git no está instalado"
    print_info "Instálalo con: sudo apt install git"
    exit 1
fi

print_success "Git está instalado"

# Verificar si ya es un repositorio git
if [ -d ".git" ]; then
    print_warning "Este directorio ya es un repositorio git"
    read -p "¿Deseas continuar de todas formas? (s/n): " CONTINUE
    if [ "$CONTINUE" != "s" ]; then
        exit 0
    fi
fi

echo ""
print_header "Configuración de GitHub"

# Pedir información del usuario
echo -e "${YELLOW}Antes de continuar, asegúrate de haber creado un repositorio en GitHub:${NC}"
echo "1. Ve a https://github.com"
echo "2. Haz clic en el botón '+' > 'New repository'"
echo "3. Dale un nombre (ej: taller-app)"
echo "4. NO inicialices con README, .gitignore, o licencia"
echo "5. Copia la URL del repositorio"
echo ""
read -p "¿Ya creaste el repositorio en GitHub? (s/n): " REPO_CREATED

if [ "$REPO_CREATED" != "s" ]; then
    print_info "Crea el repositorio en GitHub primero y vuelve a ejecutar este script"
    exit 0
fi

echo ""
read -p "Ingresa la URL de tu repositorio (ej: https://github.com/usuario/taller-app.git): " REPO_URL

if [ -z "$REPO_URL" ]; then
    print_error "Debes proporcionar una URL de repositorio"
    exit 1
fi

# Pedir nombre y email para git
read -p "Ingresa tu nombre para Git: " GIT_NAME
read -p "Ingresa tu email para Git: " GIT_EMAIL

if [ -z "$GIT_NAME" ] || [ -z "$GIT_EMAIL" ]; then
    print_error "Nombre y email son requeridos"
    exit 1
fi

# Configurar git
print_header "Configurando Git"
git config --global user.name "$GIT_NAME"
git config --global user.email "$GIT_EMAIL"
print_success "Git configurado"

# Crear .gitignore si no existe
if [ ! -f ".gitignore" ]; then
    print_info "Creando .gitignore..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
*.egg-info/
.pytest_cache/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnp/
.pnp.js

# Production
/frontend/build
/backend/dist

# Environment variables (NO subir las .env de producción)
# Descomenta si quieres incluir .env en el repo:
# backend/.env
# frontend/.env

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
logs/

# Database
*.db
*.sqlite
EOF
    print_success ".gitignore creado"
fi

# Inicializar repositorio si no existe
if [ ! -d ".git" ]; then
    print_info "Inicializando repositorio git..."
    git init
    print_success "Repositorio inicializado"
fi

# Agregar archivos
print_header "Preparando Archivos"
git add .
print_success "Archivos agregados"

# Hacer commit
print_info "Creando commit..."
git commit -m "Primera versión - Aplicación de Gestión de Taller"
print_success "Commit creado"

# Agregar remote
print_info "Configurando repositorio remoto..."
git remote remove origin 2>/dev/null
git remote add origin "$REPO_URL"
print_success "Repositorio remoto configurado"

# Push
print_header "Subiendo a GitHub"
print_warning "Si el repositorio es privado, se te pedirá tu usuario y contraseña de GitHub"
print_info "Nota: GitHub ahora requiere Personal Access Token en lugar de contraseña"
print_info "Puedes crear uno en: https://github.com/settings/tokens"
echo ""

# Determinar rama principal
MAIN_BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || echo "main")
if [ "$MAIN_BRANCH" = "master" ]; then
    print_info "Renombrando rama 'master' a 'main'..."
    git branch -M main
    MAIN_BRANCH="main"
fi

print_info "Subiendo archivos..."
if git push -u origin "$MAIN_BRANCH"; then
    print_success "¡Código subido exitosamente a GitHub!"
else
    print_error "Hubo un problema al subir el código"
    print_info "Verifica tu usuario/token de GitHub"
    print_info "Si es un repositorio privado, asegúrate de tener permisos de escritura"
    exit 1
fi

# Crear README si no existe
if [ ! -f "README.md" ]; then
    print_info "Creando README.md..."
    cat > README.md << 'EOF'
# Aplicación de Gestión de Taller

Sistema completo para gestión de equipos en taller.

## Características

- 📝 Entrada de equipos al taller
- 🔧 Revisión y calibración de equipos
- 📦 Salida y entrega de equipos
- 📊 Resumen e historial de equipos

## Instalación Automática

```bash
# Descarga el instalador
wget https://raw.githubusercontent.com/USUARIO/REPO/main/install-github.sh

# Dar permisos de ejecución
chmod +x install-github.sh

# Ejecutar
sudo bash install-github.sh
```

## Acceso

Una vez instalado, accede a:
```
http://192.168.1.7/AppTaller
```

**Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: `admin123`

## Tecnologías

- Backend: FastAPI + Python 3
- Frontend: React + TailwindCSS + Shadcn UI
- Base de Datos: MongoDB

## Documentación

Ver [GUIA_DESPLIEGUE.md](GUIA_DESPLIEGUE.md) para instalación manual completa.

Ver [README_GITHUB.md](README_GITHUB.md) para instalación automática desde GitHub.
EOF
    
    git add README.md
    git commit -m "Agregar README"
    git push
    print_success "README.md creado y subido"
fi

print_header "¡COMPLETADO!"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    PROYECTO SUBIDO A GITHUB                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  🌐 Repositorio: ${BLUE}$REPO_URL${NC}"
echo -e "  📁 Rama: ${BLUE}$MAIN_BRANCH${NC}"
echo ""
echo -e "${YELLOW}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║                    PRÓXIMOS PASOS                              ║${NC}"
echo -e "${YELLOW}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  1️⃣  Verifica que el código esté en GitHub:"
echo -e "     ${BLUE}${REPO_URL%.git}${NC}"
echo ""
echo -e "  2️⃣  Para instalar en un servidor Ubuntu, ejecuta:"
echo -e "     ${GREEN}sudo bash install-github.sh${NC}"
echo ""
echo -e "  3️⃣  Cuando el instalador te pregunte, ingresa:"
echo -e "     ${BLUE}$REPO_URL${NC}"
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    COMANDOS ÚTILES                             ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  📤 Subir cambios futuros:"
echo -e "     ${GREEN}git add .${NC}"
echo -e "     ${GREEN}git commit -m \"Descripción de cambios\"${NC}"
echo -e "     ${GREEN}git push${NC}"
echo ""
echo -e "  🔄 Actualizar desde servidor:"
echo -e "     ${GREEN}git pull${NC}"
echo ""
echo -e "  👁️  Ver estado:"
echo -e "     ${GREEN}git status${NC}"
echo ""
echo -e "  📋 Ver historial:"
echo -e "     ${GREEN}git log --oneline${NC}"
echo ""

print_success "¡Todo listo! Tu proyecto está en GitHub 🚀"
echo ""
