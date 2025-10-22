# 🎵 VideoMusic Generator - Aplicación Web

Aplicación web moderna para generar música, imágenes y videos con IA usando SunoAPI, Replicate y OpenAI.

## ✨ Características

- 🎵 **Generación de música** con SunoAPI (V3.5, V4, V4.5)
- 🤖 **Generación de letras con IA** usando OpenAI Assistant
- 🖼️ **Imágenes de portada** con Replicate (ratio 16:9)
- 🎬 **Videos animados** con bucle sincronizado con la música
- 📊 **Progreso en tiempo real** mediante WebSockets
- 📱 **Interfaz responsive** y moderna
- 💾 **Historial de sesiones** con búsqueda y filtrado
- ⚙️ **Configuración web** de API keys (sin necesidad de archivos .env)

## 🚀 Instalación Rápida

### 1. Instalar dependencias

```bash
pip install -r requirements-web.txt
```

### 2. Ejecutar la aplicación

```bash
python web_app.py
```

La aplicación estará disponible en: **http://localhost:8000**

## 📝 Configuración

### Configuración desde la interfaz web

1. Abre la aplicación en tu navegador: http://localhost:8000
2. Haz clic en **⚙️ Configuración** en la esquina superior derecha
3. Ingresa tus API keys:
   - **Suno API Key** (requerido): Para generar música
   - **Replicate API Token** (opcional): Para generar imágenes y videos
   - **OpenAI API Key** (opcional): Para generar letras con IA
4. Haz clic en **💾 Guardar**

### Configuración con archivo (alternativa)

Crea un archivo `api_config.json` en la raíz del proyecto:

```json
{
  "suno_api_key": "tu-suno-api-key",
  "suno_base_url": "https://api.sunoapi.org",
  "replicate_api_token": "tu-replicate-token",
  "openai_api_key": "tu-openai-api-key",
  "openai_assistant_id": "asst_tR6OL8QLpSsDDlc6hKdBmVNU"
}
```

## 🎯 Uso

### Generar una canción

1. **Genera letra con IA** (opcional):
   - Escribe una descripción: "Canción alegre sobre un perro que va a la playa"
   - Haz clic en **✨ Generar Letra con IA**
   - O escribe tu propia letra

2. **Configura tu canción**:
   - Título: "Mi Perro Surfista"
   - Estilo musical: Selecciona del menú (ej: "Kids Pop")
   - Modelo: V4.5 (recomendado)
   - Opciones: Modo personalizado, Instrumental
   - Generar imagen de portada (si está habilitado)

3. **Genera**:
   - Haz clic en **🎵 Generar Canción**
   - Observa el progreso en tiempo real
   - Espera a que se complete (puede tardar 2-5 minutos)

4. **Revisa tu creación**:
   - Ve a la pestaña **🎵 Historial**
   - Haz clic en tu sesión para ver detalles
   - Reproduce el audio, ve la imagen y el video

### Generar imagen y video para una sesión existente

1. Ve a **🎵 Historial**
2. En una sesión que tenga audio pero no imagen:
   - Haz clic en **📸 Imagen** para generar portada
3. Una vez que tenga imagen:
   - Haz clic en **🎬 Video** para animar la portada
4. Si quieres recrear el bucle de video:
   - Haz clic en **🔄 Recrear bucle**

## 🔧 Arquitectura

### Backend (FastAPI)

- **web_app.py**: Servidor FastAPI con WebSocket support
- **API REST**: Endpoints para configuración, sesiones y archivos
- **WebSocket**: Comunicación en tiempo real para progreso
- **Casos de uso**: Reutiliza toda la lógica de negocio existente

### Frontend (HTML/CSS/JavaScript Vanilla)

- **index.html**: Estructura de la aplicación
- **styles.css**: Estilos modernos con tema oscuro
- **app.js**: Lógica del cliente y manejo de WebSockets

### Estructura de archivos

```
videomusic-generator/
├── web_app.py              # Servidor FastAPI
├── web/                    # Frontend
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── src/                    # Lógica de negocio (sin cambios)
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   └── presentation/
├── output/                 # Archivos generados
├── api_config.json         # Configuración (creado automáticamente)
├── requirements-web.txt    # Dependencias web
└── README-WEB.md          # Este archivo
```

## 🌐 API Endpoints

### Status y Configuración

