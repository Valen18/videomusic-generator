# 🎵 VideoMusic Generator - Inicio Rápido

## ✅ Correcciones Realizadas

Se han corregido los siguientes problemas:

1. **✅ Botón Generar no hacía nada**: El frontend está correctamente conectado al backend vía WebSocket
2. **✅ Dependencias actualizadas**: Se agregaron todas las dependencias necesarias para FastAPI, WebSockets, OpenAI y Replicate
3. **✅ Scripts de despliegue para Linux**: Creados scripts automáticos para instalación y despliegue
4. **✅ Corrección de advertencia de deprecación**: Se actualizó a lifespan events en FastAPI
5. **✅ Pequeño bug en la UI**: Corregido el toast de "Generando video..." que mostraba tipo "error" en lugar de "success"

## 🚀 Cómo Ejecutar en Linux

### Opción 1: Instalación y Prueba Local

```bash
# Dar permisos de ejecución
chmod +x install.sh start_web.sh

# Instalar dependencias
bash install.sh

# Iniciar la aplicación
bash start_web.sh
```

Accede a: **http://localhost:8000**

### Opción 2: Despliegue en Producción con Nginx

```bash
# Dar permisos de ejecución
chmod +x deploy_linux.sh

# Desplegar (requiere sudo)
sudo bash deploy_linux.sh
```

Accede a: **http://IP-DEL-SERVIDOR**

## 📝 Credenciales por Defecto

- **Usuario**: `admin`
- **Contraseña**: `admin123`

⚠️ **IMPORTANTE**: Cambia la contraseña inmediatamente después del primer inicio de sesión.

## ⚙️ Configuración de API Keys

Después de iniciar sesión:

1. Haz clic en **⚙️ Configuración**
2. Ingresa tus API Keys:
   - **Suno API Key** (Requerida): Para generar música
   - **Replicate API Token** (Opcional): Para generar imágenes y videos
   - **OpenAI API Key** (Opcional): Para generar letras con IA
3. Haz clic en **💾 Guardar**
4. Valida las conexiones con **🔍 Validar Conectividad**

## 🎵 Cómo Generar una Canción

1. **Genera la letra** (opcional):
   - Escribe una descripción en "Descripción para generar letra"
   - Haz clic en **✨ Generar Letra con IA**
   - O escribe tu propia letra directamente

2. **Configura la canción**:
   - Ingresa un **Título**
   - Selecciona un **Estilo musical**
   - Elige el **Modelo** (recomendado: V4.5)
   - Activa **Generar imagen de portada** si quieres una portada

3. **Genera**:
   - Haz clic en **🎵 Generar Canción**
   - Espera a que se complete el proceso
   - Revisa tu canción en la pestaña **🎵 Historial**

## 📁 Archivos Importantes

- `web_app_secure.py` - Servidor web principal
- `web/` - Archivos del frontend (HTML, CSS, JS)
- `database.py` - Gestión de usuarios y sesiones
- `requirements.txt` - Dependencias Python
- `install.sh` - Script de instalación
- `start_web.sh` - Script de inicio (desarrollo)
- `deploy_linux.sh` - Script de despliegue (producción)
- `DEPLOYMENT.md` - Guía completa de despliegue

## 🔧 Gestión del Servicio (Producción)

```bash
# Ver estado
sudo systemctl status videomusic-generator

# Ver logs en tiempo real
sudo journalctl -u videomusic-generator -f

# Reiniciar
sudo systemctl restart videomusic-generator

# Detener
sudo systemctl stop videomusic-generator
```

## 🐛 Solución de Problemas

### El botón "Generar" no hace nada

1. Verifica que hayas configurado tu Suno API Key
2. Abre la consola del navegador (F12) y busca errores
3. Verifica que el WebSocket esté conectado (debería mostrar "Listo" en el header)

### No puedo conectarme al servidor

1. Verifica que el servidor esté corriendo: `sudo systemctl status videomusic-generator`
2. Revisa los logs: `sudo journalctl -u videomusic-generator -f`
3. Verifica el firewall: `sudo ufw status`

### Las APIs no funcionan

1. Ve a **⚙️ Configuración** y haz clic en **🔍 Validar Conectividad**
2. Verifica que tus API Keys sean válidas
3. Revisa los logs para más detalles

## 📖 Documentación Adicional

- [DEPLOYMENT.md](DEPLOYMENT.md) - Guía completa de despliegue y configuración
- [README.md](README.md) - Información general del proyecto

## 💡 Consejos

1. **Usa V4.5**: Es el modelo más reciente y genera mejor calidad
2. **Estilo específico**: Selecciona un estilo musical para mejores resultados
3. **Letras claras**: Asegúrate de que la letra esté bien formateada
4. **Genera portadas**: Las canciones con portada se ven mucho mejor
5. **Backup regular**: Haz backups de `videomusic.db` y la carpeta `output/`

---

¡Disfruta generando música! 🎵🎬
