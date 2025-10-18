# 🚀 Instalador Automático - Gestión de Taller

Este script automatiza completamente la instalación de la aplicación de Gestión de Taller en un servidor Ubuntu.

## ⚡ Instalación en 1 Comando

### Opción 1: Instalación Directa (Recomendada)

```bash
sudo bash install.sh
```

### Opción 2: Desde GitHub/Repositorio Remoto

```bash
curl -sSL https://tu-repo.com/install.sh | sudo bash
```

---

## 📋 Requisitos

- **Sistema Operativo:** Ubuntu 20.04 o superior
- **Acceso:** Root o sudo
- **Memoria RAM:** Mínimo 2GB
- **Disco:** Mínimo 10GB libres
- **Conexión a Internet:** Requerida durante la instalación

---

## 🎯 ¿Qué Hace el Script?

El instalador automático realiza las siguientes acciones:

### 1. ✅ Verificaciones Iniciales
- Verifica que se ejecute como root
- Confirma que es Ubuntu
- Crea logs de instalación

### 2. 📦 Instalación de Software
- Python 3.8+ con pip y venv
- Node.js 18.x y Yarn
- MongoDB 7.0
- Apache2 con módulos necesarios

### 3. ⚙️ Configuración de la Aplicación
- Crea estructura de directorios
- Configura backend (FastAPI)
- Instala dependencias Python
- Genera JWT secret seguro
- Configura frontend (React)
- Construye aplicación de producción

### 4. 🗄️ Base de Datos
- Inicia MongoDB
- Crea base de datos de producción
- Inserta modelos iniciales (Altair, Altair Pro, etc.)
- Crea usuario administrador por defecto

### 5. 🔧 Servicios del Sistema
- Crea servicio systemd para backend
- Configura reinicio automático
- Habilita inicio automático al bootear

### 6. 🌐 Servidor Web
- Configura Apache2 como proxy reverso
- Sirve frontend estático
- Redirige API al backend
- Configura virtual host

### 7. 🔒 Seguridad
- Configura permisos correctos
- Configura firewall (UFW)
- Opción de instalar SSL/HTTPS

### 8. 🛠️ Extras
- Script de backup automático
- Cron job para backups diarios
- Logs estructurados

---

## 🚀 Instrucciones de Uso

### Paso 1: Preparar los Archivos

Asegúrate de que tienes la estructura:

```
/app/
├── backend/
│   ├── server.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── package.json
│   ├── src/
│   └── public/
└── install.sh
```

### Paso 2: Dar Permisos de Ejecución

```bash
chmod +x /app/install.sh
```

### Paso 3: Ejecutar el Instalador

```bash
cd /app
sudo bash install.sh
```

### Paso 4: Seguir las Instrucciones

El script te preguntará:

1. **Dominio:** Ingresa tu dominio (ej: `midominio.com`) o presiona Enter para usar `localhost`

2. **SSL (opcional):** Si configuraste un dominio real, te preguntará si deseas instalar certificado SSL

   - Responde `s` para Sí
   - Ingresa tu email
   - **Importante:** Tu dominio debe apuntar al servidor antes de esto

---

## ⏱️ Tiempo de Instalación

- **Conexión rápida:** ~10-15 minutos
- **Conexión lenta:** ~20-30 minutos

---

## 📊 Al Finalizar

Al completarse la instalación verás:

```
╔════════════════════════════════════════════════════════════════╗
║                    INFORMACIÓN DE ACCESO                       ║
╚════════════════════════════════════════════════════════════════╝

  🌐 URL de la aplicación: http://tu-dominio.com

╔════════════════════════════════════════════════════════════════╗
║                  CREDENCIALES POR DEFECTO                      ║
╚════════════════════════════════════════════════════════════════╝

  👤 Usuario: admin
  🔑 Contraseña: admin123

  ⚠️  ¡IMPORTANTE! Cambia esta contraseña después del primer login
```

---

## 🎮 Uso de la Aplicación

### Acceder

