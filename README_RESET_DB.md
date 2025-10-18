# 🗑️ Script de Limpieza de Base de Datos

Script para vaciar y resetear la base de datos de la aplicación de Gestión de Taller.

---

## 🚀 Uso Rápido

```bash
sudo bash reset-database.sh
```

---

## 📋 Opciones Disponibles

### 1️⃣ Vaciar TODO (Reset Completo)

**¿Qué hace?**
- Elimina TODOS los datos
- Usuarios (incluyendo admin)
- Equipos
- Marcas
- Modelos
- Clientes
- Técnicos

**Cuándo usar:**
- Empezar completamente de cero
- Después de muchas pruebas

**Comando directo:**
```bash
sudo bash reset-database.sh
# Selecciona opción 1
```

---

### 2️⃣ Vaciar Datos de Trabajo (Recomendado)

**¿Qué hace?**
- ✅ Elimina: Equipos, clientes, técnicos
- ✅ Mantiene: Usuario admin, modelos iniciales, marcas

**Cuándo usar:**
- ⭐ **RECOMENDADO** para empezar producción después de pruebas
- Mantiene la configuración básica
- Solo limpia los datos de prueba

**Comando directo:**
```bash
sudo bash reset-database.sh
# Selecciona opción 2
```

---

### 3️⃣ Vaciar Solo Equipos

**¿Qué hace?**
- ✅ Elimina: Todos los equipos registrados
- ✅ Mantiene: TODO lo demás (usuarios, clientes, técnicos, modelos)

**Cuándo usar:**
- Solo quieres limpiar los equipos
- Mantener clientes y técnicos registrados

**Comando directo:**
```bash
sudo bash reset-database.sh
# Selecciona opción 3
```

---

### 4️⃣ Reset Completo + Reinicializar

**¿Qué hace?**
1. Vacía TODO
2. Crea modelos iniciales (Altair, Altair Pro, etc.)
3. Crea usuario admin (admin/admin123)

**Cuándo usar:**
- ⭐ Quieres empezar de cero pero con la configuración básica
- Estado inicial de la aplicación

**Comando directo:**
```bash
sudo bash reset-database.sh
# Selecciona opción 4
```

---

### 5️⃣ Restaurar desde Backup

**¿Qué hace?**
- Muestra backups disponibles
- Restaura la base de datos desde un backup seleccionado

**Cuándo usar:**
- Cometiste un error al vaciar
- Quieres volver a un estado anterior

**Comando directo:**
```bash
sudo bash reset-database.sh
# Selecciona opción 5
```

---

### 6️⃣ Ver Estadísticas

**¿Qué hace?**
- Muestra cantidad de registros en cada colección
- No modifica nada

---

## 🔒 Características de Seguridad

### ✅ Backup Automático

**Antes de cada operación destructiva**, el script crea automáticamente un backup en:
```
/var/backups/taller-db/backup-before-reset-YYYYMMDD_HHMMSS/
```

### ✅ Confirmaciones

- Operaciones menores: requieren `s` (sí)
- Operaciones críticas: requieren escribir `SI` en mayúsculas

### ✅ Vista Previa

El script muestra las estadísticas actuales antes de hacer cualquier cambio.

---

## 📊 Ejemplo de Uso Completo

### Escenario 1: Terminaste pruebas y vas a producción

```bash
# 1. Ejecutar script
sudo bash reset-database.sh

# 2. Ver estadísticas actuales
# Selecciona opción: 2 (Vaciar datos de trabajo)

# 3. Confirmar con: s

# 4. Listo! Tienes:
#    - Usuario admin funcionando
#    - Modelos iniciales listos
#    - Base de datos limpia para producción
```

### Escenario 2: Quieres empezar completamente de cero

```bash
# 1. Ejecutar script
sudo bash reset-database.sh

# 2. Selecciona opción: 4 (Reset + Reinicializar)

# 3. Confirmar con: SI (en mayúsculas)

# 4. Listo! Aplicación como recién instalada
```

### Escenario 3: Solo limpiar equipos de prueba

```bash
# 1. Ejecutar script
sudo bash reset-database.sh

# 2. Selecciona opción: 3 (Solo equipos)

# 3. Confirmar con: s

# 4. Listo! Equipos eliminados, todo lo demás intacto
```

---

## 🔄 Flujo Recomendado: Pruebas → Producción

### Durante Desarrollo/Pruebas

```bash
# Probar funcionalidades
# Crear equipos de prueba
# Experimentar con la app
```

### Antes de Ir a Producción

