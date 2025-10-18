# 📦 Guía Completa de Instalación - Aplicación de Gestión de Taller

## 🎯 Tienes 3 Opciones de Instalación

---

## OPCIÓN 1: 🚀 Instalación Desde GitHub (RECOMENDADA)

**Ideal si:** Tu código está en GitHub y quieres acceso desde red local

### Paso 1: Subir tu Código a GitHub

Si aún no has subido tu código a GitHub:

```bash
# Desde el directorio de tu proyecto
chmod +x push-to-github.sh
bash push-to-github.sh
```

El script te guiará paso a paso:
- Configurará Git
- Creará .gitignore automáticamente
- Subirá tu código a GitHub
- Te dará la URL para usar en la instalación

### Paso 2: Instalar en el Servidor

En tu servidor Ubuntu:

```bash
# Opción A: Si tienes el script localmente
sudo bash install-github.sh

# Opción B: Descarga directa
curl -sSL https://raw.githubusercontent.com/tu-usuario/tu-repo/main/install-github.sh | sudo bash
```

**El script te preguntará:**
- URL de tu repositorio GitHub
- Confirmación para continuar

**Resultado:**
- ✅ Aplicación instalada en `/var/www/taller-app/`
- ✅ Accesible en: `http://192.168.1.7/AppTaller`
- ✅ Accesible desde cualquier dispositivo en tu red local
- ✅ Backend en `http://192.168.1.7/AppTaller/api`

📖 **Documentación completa:** Ver `README_GITHUB.md`

---

## OPCIÓN 2: 📁 Instalación Local

**Ideal si:** Tienes los archivos localmente y NO quieres usar GitHub

### Requisitos Previos

Tus archivos deben estar en:
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

### Instalación

```bash
cd /app
sudo bash install.sh
```

**El script te preguntará:**
- Tu dominio (o usa localhost)
- Si deseas instalar SSL/HTTPS

**Resultado:**
- ✅ Aplicación instalada en `/var/www/taller-app/`
- ✅ Accesible en: `http://tu-dominio.com` o `http://localhost`
- ✅ Backend en `http://tu-dominio.com/api`

📖 **Documentación completa:** Ver `README_INSTALACION.md`

---

## OPCIÓN 3: 📝 Instalación Manual

**Ideal si:** Quieres control total o personalizar la instalación

Sigue la guía paso a paso con todos los comandos explicados.

📖 **Documentación completa:** Ver `GUIA_DESPLIEGUE.md`

---

## 🔍 Comparación de Opciones

| Característica | GitHub | Local | Manual |
|----------------|--------|-------|--------|
| **Dificultad** | ⭐ Fácil | ⭐⭐ Media | ⭐⭐⭐ Avanzada |
| **Tiempo** | ~15 min | ~15 min | ~30-60 min |
| **GitHub requerido** | ✅ Sí | ❌ No | ❌ No |
| **Subdirectorio (/AppTaller)** | ✅ Sí | ❌ No | ⚙️ Configurable |
| **Acceso red local** | ✅ Sí | ⚙️ Configurable | ⚙️ Configurable |
| **Actualizaciones** | ⭐⭐⭐ Muy fácil | ⭐⭐ Media | ⭐ Manual |
| **Control** | ⭐⭐ Medio | ⭐⭐ Medio | ⭐⭐⭐ Total |

---

## 🎯 ¿Cuál Elegir?

### Elige OPCIÓN 1 (GitHub) si:
- ✅ Quieres acceso desde red local en `http://192.168.1.7/AppTaller`
- ✅ Planeas actualizar frecuentemente
- ✅ Quieres backup automático en GitHub
- ✅ Trabajas en equipo

### Elige OPCIÓN 2 (Local) si:
- ✅ No quieres usar GitHub
- ✅ Tienes los archivos localmente
- ✅ Necesitas instalación rápida
- ✅ Prefieres dominio propio o localhost

### Elige OPCIÓN 3 (Manual) si:
- ✅ Necesitas personalización avanzada
- ✅ Quieres entender cada paso
- ✅ Tienes requisitos específicos
- ✅ Eres un usuario avanzado

---

## 📚 Archivos de Documentación

| Archivo | Descripción | Cuándo Usar |
|---------|-------------|-------------|
| `README_GITHUB.md` | Guía instalación desde GitHub | Opción 1 |
| `README_INSTALACION.md` | Guía instalación local | Opción 2 |
| `GUIA_DESPLIEGUE.md` | Guía manual completa | Opción 3 |
| `README_RESET_DB.md` | Guía limpieza de base de datos | Después de pruebas |
| `RESUMEN_INSTALACION.md` | Este archivo (resumen) | Empezar aquí |

---

## 🚀 Inicio Rápido

### Para Impacientes (Opción 1 - GitHub)

```bash
# 1. Subir a GitHub (desde tu máquina local)
bash push-to-github.sh

# 2. Instalar (en el servidor Ubuntu)
sudo bash install-github.sh

# 3. Acceder
# http://192.168.1.7/AppTaller
```

### Para Impacientes (Opción 2 - Local)

```bash
# En el servidor con archivos en /app
cd /app
sudo bash install.sh

# Acceder a http://localhost o http://tu-dominio.com
```

---

## 🔑 Credenciales Por Defecto

