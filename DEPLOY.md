# 🚀 Guía de Despliegue - VideoMusic Generator

Esta guía te muestra **todas las opciones** para desplegar la aplicación web, desde servidores locales hasta cloud hosting.

## 📋 Tabla de Contenidos

1. [Versión Python (FastAPI)](#versión-python-fastapi)
   - [Servidor local](#servidor-local)
   - [VPS / Cloud (DigitalOcean, AWS, etc.)](#vps--cloud)
   - [Heroku](#heroku)
   - [Render](#render)
   - [Railway](#railway)
   - [Docker](#docker)
2. [Requisitos del servidor](#requisitos-del-servidor)
3. [Configuración de producción](#configuración-de-producción)
4. [Preguntas frecuentes](#preguntas-frecuentes)

---

## Versión Python (FastAPI)

### Servidor Local

**Para desarrollo o uso personal:**

```bash
# 1. Instalar dependencias
pip install -r requirements-web.txt

# 2. Ejecutar la aplicación
python web_app_secure.py
```

La aplicación estará disponible en: `http://localhost:8000`

**Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: `admin123`

⚠️ **IMPORTANTE:** Cambia la contraseña inmediatamente después del primer inicio de sesión.

---

### VPS / Cloud (DigitalOcean, AWS, Linode, etc.)

**1. Preparar el servidor**

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python 3.10+ y pip
sudo apt install python3.10 python3-pip -y

# Instalar nginx (opcional, recomendado)
sudo apt install nginx -y
```

**2. Subir código al servidor**

```bash
# Opción A: Clonar desde Git
git clone https://github.com/tu-usuario/videomusic-generator.git
cd videomusic-generator

# Opción B: Subir con SCP/SFTP
scp -r /ruta/local usuario@tu-servidor:/home/usuario/videomusic-generator
```

**3. Instalar dependencias**

```bash
cd videomusic-generator
pip3 install -r requirements-web.txt
```

**4. Configurar como servicio (systemd)**

Crear archivo `/etc/systemd/system/videomusic.service`:

```ini
[Unit]
Description=VideoMusic Generator Web Application
After=network.target

[Service]
Type=simple
User=tu-usuario
WorkingDirectory=/home/tu-usuario/videomusic-generator
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 web_app_secure.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**5. Iniciar servicio**

```bash
sudo systemctl enable videomusic
sudo systemctl start videomusic
sudo systemctl status videomusic
```

**6. Configurar Nginx (recomendado)**

Crear archivo `/etc/nginx/sites-available/videomusic`:

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Activar sitio:

```bash
sudo ln -s /etc/nginx/sites-available/videomusic /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

**7. SSL con Let's Encrypt (recomendado)**

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d tu-dominio.com
```

---

### Heroku

**1. Crear archivos de configuración**

`Procfile`:
```
web: uvicorn web_app_secure:app --host 0.0.0.0 --port $PORT
```

`runtime.txt`:
```
python-3.10.12
```

**2. Desplegar**

```bash
# Login en Heroku
heroku login

# Crear app
heroku create tu-app-videomusic

# Push código
git push heroku main

# Ver logs
heroku logs --tail
```

**3. Abrir app**

```bash
heroku open
```

---

### Render

**1. Conectar repositorio**
- Ve a [render.com](https://render.com)
- Clic en "New +" → "Web Service"
- Conecta tu repositorio de GitHub/GitLab

**2. Configuración**
- **Name:** videomusic-generator
- **Environment:** Python 3
- **Build Command:** `pip install -r requirements-web.txt`
- **Start Command:** `uvicorn web_app_secure:app --host 0.0.0.0 --port $PORT`
- **Plan:** Free (o el que prefieras)

**3. Deploy**
- Clic en "Create Web Service"
- Espera a que se despliegue
- Accede a la URL proporcionada

**Ventajas de Render:**
- ✅ SSL gratuito
- ✅ Auto-deploy desde Git
- ✅ Logs en tiempo real
- ✅ Plan gratuito disponible

---

### Railway

**1. Instalar Railway CLI**

```bash
npm install -g @railway/cli
# O descargar desde: https://railway.app/cli
```

**2. Login**

```bash
railway login
```

**3. Inicializar proyecto**

```bash
cd videomusic-generator
railway init
```

**4. Desplegar**

```bash
railway up
```

**5. Abrir aplicación**

```bash
railway open
```

**Configuración automática:**
Railway detecta automáticamente Python y ejecuta el comando correcto.

---

### Docker

**1. Crear `Dockerfile`**

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar
COPY requirements-web.txt .
RUN pip install --no-cache-dir -r requirements-web.txt

# Copiar código
COPY . .

# Crear directorio de salida
RUN mkdir -p output

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["python", "web_app_secure.py"]
```

**2. Crear `docker-compose.yml` (opcional)**

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./output:/app/output
      - ./videomusic.db:/app/videomusic.db
    environment:
      - PORT=8000
    restart: always
```

**3. Construir y ejecutar**

```bash
# Opción A: Docker solo
docker build -t videomusic-generator .
docker run -p 8000:8000 -v $(pwd)/output:/app/output videomusic-generator

# Opción B: Docker Compose
docker-compose up -d
```

**4. Ver logs**

```bash
docker-compose logs -f
```

---

## Requisitos del Servidor

### Mínimos (para uso personal)
- **CPU:** 1 core
- **RAM:** 512 MB
- **Disco:** 5 GB
- **Ancho de banda:** 100 GB/mes

### Recomendados (para producción)
- **CPU:** 2+ cores
- **RAM:** 2+ GB
- **Disco:** 20+ GB (para almacenar archivos generados)
- **Ancho de banda:** 500+ GB/mes

### Software requerido
- **Python:** 3.10 o superior
- **pip:** Gestor de paquetes de Python
- **FFmpeg:** Para procesamiento de video (opcional pero recomendado)

---

## Configuración de Producción

### Variables de Entorno (Opcional)

Puedes preconfigurar API keys mediante variables de entorno:

```bash
export SUNO_API_KEY="tu-key"
export REPLICATE_API_TOKEN="tu-token"
export OPENAI_API_KEY="tu-key"
```

### Seguridad

**1. Cambiar contraseña por defecto**
- Inicia sesión con `admin/admin123`
- Cambia la contraseña inmediatamente

**2. Configurar HTTPS**
- En producción, SIEMPRE usa HTTPS
- Usa Let's Encrypt para SSL gratuito
- O configura un certificado SSL propio

**3. Limitar acceso**

En `web_app_secure.py`, modifica CORS:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tu-dominio.com"],  # Específico
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

**4. Base de datos**
- Por defecto usa SQLite (`videomusic.db`)
- Para producción, considera PostgreSQL o MySQL
- Haz backups regulares de la base de datos

### Monitoreo

**Ver logs en tiempo real:**

```bash
# systemd
sudo journalctl -u videomusic -f

# Docker
docker logs -f container_name

# Heroku
heroku logs --tail

# Render/Railway
Ver en el dashboard web
```

---

## Preguntas Frecuentes

### ¿Puedo usar un hosting compartido tradicional?

No directamente. Los hostings compartidos (como cPanel) no soportan aplicaciones Python/FastAPI. Necesitas:
- Un VPS
- O servicios cloud como Render, Railway, Heroku

**Alternativa:** La versión PHP que incluyo sí funciona en hosting compartido.

### ¿Cuánto cuesta el despliegue?

**Opciones gratuitas:**
- Render (con límites)
- Railway ($5 de crédito gratis/mes)
- Heroku (plan gratuito limitado)

**Opciones de pago:**
- DigitalOcean: desde $6/mes (VPS básico)
- AWS Lightsail: desde $3.50/mes
- Linode: desde $5/mes

### ¿Qué pasa con los archivos generados?

Los archivos se guardan en la carpeta `output/user_{id}/`. En producción:

**Opción 1:** Almacenamiento local
- Asegúrate de tener suficiente disco
- Monta un volumen persistente (Docker)

**Opción 2:** Cloud Storage
- AWS S3
- Google Cloud Storage
- Cloudinary
- (Requiere modificar código)

### ¿Necesito FFmpeg?

Sí, para generar videos necesitas FFmpeg instalado en el servidor:

```bash
# Ubuntu/Debian
sudo apt install ffmpeg -y

# CentOS/RHEL
sudo yum install ffmpeg -y

# macOS
brew install ffmpeg

# Docker
Ya incluido en el Dockerfile
```

### ¿Cómo hago backup?

**Backup de la base de datos:**
```bash
cp videomusic.db videomusic.db.backup
```

**Backup de archivos generados:**
```bash
tar -czf output_backup.tar.gz output/
```

**Automatizar backups (cron):**
```bash
# Editar crontab
crontab -e

# Añadir línea (backup diario a las 3 AM)
0 3 * * * /home/usuario/backup.sh
```

### ¿Puedo usar múltiples usuarios?

Sí, la versión segura (`web_app_secure.py`) incluye:
- Sistema de autenticación
- Múltiples usuarios
- Sesiones aisladas por usuario
- API keys individuales por usuario

### ¿Cómo actualizo la aplicación?

```bash
# Detener servicio
sudo systemctl stop videomusic

# Actualizar código
git pull origin main

# Instalar nuevas dependencias (si hay)
pip install -r requirements-web.txt

# Reiniciar servicio
sudo systemctl start videomusic
```

---

## 🆘 Soporte

Si tienes problemas:

1. **Revisa los logs** de la aplicación
2. **Verifica que todas las dependencias** estén instaladas
3. **Comprueba los puertos** (8000 debe estar abierto)
4. **Revisa el firewall** del servidor

---

## 🎉 ¡Listo!

Tu aplicación VideoMusic Generator debería estar corriendo. Accede a ella y empieza a generar música con IA.

**Siguiente paso:** Configura tus API keys en la sección de Configuración de la aplicación.
