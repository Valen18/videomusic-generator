# 🚀 Guía de Despliegue en Dokploy (Ubuntu)

Esta guía te ayudará a desplegar VideoMusic Generator en tu servidor Ubuntu con Dokploy instalado.

## 📋 Requisitos Previos

- ✅ Servidor Ubuntu con Dokploy instalado
- ✅ Git instalado en el servidor
- ✅ Dominio o subdominio configurado (opcional pero recomendado)
- ✅ API Keys de los servicios (ver sección de configuración)

## 🔑 API Keys Necesarias

### Obligatorias
- **Suno API Key**: Para generar música
  - Obtener en: https://www.suno.ai/

### Opcionales
- **Replicate API Token**: Para generar imágenes y videos
  - Obtener en: https://replicate.com/
- **OpenAI API Key**: Para generar letras con IA
  - Obtener en: https://platform.openai.com/

## 📦 Paso 1: Preparar el Repositorio

### Opción A: Subir a GitHub/GitLab (Recomendado)

1. Crea un repositorio en GitHub o GitLab
2. Inicializa git en tu proyecto local:

```bash
cd d:\Test\videomusic-generator
git init
git add .
git commit -m "Initial commit - VideoMusic Generator"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/videomusic-generator.git
git push -u origin main
```

### Opción B: Transferir archivos directamente al servidor

```bash
# Desde tu máquina local
scp -r d:\Test\videomusic-generator root@TU_SERVIDOR_IP:/opt/videomusic-generator
```

## 🐳 Paso 2: Configurar Dokploy

### 2.1 Acceder a Dokploy

1. Abre tu navegador y ve a: `http://TU_SERVIDOR_IP:3000`
2. Inicia sesión con tus credenciales de Dokploy

### 2.2 Crear una Nueva Aplicación

1. Click en **"Create Application"** o **"Nueva Aplicación"**
2. Selecciona **"Docker Compose"** como tipo de aplicación
3. Configuración básica:
   - **Name**: `videomusic-generator`
   - **Repository**: URL de tu repositorio Git (si usaste Opción A)
   - **Branch**: `main`

### 2.3 Configurar Variables de Entorno

En la sección de **Environment Variables**, añade las siguientes:

```env
# ===== OBLIGATORIAS =====
SUNO_API_KEY=tu-api-key-de-suno-aqui
SUNO_BASE_URL=https://api.sunoapi.org

# ===== OPCIONALES =====
REPLICATE_API_TOKEN=tu-token-de-replicate-aqui
OPENAI_API_KEY=tu-api-key-de-openai-aqui
OPENAI_ASSISTANT_ID=asst_tR6OL8QLpSsDDlc6hKdBmVNU

# ===== SEGURIDAD (IMPORTANTE) =====
SESSION_SECRET_KEY=genera-una-clave-secreta-aleatoria-de-32-caracteres-minimo
```

**⚠️ IMPORTANTE:** Genera una clave secreta segura para `SESSION_SECRET_KEY`:

```bash
# En tu servidor Ubuntu, ejecuta:
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2.4 Configurar Puerto y Dominio

1. **Puerto**: `8000` (ya configurado en docker-compose.yml)
2. **Dominio** (opcional):
   - Si tienes un dominio: `videomusic.tudominio.com`
   - Dokploy configurará automáticamente SSL con Let's Encrypt

### 2.5 Configurar Volúmenes (Persistencia de Datos)

Dokploy detectará automáticamente los volúmenes del `docker-compose.yml`:
- `./data` → Datos de usuarios y sesiones
- `./output` → Videos, audios e imágenes generadas

Estos datos persistirán incluso si reinicias el contenedor.

## 🚀 Paso 3: Desplegar

1. Click en **"Deploy"** o **"Desplegar"**
2. Dokploy comenzará a:
   - Clonar el repositorio
   - Construir la imagen Docker
   - Instalar FFmpeg y dependencias
   - Iniciar el contenedor

3. El proceso tardará 2-5 minutos la primera vez

### Monitorear el Despliegue

Ve a la pestaña **"Logs"** para ver el progreso en tiempo real:

```
Building videomusic-generator...
Installing dependencies...
Starting application...
INFO:     Uvicorn running on http://0.0.0.0:8000
✅ Application ready!
```

## ✅ Paso 4: Verificar el Despliegue

### 4.1 Comprobar Estado de Salud

```bash
# Desde tu servidor Ubuntu
curl http://localhost:8000/health
```

Deberías ver:
```json
{"status":"healthy","version":"1.0"}
```

### 4.2 Acceder a la Aplicación

- **Con dominio**: `https://videomusic.tudominio.com`
- **Sin dominio**: `http://TU_SERVIDOR_IP:8000`