**Todas las opciones crean el mismo usuario:**

- 👤 Usuario: `admin`
- 🔑 Contraseña: `admin123`

⚠️ **IMPORTANTE:** Cambia esta contraseña después del primer login

---

## 📋 Requisitos del Servidor

**Todas las opciones requieren:**

- Ubuntu 20.04 o superior
- Acceso root (sudo)
- Mínimo 2GB RAM
- Mínimo 10GB disco libre
- Conexión a Internet (durante instalación)

---

## 🎓 Flujo Completo Recomendado

### Desarrollo

1. **Desarrollar localmente**
   ```bash
   # En tu máquina de desarrollo
   cd /ruta/proyecto
   # ... desarrollar código ...
   ```

2. **Subir a GitHub**
   ```bash
   bash push-to-github.sh
   ```

### Producción

3. **Instalar en servidor**
   ```bash
   # En el servidor Ubuntu
   sudo bash install-github.sh
   # Ingresa URL de GitHub cuando pregunte
   ```

4. **Acceder desde red local**
   ```
   http://192.168.1.7/AppTaller
   ```

### Actualizaciones

5. **Actualizar código**
   ```bash
   # En tu máquina local
   git add .
   git commit -m "Mejoras"
   git push
   
   # En el servidor
   cd /var/www/taller-app
   git pull
   sudo systemctl restart taller-backend
   cd frontend && yarn build && cd ..
   sudo systemctl restart apache2
   ```

---

## 🆘 Ayuda y Soporte

### Problemas Comunes

1. **No puedo subir a GitHub**
   - Ver sección "Solución de Problemas" en `README_GITHUB.md`

2. **Instalación falla**
   - Ver logs: `sudo cat /var/log/taller-install.log`
   - Ver sección "Solución de Problemas" en el README correspondiente

3. **No puedo acceder desde otro dispositivo**
   - Verifica firewall: `sudo ufw status`
   - Verifica IP: `hostname -I`
   - Ver sección de red local en `README_GITHUB.md`

### Comandos Útiles

```bash
# Ver estado de servicios
sudo systemctl status taller-backend
sudo systemctl status apache2
sudo systemctl status mongod

# Ver logs
sudo journalctl -u taller-backend -f
sudo tail -f /var/log/apache2/error.log

# Reiniciar
sudo systemctl restart taller-backend
sudo systemctl restart apache2
```

---

## 📁 Estructura del Proyecto

```
tu-proyecto/
├── backend/                      # Backend FastAPI
│   ├── server.py                 # API principal
│   ├── requirements.txt          # Dependencias Python
│   └── .env                      # Variables de entorno
├── frontend/                     # Frontend React
│   ├── src/                      # Código fuente
│   ├── public/                   # Archivos estáticos
│   └── package.json              # Dependencias Node
├── install.sh                    # Instalador local
├── install-github.sh             # Instalador desde GitHub
├── push-to-github.sh             # Helper para subir a GitHub
├── GUIA_DESPLIEGUE.md           # Guía manual completa
├── README_INSTALACION.md         # Guía instalación local
├── README_GITHUB.md              # Guía instalación GitHub
└── RESUMEN_INSTALACION.md        # Este archivo
```

---

## 🎉 Próximos Pasos

Una vez instalado:

1. ✅ Accede a la aplicación
2. ✅ Cambia la contraseña de admin
3. ✅ Crea usuarios adicionales
4. ✅ Configura marcas, modelos, clientes
5. ✅ Comienza a registrar equipos

---

## 💡 Tips Importantes

### Seguridad
- 🔒 Cambia contraseña de admin inmediatamente
- 🔒 Usa contraseñas seguras
- 🔒 Habilita SSL/HTTPS si es accesible desde internet
- 🔒 Mantén el sistema actualizado

### Backups
- 💾 Los backups son automáticos (diarios a las 2 AM)
- 💾 Se guardan en `/var/backups/taller-db/`
- 💾 Se mantienen los últimos 7 backups
- 💾 Para backup manual: `sudo /usr/local/bin/taller-backup.sh`

### Actualizaciones
- 🔄 Backend: Actualiza requirements.txt y reinicia servicio
- 🔄 Frontend: Ejecuta `yarn build` después de cambios
- 🔄 Desde GitHub: `git pull` para obtener últimos cambios

---

## 📞 Contacto

Si necesitas ayuda adicional:
- 📖 Lee la documentación específica para tu opción
- 🔍 Busca en la sección de Solución de Problemas
- 📋 Revisa los logs del sistema

---

## ✨ Características de la Aplicación

### 📝 Módulo 1: Entrada de Equipos
- Registro completo de equipos
- Marcas y modelos configurables
- Clientes con CIF
- Observaciones y fecha de entrada

### 🔧 Módulo 2: Revisión de Equipos
- Búsqueda por número de serie
- Tabla de calibración (hasta 6 sensores)
- Registro de repuestos
- Asignación de técnico

### 📦 Módulo 3: Salida de Equipos
- Listado de equipos calibrados
- Selección múltiple
- Número de albarán
- Lugar de entrega

### 📊 Módulo 4: Resumen
- Historial completo
- Cálculo automático de tiempo en taller
- Estadísticas
- Filtros y búsquedas

---

**¡Buena suerte con tu instalación! 🚀**