- `GET /api/status` - Estado de configuración
- `GET /api/config` - Configuración actual (keys enmascaradas)
- `POST /api/config` - Actualizar configuración

### Generación de Letras

- `POST /api/generate-lyrics` - Generar letra con OpenAI

### Sesiones

- `GET /api/sessions` - Listar todas las sesiones
- `GET /api/sessions/{session_id}` - Obtener detalles de sesión

### Archivos

- `GET /api/files/{session_id}/{filename}` - Descargar archivo (audio, imagen, video)

### WebSocket

- `WS /ws/{client_id}` - Conexión WebSocket para progreso en tiempo real

## 📦 Despliegue en Producción

### Opción 1: Servidor local con uvicorn

```bash
uvicorn web_app:app --host 0.0.0.0 --port 8000
```

### Opción 2: Docker (recomendado)

Crea un `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements-web.txt .
RUN pip install --no-cache-dir -r requirements-web.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "web_app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Construye y ejecuta:

```bash
docker build -t videomusic-generator .
docker run -p 8000:8000 -v $(pwd)/output:/app/output videomusic-generator
```

### Opción 3: Plataformas Cloud

#### Render, Railway, Fly.io

1. Conecta tu repositorio
2. Comando de inicio: `uvicorn web_app:app --host 0.0.0.0 --port $PORT`
3. Variables de entorno (opcional):
   - `SUNO_API_KEY`
   - `REPLICATE_API_TOKEN`
   - `OPENAI_API_KEY`

#### Vercel, Netlify

Estas plataformas son para sitios estáticos. Usa Render o Railway para el backend FastAPI.

## 🔐 Seguridad

### Buenas prácticas

1. **API Keys**: Nunca compartas tus API keys públicamente
2. **HTTPS**: En producción, usa siempre HTTPS
3. **Autenticación**: Considera añadir autenticación de usuarios
4. **Rate Limiting**: Implementa límites de tasa para prevenir abuso
5. **CORS**: Ajusta la configuración CORS según tus necesidades

### Mejoras recomendadas para producción

```python
# En web_app.py, modifica el middleware CORS:

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tu-dominio.com"],  # Específico
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## 🐛 Solución de Problemas

### Error: "Configuración requerida"

- Asegúrate de configurar al menos tu Suno API Key en **⚙️ Configuración**

### Error de conexión WebSocket

- Verifica que el puerto 8000 esté abierto
- En producción, asegúrate de que tu servidor soporte WebSockets

### Los archivos no se descargan

- Verifica que la carpeta `output/` exista y tenga permisos de escritura
- En Docker, monta el volumen correctamente: `-v $(pwd)/output:/app/output`

### Error "Module not found"

```bash
pip install -r requirements-web.txt
```

## 📊 Diferencias con la aplicación Desktop

| Característica | Desktop (Tkinter) | Web (FastAPI) |
|----------------|-------------------|---------------|
| Interfaz | GUI nativa | Navegador web |
| Configuración | Archivo .env o ventana | Interfaz web + JSON |
| Progreso | Barra de progreso | WebSocket en tiempo real |
| Historial | Tabla Tkinter | Cards responsive |
| Despliegue | Ejecutable | Servidor web |
| Multiplataforma | Requiere compilar | Acceso desde cualquier navegador |
| Colaboración | Individual | Multi-usuario (con auth) |

## 🎨 Personalización

### Cambiar tema de colores

Edita `web/styles.css`:

```css
:root {
    --primary-color: #6366f1;  /* Cambia a tu color */
    --secondary-color: #8b5cf6;
    /* ... más variables ... */
}
```

### Añadir estilos musicales

Edita `web/index.html`, busca `styleInput` y añade más opciones:

```html
<option value="tu-estilo-custom">Tu Estilo Custom</option>
```

## 📄 Licencia

Este proyecto utiliza las siguientes APIs:
- **SunoAPI**: Revisa sus términos de servicio
- **Replicate**: Revisa sus términos de servicio
- **OpenAI**: Revisa sus términos de servicio

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Soporte

Si tienes problemas:

1. Revisa la sección de **Solución de Problemas**
2. Verifica que todas las dependencias estén instaladas
3. Revisa los logs del servidor para mensajes de error

## 🎉 ¡Disfruta generando música con IA!

¡Ahora puedes crear canciones increíbles desde cualquier navegador sin preocuparte por archivos .env o ejecutables!
