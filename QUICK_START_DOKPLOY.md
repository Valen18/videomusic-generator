# 🚀 Quick Start - Despliegue en Dokploy

Guía rápida para desplegar VideoMusic Generator en tu servidor Ubuntu con Dokploy.

## 📦 Paso 1: Subir el Código

### Opción A: GitHub (Recomendado)

```bash
cd d:\Test\videomusic-generator
git init
git add .
git commit -m "VideoMusic Generator - Ready for deployment"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/videomusic-generator.git
git push -u origin main
```

### Opción B: GitLab

Igual que GitHub, pero usa tu URL de GitLab.

## 🐳 Paso 2: Configurar en Dokploy

1. **Accede a Dokploy**: `http://TU_SERVIDOR_IP:3000`

2. **Crear Nueva Aplicación**:
   - Type: **Docker Compose**
   - Name: `videomusic-generator`
   - Repository: URL de tu repositorio Git
   - Branch: `main`

3. **Variables de Entorno** (obligatorias):

```env
SUNO_API_KEY=tu-api-key-aqui
SUNO_BASE_URL=https://api.sunoapi.org
SESSION_SECRET_KEY=genera-clave-secreta-con-comando-abajo
```

**Generar clave secreta** (desde el servidor):
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

4. **Variables Opcionales**:

```env
REPLICATE_API_TOKEN=tu-token-aqui
OPENAI_API_KEY=tu-api-key-aqui
OPENAI_ASSISTANT_ID=asst_tR6OL8QLpSsDDlc6hKdBmVNU
```

5. **Configurar Puerto**: `8000` (ya configurado)

6. **Configurar Dominio** (opcional):
   - Añade tu dominio: `videomusic.tudominio.com`
   - Dokploy configurará SSL automáticamente

7. **Click en "Deploy"** ✅

## ✅ Paso 3: Verificar

Espera 3-5 minutos y verifica:

```bash
curl http://localhost:8000/health
```

Deberías ver: `{"status":"healthy","version":"1.0"}`

## 🌐 Acceder

- **Con dominio**: `https://videomusic.tudominio.com`
- **Sin dominio**: `http://TU_IP:8000`

## 📚 Documentación Completa

Ver [DEPLOYMENT_DOKPLOY.md](./DEPLOYMENT_DOKPLOY.md) para más detalles.

## 🔧 Comandos Útiles

### Ver Logs
```bash
docker logs -f videomusic-generator
```

### Reiniciar
```bash
docker-compose restart
```

### Actualizar
```bash
git pull origin main
docker-compose up -d --build
```

## ⚠️ Importante

- ✅ El puerto 8000 debe estar disponible
- ✅ Genera una SESSION_SECRET_KEY única y segura
- ✅ Los archivos se guardan en volúmenes persistentes
- ✅ FFmpeg viene incluido en la imagen Docker

## 🎉 ¡Listo!

Tu aplicación estará corriendo en minutos. Todo está configurado para funcionar en producción sin cambios adicionales.
