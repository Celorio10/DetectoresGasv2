# REQUERIMIENTOS TÉCNICOS - Sistema de Gestión de Taller
## Versión Resumida para Servicio Técnico

---

## 📦 INFORMACIÓN DEL PROYECTO

**Aplicación:** Sistema de Gestión de Taller de Equipos  
**Repositorio:** https://github.com/Celorio10/DetectoresGas  
**Stack:** Python (FastAPI) + React + MongoDB

---

## 💻 SERVIDOR

### Sistema Operativo
- ✅ **Ubuntu 20.04 LTS o superior** (REQUERIDO)
- ❌ NO compatible con Debian, CentOS, Windows

### Hardware Mínimo
| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| CPU | 2 cores | 4 cores |
| RAM | 2 GB | 4 GB |
| Disco | 10 GB libres | 20 GB libres |
| Red | 100 Mbps | 1 Gbps |

⚠️ **IMPORTANTE:** Si CPU no soporta AVX, usar MongoDB 5.0 en lugar de 7.0

---

## 🌐 RED Y ACCESO

### Puertos
- **80** (HTTP) - Interfaz web
- **443** (HTTPS) - Opcional, con SSL
- 8001 (Backend - solo interno)
- 27017 (MongoDB - solo interno)

### IP Recomendada
- IP estática en red local (ej: 192.168.1.7)

### URL de Acceso
```
http://192.168.1.7/AppTaller
```

---

## 🚀 INSTALACIÓN (MÉTODO AUTOMÁTICO)

### Requisitos Previos
1. Servidor Ubuntu con acceso sudo
2. Conexión a Internet
3. MongoDB instalado (si CPU sin AVX, usar v5.0)

### Comandos

```bash
# 1. Descargar instalador
wget https://raw.githubusercontent.com/Celorio10/DetectoresGas/main/install-github.sh

# 2. Dar permisos
chmod +x install-github.sh

# 3. Ejecutar
sudo bash install-github.sh

# 4. Cuando pregunte la URL del repo, ingresar:
https://github.com/Celorio10/DetectoresGas.git
```

**Tiempo de instalación:** 15-20 minutos (automático)

---

## 🔧 DESPUÉS DE LA INSTALACIÓN

### Acceso Inicial
- **URL:** http://[IP-DEL-SERVIDOR]/AppTaller
- **Usuario:** admin
- **Contraseña:** admin123

⚠️ **CAMBIAR contraseña después del primer login**

### Verificar Servicios
```bash
sudo systemctl status taller-backend
sudo systemctl status apache2
sudo systemctl status mongod
```

### Ver Logs (si hay problemas)
```bash
sudo tail -f /var/log/taller-install.log
sudo journalctl -u taller-backend -f
```

---

## ⚙️ COMANDOS ÚTILES

### Reiniciar Aplicación
```bash
sudo systemctl restart taller-backend
sudo systemctl restart apache2
```

### Backup Manual
```bash
sudo /usr/local/bin/taller-backup.sh
```

### Limpiar Base de Datos
```bash
sudo bash reset-database.sh
```

---

## 🆘 PROBLEMAS COMUNES

### 1. MongoDB no inicia (CPU antiguo sin AVX)

**Instalar MongoDB 5.0:**
```bash
wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list
sudo apt update
sudo apt install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod
```

### 2. No se puede acceder desde otros dispositivos

**Verificar:**
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo systemctl status apache2
hostname -I  # Ver IP del servidor
```

### 3. Error 502 Bad Gateway

**Reiniciar backend:**
```bash
sudo systemctl restart taller-backend
sudo journalctl -u taller-backend -n 50
```

---

## 📋 CHECKLIST DE INSTALACIÓN

**Pre-instalación:**
- [ ] Servidor Ubuntu 20.04+ disponible
- [ ] Acceso SSH con sudo
- [ ] Conexión a Internet
- [ ] IP estática configurada

**Instalación:**
- [ ] Descargar `install-github.sh`
- [ ] Ejecutar con sudo
- [ ] Proporcionar URL del repo
- [ ] Esperar 15-20 minutos

**Post-instalación:**
- [ ] Acceder a http://IP/AppTaller
- [ ] Login admin/admin123
- [ ] Cambiar contraseña
- [ ] Crear usuarios
- [ ] Realizar prueba completa

---

## 📞 SOPORTE

**Repositorio:** https://github.com/Celorio10/DetectoresGas  
**Documentación completa:** Ver archivos README_*.md en el repositorio

---

**Última actualización:** Octubre 2024
