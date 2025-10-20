# Requerimientos Técnicos - Sistema de Gestión de Taller

## Información del Proyecto

**Aplicación:** Sistema de Gestión de Taller de Equipos  
**Repositorio:** https://github.com/Celorio10/DetectoresGas  
**Tipo:** Aplicación Web Full-Stack  
**Stack:** FastAPI (Python) + React + MongoDB

---

## 📋 Requerimientos del Servidor

### Sistema Operativo

**Requerido:**
- Ubuntu Server 20.04 LTS o superior
- Ubuntu Desktop 20.04 LTS o superior

**Probado en:**
- ✅ Ubuntu 20.04 LTS (Focal Fossa)
- ✅ Ubuntu 22.04 LTS (Jammy Jellyfish)
- ✅ Ubuntu 24.04 LTS (Noble Numbat)

**NO compatible:**
- ❌ Debian
- ❌ CentOS / RedHat
- ❌ Windows Server
- ❌ Otras distribuciones Linux (no probadas)

---

### Hardware Mínimo

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| **CPU** | 2 cores | 4 cores |
| **RAM** | 2 GB | 4 GB o más |
| **Disco Duro** | 10 GB libres | 20 GB libres |
| **Red** | 100 Mbps | 1 Gbps |

**⚠️ IMPORTANTE - Compatibilidad CPU:**
- MongoDB 5.x o superior requiere soporte AVX en el procesador
- Si el CPU es antiguo (sin AVX), usar MongoDB 4.4 o 5.0 (versiones sin AVX)
- La aplicación es compatible con MongoDB 4.x, 5.x, 6.x y 7.x

**Verificar soporte AVX:**
```bash
grep avx /proc/cpuinfo
```
Si no devuelve nada, el CPU NO soporta AVX.

---

### Software Requerido

#### Base (se instala automáticamente)

| Software | Versión Mínima | Notas |
|----------|----------------|-------|
| **Python** | 3.8 | Preferible 3.10+ |
| **Node.js** | 16.x | Se instalará 18.x |
| **MongoDB** | 4.4 | Compatible hasta 7.x |
| **Apache2** | 2.4 | Proxy reverso |
| **Git** | 2.x | Para clonar repositorio |

#### Dependencias Python (automáticas)
- fastapi
- uvicorn
- motor (MongoDB async driver)
- pydantic
- python-jose[cryptography]
- passlib[bcrypt]
- python-multipart

#### Dependencias Node.js (automáticas)
- react
- react-router-dom
- axios
- tailwindcss
- shadcn/ui components

---

## 🌐 Requerimientos de Red

### Puertos Necesarios

| Puerto | Servicio | Uso | Acceso |
|--------|----------|-----|--------|
| **80** | HTTP (Apache) | Interfaz web | Red local o Internet |
| **443** | HTTPS (Opcional) | Interfaz web segura | Red local o Internet |
| **8001** | FastAPI Backend | API (interno) | Solo localhost |
| **27017** | MongoDB | Base de datos | Solo localhost |

### Firewall

```bash
# Permitir tráfico web
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow ssh
sudo ufw enable
```

### Configuración de Red

**Para acceso en red local:**
- IP estática recomendada (ej: 192.168.1.7)
- Sin restricciones de firewall entre clientes y servidor
- Router configurado para permitir tráfico interno

