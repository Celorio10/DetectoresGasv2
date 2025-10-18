# 🚀 Instalador desde GitHub con Subdirectorio

Este instalador descarga automáticamente tu proyecto desde GitHub y lo configura para funcionar en un subdirectorio de tu red local.

## ✨ Características Especiales

- 📥 **Descarga automática desde GitHub**
- 🌐 **Acceso vía subdirectorio**: `http://192.168.1.7/AppTaller`
- 🏠 **Acceso en red local** desde cualquier dispositivo
- ⚡ **Un solo comando** para instalar todo

---

## 🎯 Preparativos en GitHub

### 1. Sube tu Proyecto a GitHub

Tu repositorio debe tener esta estructura:

```
tu-repositorio/
├── backend/
│   ├── server.py
│   ├── requirements.txt
│   └── .env (opcional)
├── frontend/
│   ├── package.json
│   ├── src/
│   └── public/
└── README.md
```

**Alternativa:** También puede estar en una carpeta `app/`:

```
tu-repositorio/
└── app/
    ├── backend/
    └── frontend/
```

### 2. Asegúrate de que sea Público o Configura SSH

**Opción A: Repositorio Público** (más fácil)
- El instalador puede clonar directamente

**Opción B: Repositorio Privado**
- Configura SSH keys en tu servidor antes de instalar:

```bash
# Generar SSH key
ssh-keygen -t ed25519 -C "tu-email@ejemplo.com"

# Ver y copiar la clave pública
cat ~/.ssh/id_ed25519.pub

# Agrégala a GitHub en: Settings > SSH and GPG keys
```

---

## 🚀 Instalación

### Descarga el Script

**Opción 1: Si ya tienes el script localmente**

```bash
sudo bash install-github.sh
```

**Opción 2: Descarga directa desde tu repositorio**

```bash
# Reemplaza con la URL de tu repositorio
curl -sSL https://raw.githubusercontent.com/usuario/repositorio/main/install-github.sh | sudo bash
```

### El Script Te Preguntará

1. **URL del repositorio de GitHub**
   ```
   Ejemplos:
   https://github.com/usuario/taller-app.git
   https://github.com/usuario/taller-app
   git@github.com:usuario/taller-app.git (si usas SSH)
   ```

2. **Confirmar instalación**
   - Presiona `s` para continuar

---

## 🌐 Acceso a la Aplicación

Una vez instalado, podrás acceder desde:

### Desde el Servidor

```
http://localhost/AppTaller
```

### Desde Otros Dispositivos en la Red Local

```
http://192.168.1.7/AppTaller
```

O la IP que tenga tu servidor:

```
http://[IP-DE-TU-SERVIDOR]/AppTaller
```

**Para encontrar tu IP:**
```bash
hostname -I
# o
ip addr show
```

---

## 📋 Lo Que Hace el Script

### 1. ✅ Instalación de Software

- MongoDB 7.0
- Python 3 + pip + venv
- Node.js 18 + Yarn
- Apache2
- Git (para clonar)

### 2. 📥 Descarga desde GitHub

- Clona tu repositorio automáticamente
- Detecta la estructura (backend/frontend o app/backend/frontend)
- Copia archivos a `/var/www/taller-app/`

### 3. ⚙️ Configuración

**Backend:**
- Crea entorno virtual Python
- Instala dependencias
- Configura MongoDB
- Genera JWT secret
- Configura CORS para red local

**Frontend:**
- Instala dependencias (yarn)
- Configura para subdirectorio `/AppTaller`
- Build de producción
- Configura rutas correctamente

### 4. 🗄️ Base de Datos

- Crea base de datos `taller_production`
- Inserta modelos iniciales (Altair, Altair Pro, etc.)
- Crea usuario admin (admin/admin123)

### 5. 🌐 Servidor Web

Apache se configura para:
- Servir frontend en `/AppTaller`
- Proxy del API a `/AppTaller/api`
- React Router funcional
- Acceso desde red local

### 6. 🔒 Seguridad

- Permisos correctos
- Firewall (UFW)
- JWT secret seguro

---

## 🎯 Configuración Especial para Subdirectorio

El script automáticamente:

### En el Frontend:

1. **package.json:**
   ```json
   {
     "homepage": "/AppTaller"
   }
   ```

2. **.env:**
   ```bash
   REACT_APP_BACKEND_URL=http://192.168.1.7
   PUBLIC_URL=/AppTaller
   ```

### En Apache:

```apache
Alias "/AppTaller" "/var/www/taller-app/frontend/build"

<Directory "/var/www/taller-app/frontend/build">
    # Configuración React Router
    RewriteEngine On
    RewriteBase /AppTaller/
    RewriteRule ^index\.html$ - [L]
    RewriteCond %{REQUEST_FILENAME} !-f
    RewriteCond %{REQUEST_FILENAME} !-d
    RewriteRule . /AppTaller/index.html [L]
</Directory>

# Proxy para API
<Location "/AppTaller/api">
    ProxyPass http://localhost:8001/api
    ProxyPassReverse http://localhost:8001/api
</Location>
```

