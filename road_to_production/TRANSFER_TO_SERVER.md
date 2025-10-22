# 📤 Cómo Transferir al Servidor

Hay 3 formas de llevar `road_to_production` a tu servidor Ubuntu.

---

## ✅ Opción 1: GitHub (RECOMENDADO)

### Paso 1: Subir a GitHub

**Desde tu PC Windows:**

```powershell
cd D:\Test\videomusic-generator

# Inicializar git (si no lo has hecho)
git init
git add .
git commit -m "VideoMusic Generator - Production Ready"

# Subir a GitHub
git branch -M main
git remote add origin https://github.com/TU_USUARIO/videomusic-generator.git
git push -u origin main
```

### Paso 2: Clonar en Servidor

**Desde tu servidor Ubuntu:**

```bash
# SSH al servidor
ssh root@158.220.94.179

# Clonar repositorio
git clone https://github.com/TU_USUARIO/videomusic-generator.git
cd videomusic-generator/road_to_production

# Configurar y desplegar
cp .env.example .env
nano .env  # Agregar tus API keys
chmod +x *.sh
./deploy.sh
```

---

## ⚡ Opción 2: SCP desde Windows PowerShell

**Desde PowerShell en Windows:**

```powershell
# Navegar al proyecto
cd D:\Test\videomusic-generator

# Transferir carpeta (ruta absoluta)
scp -r "D:\Test\videomusic-generator\road_to_production" root@158.220.94.179:~/

# Transferir solo archivos esenciales (más rápido)
scp road_to_production/deploy.sh root@158.220.94.179:~/
scp road_to_production/docker-compose.yml root@158.220.94.179:~/
scp road_to_production/.env.example root@158.220.94.179:~/
```

**Luego en el servidor:**

```bash
ssh root@158.220.94.179

# Configurar
cp .env.example .env
nano .env  # Agregar API keys
chmod +x deploy.sh

# Desplegar
./deploy.sh
```

---

## 🗜️ Opción 3: Crear ZIP y Subir

### En Windows:

1. **Comprimir carpeta:**
   - Botón derecho en `road_to_production`
   - "Enviar a" → "Carpeta comprimida"
   - Se crea `road_to_production.zip`

2. **Subir con WinSCP o FileZilla:**
   - Host: `158.220.94.179`
   - Usuario: `root`
   - Contraseña: tu contraseña
   - Subir `road_to_production.zip` a `/root/`

### En el Servidor:

```bash
ssh root@158.220.94.179

# Descomprimir
apt install unzip -y
unzip road_to_production.zip
cd road_to_production

# Configurar y desplegar
cp .env.example .env
nano .env
chmod +x *.sh
./deploy.sh
```

---

## 🎯 Método Rápido SOLO Archivos Esenciales

Si quieres ir súper rápido, solo necesitas estos archivos:

**Crear manualmente en el servidor:**

```bash
ssh root@158.220.94.179

# Crear directorio
mkdir -p ~/videomusic
cd ~/videomusic

# Crear docker-compose.yml
nano docker-compose.yml
```

**Pegar este contenido:**

```yaml
version: '3.8'

services:
  videomusic-generator:
    image: ${DOCKER_USERNAME:-yourusername}/videomusic-generator:latest
    container_name: videomusic-generator
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - videomusic-data:/app/data
      - videomusic-output:/app/output
    environment:
      - SUNO_API_KEY=${SUNO_API_KEY}
      - SUNO_BASE_URL=https://api.sunoapi.org
      - SESSION_SECRET_KEY=${SESSION_SECRET_KEY}
      - REPLICATE_API_TOKEN=${REPLICATE_API_TOKEN:-}
      - OPENAI_API_KEY=${OPENAI_API_KEY:-}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

volumes:
  videomusic-data:
  videomusic-output:
```

**Crear .env:**

```bash
nano .env
```

**Pegar:**

```env
DOCKER_USERNAME=yourusername
SUNO_API_KEY=tu-api-key-aqui
SESSION_SECRET_KEY=genera-con-python
```

**Generar SECRET_KEY y desplegar:**

```bash
# Generar clave
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Copiar resultado y agregarlo a .env

# Desplegar
docker-compose up -d

# Verificar
curl http://localhost:8000/health
```

---

## 🚀 Mi Recomendación

**USA GITHUB (Opción 1)** porque:

✅ Más profesional
✅ Control de versiones
✅ Fácil actualizar después (git pull)
✅ No necesitas transferir archivos manualmente
✅ Puedes usar desde cualquier servidor
✅ Otros pueden colaborar

---

## 📝 Comandos Completos para GitHub

**En Windows (PowerShell):**

```powershell
cd D:\Test\videomusic-generator
git init
git add .
git commit -m "Production ready"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/videomusic-generator.git
git push -u origin main
```

**En Servidor Ubuntu:**

```bash
ssh root@158.220.94.179
git clone https://github.com/TU_USUARIO/videomusic-generator.git
cd videomusic-generator/road_to_production
cp .env.example .env
nano .env  # Configurar API keys
chmod +x deploy.sh
./deploy.sh
```

**Listo en 5 minutos!** 🎉

---

## ❓ Si No Tienes GitHub

1. Crea cuenta gratis: https://github.com/signup
2. Crea repositorio: https://github.com/new
3. Sigue los comandos de arriba

O usa **Opción 3 (ZIP)** que es la más simple sin GitHub.