**Para acceso desde Internet (opcional):**
- IP pública estática o DNS dinámico
- Port forwarding en router (80, 443)
- Certificado SSL/TLS (Let's Encrypt gratuito)

---

## 💾 Requerimientos de Base de Datos

### MongoDB

**Versión:** 4.4, 5.0, 6.0 o 7.0

**Configuración:**
- Bind IP: 127.0.0.1 (solo localhost)
- Puerto: 27017 (predeterminado)
- Autenticación: Opcional (recomendada para producción)
- Storage Engine: WiredTiger (predeterminado)

**Espacio en disco:**
- Mínimo: 1 GB
- Recomendado: 5 GB o más (depende de volumen de datos)

---

## 🔒 Requerimientos de Seguridad

### Acceso SSH (para instalación remota)

```
Usuario con permisos sudo
Puerto SSH habilitado (22 por defecto)
```

### Credenciales Necesarias

**GitHub:**
- URL del repositorio: `https://github.com/Celorio10/DetectoresGas.git`
- Repositorio debe ser público, O
- Personal Access Token si es privado

**Aplicación (se crean automáticamente):**
- Usuario admin: `admin`
- Contraseña: `admin123` (CAMBIAR después del primer login)

---

## 📁 Estructura de Instalación

### Directorios Creados

```
/var/www/taller-app/          # Aplicación principal
├── backend/                   # Backend FastAPI
│   ├── venv/                 # Entorno virtual Python
│   ├── server.py
│   ├── requirements.txt
│   └── .env
└── frontend/                  # Frontend React
    └── build/                # Archivos estáticos

/var/backups/taller-db/        # Backups automáticos de MongoDB
/var/log/taller-install.log    # Log de instalación
/var/log/supervisor/           # Logs de servicios
```

### Servicios del Sistema

```
taller-backend.service         # Servicio systemd para FastAPI
mongod.service                 # MongoDB
apache2.service                # Servidor web
```

---

## 🚀 Proceso de Instalación

### Método Automatizado (Recomendado)

**Tiempo estimado:** 15-20 minutos

**Requisitos previos:**
1. Servidor Ubuntu limpio con acceso root/sudo
2. Conexión a Internet estable
3. MongoDB instalado (o se instalará automáticamente si CPU soporta AVX)

**Pasos:**

```bash
# 1. Descargar instalador
wget https://raw.githubusercontent.com/Celorio10/DetectoresGas/main/install-github.sh

# 2. Dar permisos
chmod +x install-github.sh

# 3. Ejecutar (como root)
sudo bash install-github.sh

# 4. Cuando pregunte, ingresar:
# https://github.com/Celorio10/DetectoresGas.git
```

**El script hace TODO automáticamente:**
- ✅ Verifica requisitos del sistema
- ✅ Instala software necesario
- ✅ Descarga código desde GitHub
- ✅ Configura backend y frontend
- ✅ Crea base de datos
- ✅ Configura servicios
- ✅ Configura Apache
- ✅ Configura firewall
- ✅ Crea backups automáticos

---

## 🌐 URLs de Acceso

### Red Local

```
http://192.168.1.7/AppTaller
```
*(Reemplazar 192.168.1.7 con la IP del servidor)*

### API Backend

```
http://192.168.1.7/AppTaller/api
```

### Documentación API (Swagger)

```
http://192.168.1.7:8001/docs
```
*(Solo accesible desde el servidor)*

---

## 🔧 Comandos de Administración

### Ver estado de servicios

```bash
sudo systemctl status taller-backend
sudo systemctl status apache2
sudo systemctl status mongod
```

### Reiniciar servicios

```bash
sudo systemctl restart taller-backend
sudo systemctl restart apache2
sudo systemctl restart mongod
```

### Ver logs

```bash
# Backend
sudo journalctl -u taller-backend -f

# Apache
sudo tail -f /var/log/apache2/taller-error.log

# MongoDB
sudo tail -f /var/log/mongodb/mongod.log

# Instalación
sudo cat /var/log/taller-install.log
```

### Backup manual

```bash
sudo /usr/local/bin/taller-backup.sh
```

### Limpiar base de datos

```bash
sudo bash reset-database.sh
```

---

## 📊 Monitoreo y Mantenimiento

### Recursos del Sistema

**CPU:** 
- Normal: 5-15%
- Picos: hasta 40% durante búsquedas

**RAM:**
- Backend: ~200-300 MB
- Frontend: ~100 MB
- MongoDB: ~500 MB - 1 GB

**Disco:**
- Aplicación: ~500 MB
- MongoDB (datos): Crece con el uso
- Logs: ~100 MB/mes

### Backups Automáticos

- **Frecuencia:** Diaria (2:00 AM)
- **Ubicación:** `/var/backups/taller-db/`
- **Retención:** Últimos 7 backups
- **Tamaño:** Depende de datos (típicamente 1-50 MB)

---

## 🆘 Solución de Problemas

### Problema: MongoDB no inicia (CPU sin AVX)

**Solución:**
```bash
# Instalar MongoDB 5.0 (no requiere AVX)
wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list
sudo apt update
sudo apt install -y mongodb-org=5.0.* mongodb-org-database=5.0.* mongodb-org-server=5.0.* mongodb-org-shell=5.0.* mongodb-org-mongos=5.0.* mongodb-org-tools=5.0.*
sudo systemctl start mongod
sudo systemctl enable mongod
```

### Problema: No se puede acceder desde otros dispositivos

**Verificar:**
1. Firewall: `sudo ufw status`
2. Apache corriendo: `sudo systemctl status apache2`
3. IP correcta: `hostname -I`

### Problema: Error 502 Bad Gateway

**Causa:** Backend no está corriendo

**Solución:**
```bash
sudo systemctl restart taller-backend
sudo journalctl -u taller-backend -n 50
```

---

## 📞 Información de Contacto

### Soporte Técnico

**Documentación completa:**
- `README_GITHUB.md` - Guía de instalación desde GitHub
- `README_INSTALACION.md` - Guía de instalación local
- `GUIA_DESPLIEGUE.md` - Guía manual completa
- `README_RESET_DB.md` - Guía de limpieza de base de datos

**Repositorio:**
https://github.com/Celorio10/DetectoresGas

**Issues/Problemas:**
https://github.com/Celorio10/DetectoresGas/issues

---

## ✅ Checklist de Instalación

### Pre-instalación
- [ ] Servidor Ubuntu 20.04+ disponible
- [ ] Acceso SSH con permisos sudo
- [ ] Conexión a Internet estable
- [ ] IP estática configurada (red local)
- [ ] Firewall configurado correctamente

### Durante la instalación
- [ ] Descargar script `install-github.sh`
- [ ] Ejecutar con sudo
- [ ] Proporcionar URL del repositorio cuando se solicite
- [ ] Esperar 15-20 minutos
- [ ] Verificar mensaje "Instalación completada"

### Post-instalación
- [ ] Acceder a `http://IP-SERVIDOR/AppTaller`
- [ ] Login con admin/admin123
- [ ] Cambiar contraseña de admin
- [ ] Crear usuarios adicionales
- [ ] Configurar marcas y modelos
- [ ] Realizar prueba completa del flujo
- [ ] Verificar backups automáticos funcionan
- [ ] Documentar IP y credenciales

### Producción
- [ ] Backups programados verificados
- [ ] Monitoreo de servicios configurado
- [ ] SSL/HTTPS configurado (si acceso externo)
- [ ] Credenciales de admin cambiadas
- [ ] Usuarios reales creados
- [ ] Capacitación a usuarios finales

---

## 📝 Notas Finales

**Tiempo de instalación:** 15-20 minutos (automático)  
**Dificultad:** Baja (script automatizado)  
**Conocimientos requeridos:** Básicos de Linux  
**Disponibilidad:** 24/7 una vez instalado  
**Mantenimiento:** Mínimo (backups automáticos)

---

**Versión del documento:** 1.0  
**Fecha:** Octubre 2024  
**Aplicación:** Sistema de Gestión de Taller v1.0