## 🔧 Gestión Post-Despliegue

### Ver Logs

En Dokploy, ve a la pestaña **"Logs"** para monitorear la aplicación en tiempo real.

### Reiniciar la Aplicación

```bash
# Opción 1: Desde Dokploy UI
Click en "Restart" en la interfaz

# Opción 2: Desde terminal SSH
cd /opt/dokploy/apps/videomusic-generator
docker-compose restart
```

### Actualizar la Aplicación

```bash
# Opción 1: Desde Dokploy UI
Click en "Rebuild & Deploy"

# Opción 2: Desde terminal SSH
cd /opt/dokploy/apps/videomusic-generator
git pull origin main
docker-compose down
docker-compose up -d --build
```

### Ver Contenido Generado

```bash
# SSH al servidor
ssh root@TU_SERVIDOR_IP

# Ver archivos generados
cd /opt/dokploy/apps/videomusic-generator/output
ls -lah
```

## 🔒 Seguridad

### Configurar Firewall (UFW)

```bash
# Permitir SSH
sudo ufw allow 22/tcp

# Permitir HTTP/HTTPS para Dokploy
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Permitir puerto de Dokploy
sudo ufw allow 3000/tcp

# Activar firewall
sudo ufw enable
```

### SSL/HTTPS (Recomendado)

Si configuraste un dominio en Dokploy:
1. Dokploy automáticamente configurará Let's Encrypt
2. Tu aplicación estará disponible en `https://`

## 📊 Monitoreo

### Ver Uso de Recursos

```bash
# CPU y memoria del contenedor
docker stats videomusic-generator

# Espacio en disco usado
du -sh /opt/dokploy/apps/videomusic-generator/output
```

### Limpiar Archivos Antiguos (Opcional)

```bash
# Eliminar archivos generados hace más de 30 días
find /opt/dokploy/apps/videomusic-generator/output -type f -mtime +30 -delete
```

## 🐛 Troubleshooting

### El contenedor no inicia

```bash
# Ver logs completos
docker logs videomusic-generator

# Verificar configuración
docker-compose config
```

### Error "FFmpeg not found"

El Dockerfile ya incluye FFmpeg, pero si hay problemas:

```bash
# Entrar al contenedor
docker exec -it videomusic-generator bash

# Verificar FFmpeg
ffmpeg -version
```

### Problemas con API Keys

1. Verifica que las variables de entorno estén configuradas correctamente en Dokploy
2. Prueba las APIs desde la interfaz web: Click en "⚙️ Configuración" → "🔍 Validar Conectividad"

### Puerto 8000 ocupado

```bash
# Ver qué está usando el puerto
sudo lsof -i :8000

# Cambiar puerto en docker-compose.yml (si es necesario)
ports:
  - "8001:8000"  # Cambiar 8000 por otro puerto
```

## 📚 Recursos Adicionales

- **Documentación de Dokploy**: https://docs.dokploy.com
- **Suno API Docs**: https://docs.suno.ai
- **Replicate API Docs**: https://replicate.com/docs
- **FFmpeg Documentation**: https://ffmpeg.org/documentation.html

## ✨ Características en Producción

Una vez desplegado, tendrás:

- ✅ Generación de música con Suno
- ✅ Generación de imágenes con Replicate
- ✅ Generación de videos con subtítulos animados
- ✅ Sistema de usuarios y sesiones
- ✅ Historial persistente con audio/video integrados
- ✅ WebSocket para progreso en tiempo real
- ✅ Auto-restart si la aplicación falla
- ✅ Health checks automáticos
- ✅ Volúmenes persistentes para datos

## 🎉 ¡Listo!

Tu aplicación VideoMusic Generator ahora está corriendo en producción con Dokploy.

**URL de acceso**: `https://tudominio.com` o `http://TU_IP:8000`

---

**Notas finales:**
- Los archivos generados se guardan en el servidor, no consumen espacio local
- Puedes escalar horizontalmente con múltiples instancias si es necesario
- Dokploy maneja automáticamente los reinicios y actualizaciones
- El health check verifica que la app esté funcionando cada 30 segundos