```bash
# Opción A: Mantener configuración básica (RECOMENDADO)
sudo bash reset-database.sh
# Opción 2 - Vaciar datos de trabajo

# Opción B: Reset completo
sudo bash reset-database.sh
# Opción 4 - Reset + Reinicializar
```

### Resultado

✅ Base de datos limpia  
✅ Usuario admin: admin/admin123  
✅ Modelos listos (Altair, Altair Pro, etc.)  
✅ Sin datos de prueba  
✅ Lista para producción

---

## 🆘 Recuperación de Errores

### "Vacié por error la base de datos"

```bash
# 1. Ejecutar script
sudo bash reset-database.sh

# 2. Selecciona opción: 5 (Restaurar desde backup)

# 3. Selecciona el backup más reciente

# 4. Confirmar con: SI

# 5. ¡Restaurado!
```

### "El script no encuentra MongoDB"

```bash
# Verificar que MongoDB está corriendo
sudo systemctl status mongod

# Si no está corriendo, iniciarlo
sudo systemctl start mongod

# Luego ejecutar el script nuevamente
sudo bash reset-database.sh
```

### "No se pueden crear modelos iniciales"

```bash
# Verificar que el backend existe
ls -la /var/www/taller-app/backend/

# Verificar entorno virtual
ls -la /var/www/taller-app/backend/venv/

# Si falta algo, reinstalar con:
sudo bash install.sh
```

---

## 📁 Ubicaciones Importantes

```
/var/backups/taller-db/              # Backups automáticos
├── backup-before-reset-20250118_143022/
├── backup-before-reset-20250118_150133/
└── ...

/var/www/taller-app/backend/         # Backend (necesario para reinicializar)
```

---

## 🎯 Casos de Uso Específicos

### Caso 1: Demostración de la Aplicación

```bash
# Antes de la demo, llenar con datos de ejemplo
# Después de la demo:
sudo bash reset-database.sh
# Opción 2 - Mantener configuración
```

### Caso 2: Migración de Datos

```bash
# 1. Crear backup manual
sudo /usr/local/bin/taller-backup.sh

# 2. Vaciar base de datos
sudo bash reset-database.sh
# Opción 1 - Vaciar todo

# 3. Importar nuevos datos
mongorestore --db taller_production /ruta/nuevos/datos
```

### Caso 3: Múltiples Instalaciones de Prueba

```bash
# En cada instalación de prueba, después de usar:
sudo bash reset-database.sh
# Opción 4 - Reset + Reinicializar
```

---

## ⚠️ Advertencias Importantes

### ❗ Sin Undo

Una vez que vacías la base de datos (excepto por los backups automáticos), **no hay forma de deshacer la acción** sin un backup.

### ❗ Backups Automáticos

Los backups creados automáticamente por el script están en:
```
/var/backups/taller-db/backup-before-reset-*
```

Estos NO se borran automáticamente. Gestiónalos manualmente si ocupan mucho espacio.

### ❗ Aplicación en Producción

Si la aplicación está en uso por otros usuarios, **vaciar la base de datos eliminará su trabajo**. Coordina con tu equipo antes de usar este script.

---

## 🔧 Comandos MongoDB Directos (Avanzado)

Si prefieres usar MongoDB directamente:

### Ver todas las colecciones
```bash
mongosh taller_production --eval "show collections"
```

### Contar documentos
```bash
mongosh taller_production --eval "
  print('Usuarios: ' + db.users.countDocuments());
  print('Equipos: ' + db.equipment.countDocuments());
"
```

### Vaciar colección específica
```bash
mongosh taller_production --eval "db.equipment.deleteMany({})"
```

### Vaciar todo
```bash
mongosh taller_production --eval "db.dropDatabase()"
```

⚠️ **Cuidado:** Los comandos directos NO crean backup automático.

---

## 📞 Soporte

Si tienes problemas:

1. **Verifica MongoDB:**
   ```bash
   sudo systemctl status mongod
   ```

2. **Verifica logs:**
   ```bash
   sudo tail -f /var/log/mongodb/mongod.log
   ```

3. **Ejecuta con verbose:**
   ```bash
   bash -x reset-database.sh
   ```

---

## 🎉 Resumen Rápido

| Opción | Qué Elimina | Qué Mantiene | Cuándo Usar |
|--------|-------------|--------------|-------------|
| 1 | TODO | Nada | Reset total |
| 2 | Equipos, clientes, técnicos | Admin, modelos, marcas | ⭐ Producción |
| 3 | Solo equipos | Todo lo demás | Limpieza rápida |
| 4 | TODO + Reinicia | Admin + modelos | Estado inicial |
| 5 | - | - | Restaurar backup |

---

**¡Usa con precaución y siempre verifica los backups! 🔒**
