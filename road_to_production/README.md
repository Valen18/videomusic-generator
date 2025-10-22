# 🚀 Road to Production - VideoMusic Generator

**Everything you need to deploy VideoMusic Generator to production.**

This folder contains all deployment files and scripts for running VideoMusic Generator in Docker, including building and pushing to Docker Hub for easy deployment on any server.

---

## 📦 What's Included

```
road_to_production/
├── README.md                  ← You are here
├── deployment-guide.md        ← Complete deployment guide
├── Dockerfile                 ← Optimized production image
├── docker-compose.yml         ← Complete orchestration setup
├── .dockerignore              ← Build optimization
├── .env.template              ← Environment variables template
├── build.sh / build.bat       ← Build Docker image scripts
└── push.sh / push.bat         ← Push to Docker Hub scripts
```

---

## 🎯 Quick Start (3 Commands)

### 1. Build Docker Image

**Linux/Mac:**
```bash
cd road_to_production
chmod +x build.sh push.sh
./build.sh
```

**Windows:**
```bash
cd road_to_production
build.bat
```

### 2. Push to Docker Hub

**Linux/Mac:**
```bash
./push.sh
```

**Windows:**
```bash
push.bat
```

### 3. Deploy on Server

```bash
# On your Ubuntu server
docker pull yourusername/videomusic-generator:latest
docker-compose up -d
```

---

## 🐳 Docker Hub Deployment

### Why Docker Hub?

✅ **Single source of truth** - One image for all environments
✅ **Easy updates** - Just pull latest image
✅ **Version control** - Tag different versions
✅ **Portable** - Deploy anywhere Docker runs
✅ **No build time on server** - Ready to run

### Image Details

- **Base**: Python 3.11 slim
- **Includes**: FFmpeg, all Python dependencies
- **Size**: ~800MB (optimized)
- **User**: Non-root for security
- **Health Check**: Built-in

---

## 📋 Prerequisites

### Local Machine (for building)
- Docker installed
- Docker Hub account
- This repository

### Production Server
- Ubuntu 20.04+ (or any Linux with Docker)
- Docker & Docker Compose installed
- Open port 8000 (or custom)
- API Keys:
  - **Required**: Suno API Key
  - **Optional**: Replicate, OpenAI

---

## 🔑 Environment Variables

Copy `.env.template` to `.env` and configure:

```env
# Docker Hub
DOCKER_USERNAME=your-dockerhub-username
VERSION=latest

# API Keys (REQUIRED)
SUNO_API_KEY=your-suno-api-key
SESSION_SECRET_KEY=generate-secure-key

# Optional
REPLICATE_API_TOKEN=your-replicate-token
OPENAI_API_KEY=your-openai-key
```

**Generate SESSION_SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🚀 Deployment Options

### Option 1: Docker Compose (Recommended)

```bash
# 1. Create .env file with your keys
# 2. Download or copy docker-compose.yml
# 3. Run:
docker-compose up -d
```

### Option 2: Docker Run

```bash
docker run -d \
  --name videomusic-generator \
  -p 8000:8000 \
  -e SUNO_API_KEY=your-key \
  -e SESSION_SECRET_KEY=your-secret \
  -v videomusic-data:/app/data \
  -v videomusic-output:/app/output \
  yourusername/videomusic-generator:latest
```

### Option 3: Dokploy

1. Login to Dokploy UI
2. Create new application (Docker Compose)
3. Paste `docker-compose.yml` content
4. Set environment variables
5. Deploy ✅

---

## 🔧 Build Scripts Reference

### build.sh / build.bat

Builds the Docker image with proper tags.

**Environment Variables:**
- `DOCKER_USERNAME` - Your Docker Hub username
- `VERSION` - Image version (default: latest)

**Example:**
```bash
DOCKER_USERNAME=myuser VERSION=v1.0.0 ./build.sh
```

### push.sh / push.bat

Pushes built image to Docker Hub.

**Requires:** Docker Hub login (`docker login`)

**Pushes:**
- `yourusername/videomusic-generator:VERSION`
- `yourusername/videomusic-generator:latest` (if VERSION != latest)

---

## 📊 Verify Deployment

### Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","version":"1.0"}
```

### Container Status
```bash
docker ps
docker logs videomusic-generator
```

### Web Interface
Open: `http://YOUR_SERVER_IP:8000`

---

## 🔄 Update Process

### Update from Docker Hub

```bash
# Pull latest
docker-compose pull

# Restart with new image
docker-compose up -d

# Verify
docker-compose logs -f
```

### Build & Push New Version

```bash
# Local machine
cd road_to_production
VERSION=v1.1.0 ./build.sh
VERSION=v1.1.0 ./push.sh

# Server
docker-compose pull
docker-compose up -d
```

---

## 📚 Documentation

- **[deployment-guide.md](./deployment-guide.md)** - Complete deployment guide
- **[Dockerfile](./Dockerfile)** - Image build configuration
- **[docker-compose.yml](./docker-compose.yml)** - Orchestration setup

---

## 🐛 Common Issues

### Build fails
```bash
# Ensure you're in project root when building
cd path/to/videomusic-generator
./road_to_production/build.sh
```

### Push fails - Not logged in
```bash
docker login
# Enter Docker Hub credentials
```

### Container won't start - Missing API key
```bash
# Check .env file has SUNO_API_KEY and SESSION_SECRET_KEY
cat .env
```

### Port 8000 in use
```bash
# Change HOST_PORT in .env
echo "HOST_PORT=8001" >> .env
docker-compose up -d
```

---

## ✨ Features

Your deployed application includes:

✅ **Music Generation** - Suno AI integration
✅ **Image Generation** - Replicate (16:9 covers)
✅ **Video Generation** - With animated subtitles
✅ **Video Loops** - Audio-synced looping
✅ **User System** - Authentication & sessions
✅ **Beautiful UI** - Tailwind CSS, Spotify-style
✅ **Real-time Progress** - WebSocket updates
✅ **Persistent Storage** - Docker volumes
✅ **Health Monitoring** - Auto-restart on failure

---

## 🎯 Production Checklist

- [ ] Built Docker image locally
- [ ] Pushed to Docker Hub successfully
- [ ] Created `.env` on server with all keys
- [ ] Changed `SESSION_SECRET_KEY` to secure value
- [ ] Ran `docker-compose up -d`
- [ ] Health check returns healthy
- [ ] Web UI loads and is accessible
- [ ] Can login to application
- [ ] API connectivity validation passes
- [ ] Generated test song successfully
- [ ] Set up domain & SSL (optional)
- [ ] Configured firewall rules
- [ ] Set up backup for volumes (optional)

---

## 🆘 Support

1. **Check logs first:**
   ```bash
   docker logs videomusic-generator
   docker-compose logs
   ```

2. **Review documentation:**
   - [deployment-guide.md](./deployment-guide.md)

3. **Common solutions:**
   - Restart: `docker-compose restart`
   - Rebuild: `docker-compose up -d --build`
   - Clean start: `docker-compose down && docker-compose up -d`

---

## 🎉 You're Ready!

Everything is set up for a smooth deployment to production.

**Next steps:**
1. Run `./build.sh` (or `build.bat` on Windows)
2. Run `./push.sh` (or `push.bat` on Windows)
3. Deploy on your server using `docker-compose up -d`

**Questions?** Check [deployment-guide.md](./deployment-guide.md) for detailed instructions.

---

**Made with ❤️ for production deployments**