1. Abre tu navegador
2. Ve a la URL mostrada (http://tu-dominio.com o http://localhost)
3. Inicia sesión con `admin` / `admin123`
4. **Cambia la contraseña inmediatamente**

### Funcionalidades

- ✅ **Entrada de Equipos:** Registra equipos que llegan al taller
- ✅ **Revisión de Equipos:** Calibra y revisa equipos
- ✅ **Salida de Equipos:** Gestiona entregas
- ✅ **Resumen:** Consulta historial y estadísticas

---

## 🔧 Comandos Útiles Post-Instalación

### Ver Estado de Servicios

```bash
# Backend
sudo systemctl status taller-backend

# Apache
sudo systemctl status apache2

# MongoDB
sudo systemctl status mongod
```

### Reiniciar Servicios

```bash
# Reiniciar backend
sudo systemctl restart taller-backend

# Reiniciar Apache
sudo systemctl restart apache2

# Reiniciar MongoDB
sudo systemctl restart mongod
```

### Ver Logs

```bash
# Logs del backend
sudo journalctl -u taller-backend -f

# Logs de Apache
sudo tail -f /var/log/apache2/taller-error.log

# Log de instalación
sudo cat /var/log/taller-install.log
```

### Hacer Backup Manual

```bash
sudo /usr/local/bin/taller-backup.sh
```

Los backups se guardan en: `/var/backups/taller-db/`

---

## 🆘 Solución de Problemas

### El Script Falla

```bash
# Ver el log de instalación
sudo cat /var/log/taller-install.log

# Ver últimas 50 líneas
sudo tail -50 /var/log/taller-install.log
```

### Backend No Inicia

```bash
# Ver estado detallado
sudo systemctl status taller-backend

# Ver logs
sudo journalctl -u taller-backend -n 100
```

### Apache No Sirve la Aplicación

```bash
# Verificar configuración
sudo apache2ctl configtest

# Ver logs de error
sudo tail -f /var/log/apache2/error.log
```

### MongoDB No Conecta

```bash
# Verificar que está corriendo
sudo systemctl status mongod

# Ver logs
sudo tail -f /var/log/mongodb/mongod.log

# Reiniciar MongoDB
sudo systemctl restart mongod
```

### Página No Carga

1. Verifica que todos los servicios estén corriendo
2. Verifica el firewall: `sudo ufw status`
3. Si usas un dominio, verifica que apunte al servidor
4. Verifica los logs de Apache

---

## 🔄 Reinstalar o Actualizar

### Reinstalación Completa

```bash
# Detener servicios
sudo systemctl stop taller-backend
sudo systemctl stop apache2

# Eliminar instalación anterior
sudo rm -rf /var/www/taller-app

# Ejecutar instalador nuevamente
sudo bash install.sh
```

### Actualizar Solo la Aplicación

```bash
# Copiar archivos nuevos
sudo cp -r /app/backend/* /var/www/taller-app/backend/
sudo cp -r /app/frontend/* /var/www/taller-app/frontend/

# Actualizar backend
cd /var/www/taller-app/backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart taller-backend

# Actualizar frontend
cd /var/www/taller-app/frontend
yarn install
yarn build
sudo systemctl restart apache2
```

---

## 📁 Ubicaciones Importantes

- **Aplicación:** `/var/www/taller-app/`
- **Backend:** `/var/www/taller-app/backend/`
- **Frontend:** `/var/www/taller-app/frontend/`
- **Backups:** `/var/backups/taller-db/`
- **Logs:** `/var/log/taller-install.log`
- **Apache Logs:** `/var/log/apache2/`

---

## 🔐 Configurar SSL Después

Si instalaste sin SSL y ahora quieres agregarlo:

```bash
# Instalar Certbot
sudo apt install certbot python3-certbot-apache -y

# Obtener certificado
sudo certbot --apache -d tu-dominio.com -d www.tu-dominio.com

# Actualizar frontend para usar HTTPS
cd /var/www/taller-app/frontend
sudo sed -i 's|http://|https://|g' .env
yarn build
sudo systemctl restart apache2
```

---

## 🗑️ Desinstalar Completamente

```bash
# Detener servicios
sudo systemctl stop taller-backend
sudo systemctl stop apache2
sudo systemctl stop mongod

# Deshabilitar servicios
sudo systemctl disable taller-backend
sudo systemctl disable apache2
sudo systemctl disable mongod

# Eliminar archivos
sudo rm -rf /var/www/taller-app
sudo rm -rf /var/backups/taller-db
sudo rm /etc/systemd/system/taller-backend.service
sudo rm /etc/apache2/sites-available/taller-app.conf
sudo rm /usr/local/bin/taller-backup.sh

# Eliminar paquetes (opcional)
sudo apt remove mongodb-org apache2 -y
sudo apt autoremove -y

# Recargar systemd
sudo systemctl daemon-reload
```

---

## ❓ Preguntas Frecuentes

### ¿Puedo usar mi propio dominio?

Sí, simplemente ingrésalo cuando el script lo pregunte. Asegúrate de que el dominio apunte a tu servidor.

### ¿Necesito SSL?

No es obligatorio, pero es muy recomendado para producción. Puedes agregarlo después.

### ¿Los backups son automáticos?

Sí, se ejecutan diariamente a las 2 AM y se mantienen los últimos 7 backups.

### ¿Cómo cambio la contraseña del admin?

1. Inicia sesión en la aplicación
2. Ve a tu perfil o configuración
3. Cambia la contraseña desde ahí

O manualmente en la base de datos:

```bash
mongosh taller_production
db.users.updateOne(
  {username: "admin"},
  {$set: {hashed_password: "nuevo_hash_aquí"}}
)
```

### ¿Puedo instalar en otra ubicación?

Sí, edita la variable `INSTALL_DIR` al inicio del script `install.sh`.

---

## 📞 Soporte

Si encuentras problemas:

1. Revisa los logs: `sudo cat /var/log/taller-install.log`
2. Verifica el estado de servicios
3. Consulta la sección de Solución de Problemas
4. Revisa la guía manual: `GUIA_DESPLIEGUE.md`

---

## 📝 Licencia

Este software es propiedad de tu organización.

---

## 🎉 ¡Listo!

Tu aplicación de Gestión de Taller está instalada y lista para usar.

**¡Disfruta gestionando tu taller! 🔧**