---

## 🔧 Comandos Útiles

### Ver Estado

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
sudo systemctl restart taller-backend
sudo systemctl restart apache2
```

### Ver Logs

```bash
# Log de instalación
sudo cat /var/log/taller-install.log

# Backend
sudo journalctl -u taller-backend -f

# Apache
sudo tail -f /var/log/apache2/error.log
```

### Actualizar desde GitHub

```bash
cd /var/www/taller-app
sudo rm -rf backend frontend

# Clonar repositorio actualizado
cd /tmp
git clone https://github.com/usuario/tu-repo.git

# Copiar archivos
sudo cp -r /tmp/tu-repo/backend /var/www/taller-app/
sudo cp -r /tmp/tu-repo/frontend /var/www/taller-app/

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

# Limpiar
rm -rf /tmp/tu-repo
```

---

## 🆘 Solución de Problemas

### Error: No se puede clonar el repositorio

**Causa:** Repositorio privado o URL incorrecta

**Solución:**
- Verifica la URL
- Si es privado, configura SSH keys
- Prueba clonar manualmente: `git clone URL-DEL-REPO`

### Error: Estructura no encontrada

**Causa:** El repositorio no tiene las carpetas backend/frontend

**Solución:**
- Verifica que tu repo tenga:
  - `backend/` y `frontend/`
  - O `app/backend/` y `app/frontend/`

### No puedo acceder desde otro dispositivo

**Causas posibles:**

1. **Firewall bloqueando:**
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw reload
   ```

2. **IP incorrecta:**
   ```bash
   # Ver todas las IPs
   hostname -I
   # Usa la IP de la red local (generalmente 192.168.x.x)
   ```

3. **Apache no está sirviendo:**
   ```bash
   sudo systemctl status apache2
   sudo systemctl restart apache2
   ```

### La aplicación carga pero la API no responde

**Verificar backend:**
```bash
# Estado del servicio
sudo systemctl status taller-backend

# Probar API directamente
curl http://localhost:8001/api/

# Ver logs
sudo journalctl -u taller-backend -f
```

### React Router no funciona (404 en subrutas)

**Verificar configuración de Apache:**
```bash
sudo apache2ctl configtest
sudo cat /etc/apache2/sites-available/000-default.conf
```

Debe tener las reglas de RewriteEngine para `/AppTaller`.

---

## 📱 Acceso desde Dispositivos Móviles

Desde cualquier dispositivo en la misma red WiFi:

1. **Android/iOS:**
   - Abre el navegador
   - Ingresa: `http://192.168.1.7/AppTaller`

2. **Laptop/PC:**
   - Cualquier navegador
   - Misma URL

---

## 🔄 Cambiar el Subdirectorio

Si quieres cambiar `/AppTaller` a otro nombre:

1. **Edita el script:**
   ```bash
   nano install-github.sh
   ```

2. **Cambia la variable:**
   ```bash
   SUBDIR_PATH="/MiTaller"  # O el nombre que prefieras
   ```

3. **Ejecuta el script**

---

## 📊 Ubicaciones de Archivos

```
/var/www/taller-app/          # Aplicación
├── backend/                   # Backend FastAPI
│   ├── venv/                 # Entorno virtual Python
│   ├── server.py
│   └── .env
└── frontend/                  # Frontend React
    └── build/                # Build de producción

/var/backups/taller-db/        # Backups automáticos
/var/log/taller-install.log    # Log de instalación
/var/log/apache2/              # Logs de Apache
```

---

## 🎓 Ejemplo Completo

### Paso a Paso Completo:

1. **Subir código a GitHub:**
   ```bash
   # En tu máquina local
   cd /ruta/a/tu/proyecto
   git init
   git add .
   git commit -m "Primera versión"
   git remote add origin https://github.com/usuario/taller-app.git
   git push -u origin main
   ```

2. **En el servidor Ubuntu:**
   ```bash
   # Descargar instalador
   wget https://raw.githubusercontent.com/usuario/taller-app/main/install-github.sh
   
   # Dar permisos
   chmod +x install-github.sh
   
   # Ejecutar
   sudo bash install-github.sh
   
   # Cuando pregunte, ingresa:
   # https://github.com/usuario/taller-app.git
   ```

3. **Acceder desde cualquier dispositivo:**
   ```
   http://192.168.1.7/AppTaller
   ```

4. **Login:**
   - Usuario: `admin`
   - Contraseña: `admin123`

---

## 🎉 ¡Listo!

Tu aplicación de Gestión de Taller está:
- ✅ Instalada desde GitHub
- ✅ Funcionando en subdirectorio
- ✅ Accesible desde toda tu red local
- ✅ Con backups automáticos
- ✅ Con auto-inicio en el servidor

**¡Disfruta gestionando tu taller! 🔧**
