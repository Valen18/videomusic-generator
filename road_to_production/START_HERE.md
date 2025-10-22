# 🚀 START HERE - Despliegue en Ubuntu/Dokploy

**Deployment simplificado para tu servidor Linux.**

---

## ⚡ Método Más Simple (Recomendado)

### En tu Servidor Ubuntu:

```bash
# 1. Clonar o transferir proyecto
git clone https://github.com/TU_USUARIO/videomusic-generator.git
cd videomusic-generator/road_to_production

# 2. Configurar variables
cp .env.template .env
nano .env  # Editar con tus API keys

# 3. Deploy automático
chmod +x deploy.sh
./deploy.sh
```

**Acceso:** `http://TU_IP:8000`

---

## 🔑 Configurar .env (OBLIGATORIO)

```env
# Docker Hub (usa una imagen pública o la tuya)
DOCKER_USERNAME=tu-usuario-dockerhub

# API Keys OBLIGATORIAS
SUNO_API_KEY=tu-api-key-suno
SESSION_SECRET_KEY=genera-con-comando-abajo

# Opcionales
REPLICATE_API_TOKEN=tu-token
OPENAI_API_KEY=tu-key
```

**Generar SESSION_SECRET_KEY segura:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 📦 Opciones de Deployment

### Opción 1: Usar Imagen de Docker Hub (Más Rápido)

```bash
# Si ya tienes imagen en Docker Hub
./deploy.sh  # Solo esto!
```

### Opción 2: Build Local en Servidor

```bash
# Build imagen en el servidor
./build.sh   # Construye imagen (tarda ~5 min)
./deploy.sh  # Despliega
```

### Opción 3: Build + Push desde otra máquina

```bash
# En tu PC/Mac (si tienes Docker):
./build.sh   # Construye imagen
./push.sh    # Sube a Docker Hub

# En servidor:
./deploy.sh  # Descarga y despliega
```

---

## 🐳 Con Dokploy (UI Web)

1. **Login**: `http://TU_IP:3000`
2. **Nueva App**: Docker Compose
3. **Pegar**: Contenido de `docker-compose.yml`
4. **Variables**:
   ```env
   DOCKER_USERNAME=tu-user
   SUNO_API_KEY=tu-key
   SESSION_SECRET_KEY=tu-secret
   ```
5. **Deploy** ✅

---

## 🛠️ Comandos Útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Reiniciar
docker-compose restart

# Parar
docker-compose down

# Actualizar a nueva versión
docker-compose pull && docker-compose up -d

# Health check
curl http://localhost:8000/health
```

---

## ✅ Verificar Deployment

```bash
# 1. Estado de contenedores
docker-compose ps

# 2. Health check
curl http://localhost:8000/health
# Debe retornar: {"status":"healthy","version":"1.0"}

# 3. Ver logs
docker-compose logs --tail=50

# 4. Acceder en navegador
# http://TU_IP:8000
```

---

## 🐛 Solución Rápida de Problemas

**Docker no instalado:**
```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
```

**Puerto 8000 ocupado:**
```bash
echo "HOST_PORT=8001" >> .env
docker-compose down && docker-compose up -d
```

**Container no inicia:**
```bash
docker logs videomusic-generator
# Verificar que .env tenga SUNO_API_KEY y SESSION_SECRET_KEY
```

**Permisos denegados:**
```bash
sudo usermod -aG docker $USER
# Logout y login de nuevo
```

---

## 📁 Archivos Incluidos

```
road_to_production/
├── deploy.sh              ← Script completo (USAR ESTE)
├── build.sh               ← Build imagen Docker
├── push.sh                ← Push a Docker Hub
├── Dockerfile             ← Definición imagen
├── docker-compose.yml     ← Orquestación
├── .env.template          ← Variables (copiar a .env)
└── deployment-guide.md    ← Guía completa
```

---

## 🎯 Flujo Recomendado

```
1. Transferir carpeta road_to_production/ al servidor
2. cd road_to_production
3. cp .env.template .env
4. nano .env (agregar API keys)
5. ./deploy.sh
6. Acceder a http://TU_IP:8000
```

**Tiempo total: 5 minutos** ⏱️

---

## 📚 Documentación Completa

- **deployment-guide.md** - Guía detallada completa
- **README.md** - Documentación de la carpeta
- **ESTRUCTURA.txt** - Diagrama visual

---

## ✨ Características

Una vez desplegado tendrás:

✅ Generación de música (Suno)
✅ Imágenes de portada 16:9 (Replicate)
✅ Videos con subtítulos animados (FFmpeg)
✅ Videos en loop con audio
✅ Sistema de usuarios
✅ UI moderna (Tailwind CSS)
✅ Historial con reproductor integrado
✅ Progreso en tiempo real
✅ Almacenamiento persistente
✅ Health checks automáticos
✅ Auto-restart si falla

---

**¿Dudas?** Lee [deployment-guide.md](./deployment-guide.md)

**🎉 ¡A desplegar!**
