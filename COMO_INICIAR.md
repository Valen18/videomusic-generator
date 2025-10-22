# 🚀 Cómo Iniciar la Aplicación

## Inicio Rápido

### 1. Instalar dependencias (solo la primera vez)

```bash
pip install -r requirements-web.txt
```

### 2. Iniciar el servidor

```bash
python start_server.py
```

### 3. Abrir en el navegador

```
http://localhost:8000
```

### 4. Iniciar sesión

**Credenciales por defecto:**
- **Usuario:** `admin`
- **Contraseña:** `admin123`

⚠️ **¡IMPORTANTE!** Cambia la contraseña después del primer login.

---

## Configurar tus API Keys

1. Inicia sesión
2. Haz clic en el botón **⚙️ Configuración**
3. Ingresa tus API keys:
   - **Suno API Key** (requerido para generar música)
   - **Replicate API Token** (opcional, para imágenes y videos)
   - **OpenAI API Key** (opcional, para generar letras con IA)
4. Haz clic en **💾 Guardar**
5. Haz clic en **🔍 Validar Conectividad** para verificar que funcionen

---

## Solución de Problemas

### Error: "Puerto 8000 ya está en uso"

**Opción 1: Cerrar el proceso que usa el puerto**

```bash
# Ver qué proceso usa el puerto 8000
netstat -ano | findstr :8000

# Matar el proceso (reemplaza <PID> con el número mostrado)
taskkill /F /PID <PID>
```

**Opción 2: Usar otro puerto**

Edita `start_server.py` y cambia la línea:
```python
port=8000,  # Cambiar a 8001, 8080, etc.
```

### Error: "Module not found"

Instala las dependencias:
```bash
pip install -r requirements-web.txt
```

### Error de codificación / caracteres raros

Ya está solucionado en `start_server.py`. Si persiste, ejecuta:
```bash
chcp 65001
python start_server.py
```

### No puedo acceder desde otro dispositivo

Por defecto el servidor solo acepta conexiones desde localhost (127.0.0.1).

Para permitir acceso desde otros dispositivos en la misma red:

Edita `start_server.py` y cambia:
```python
host="127.0.0.1",  # Cambiar a "0.0.0.0"
```

Luego accede desde otro dispositivo usando:
```
http://IP_DE_TU_PC:8000
```

---

## ¿Qué puedo hacer con la aplicación?

### 1. Generar música con IA 🎵
- Escribe una descripción o letra
- Selecciona estilo musical
- Genera la canción

### 2. Crear letras con OpenAI 🤖
- Describe de qué quieres que sea la canción
- La IA genera la letra completa
- Edítala si quieres

### 3. Generar imágenes de portada 🖼️
- Se generan automáticamente con la canción
- O agrégalas después desde el Historial
- Estilo ilustración infantil 16:9

### 4. Crear videos animados 🎬
- Anima la imagen de portada
- Video en bucle sincronizado con la música
- Con subtítulos karaoke opcionales

### 5. Ver tu historial 📜
- Todas tus canciones guardadas
- Buscar por título o estilo
- Reproducir, descargar, compartir

---

## Archivos Generados

Los archivos se guardan en:
```
output/user_<id>/<session_id>/
```

Cada sesión contiene:
- 🎵 **Audio:** `track_1_<título>.mp3`
- 🖼️ **Imagen:** `<session_id>_cover.png`
- 🎬 **Video:** `<session_id>_cover_video.mp4`
- 📝 **Metadata:** `metadata.json`

---

## Siguiente Paso: Desplegar en Internet

Si quieres que otras personas accedan a tu aplicación desde internet, revisa:

📖 **`DEPLOY.md`** - Guía completa de despliegue

Opciones incluidas:
- Render (gratis)
- Railway ($5 gratis)
- Heroku
- VPS (DigitalOcean, AWS, etc.)
- Docker

---

## ¿Necesitas Ayuda?

1. **Revisa esta guía** primero
2. **Revisa el archivo `README_FINAL.md`** para más detalles
3. **Mira los logs** del servidor para ver errores específicos
4. **Revisa `DEPLOY.md`** si quieres desplegar en producción

---

## 🎉 ¡Disfruta generando música con IA!
