# 🚀 VideoMusic Generator - Deployment Guide

Complete guide to deploy VideoMusic Generator using Docker Hub.

## 📋 Prerequisites

- Docker installed ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Hub account ([Sign up](https://hub.docker.com/signup))
- Ubuntu server with Dokploy (or any Docker-compatible environment)
- API Keys (Suno required, Replicate & OpenAI optional)

---

## 🎯 Quick Deployment (3 Steps)

### Step 1: Build & Push to Docker Hub (Local Machine)

```bash
# Navigate to deployment folder
cd road_to_production

# For Linux/Mac:
chmod +x build.sh push.sh
./build.sh
./push.sh

# For Windows:
build.bat
push.bat
```

**What this does:**
- Builds optimized Docker image with FFmpeg
- Tags image as `yourusername/videomusic-generator:latest`
- Pushes to Docker Hub

### Step 2: Configure Environment (Server)

Create `.env` file on your server:

```bash
# On your Ubuntu server
mkdir -p ~/videomusic-generator
cd ~/videomusic-generator

# Create .env file
nano .env
```

Paste this configuration:

```env
# Docker Hub image
DOCKER_USERNAME=your-dockerhub-username
VERSION=latest
HOST_PORT=8000

# Required API Keys
SUNO_API_KEY=your-suno-api-key
SUNO_BASE_URL=https://api.sunoapi.org

# Optional API Keys
REPLICATE_API_TOKEN=your-replicate-token
OPENAI_API_KEY=your-openai-key
OPENAI_ASSISTANT_ID=asst_tR6OL8QLpSsDDlc6hKdBmVNU

# Security (generate new key!)
SESSION_SECRET_KEY=your-secure-random-key-here

# Settings
LOG_LEVEL=info
```

**Generate secure SESSION_SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 3: Deploy with Docker Compose (Server)

```bash
# Download docker-compose.yml
wget https://raw.githubusercontent.com/YOUR_REPO/main/road_to_production/docker-compose.yml

# Or copy from local:
# Upload your docker-compose.yml to the server

# Start the application
docker-compose up -d

# Verify it's running
docker-compose ps
docker-compose logs -f
```

**Access your app:**
- Local: `http://localhost:8000`
- Remote: `http://YOUR_SERVER_IP:8000`

---

## 🐳 Using Dokploy

### Option A: From Docker Hub Image

1. **Login to Dokploy**: `http://YOUR_SERVER_IP:3000`

2. **Create New Application**:
   - Type: **Docker Compose**
   - Name: `videomusic-generator`
   - Source: **Docker Compose File**

3. **Paste docker-compose.yml content**

4. **Set Environment Variables**:
```env
DOCKER_USERNAME=your-dockerhub-username
SUNO_API_KEY=your-suno-key
SESSION_SECRET_KEY=your-secure-key
REPLICATE_API_TOKEN=your-replicate-token
OPENAI_API_KEY=your-openai-key
```

5. **Deploy** ✅

### Option B: From Git Repository

1. Push your code to GitHub/GitLab (including `road_to_production/`)
2. In Dokploy:
   - Type: **Docker Compose**
   - Repository: Your Git URL
   - Compose Path: `road_to_production/docker-compose.yml`
   - Dockerfile Path: `road_to_production/Dockerfile`
3. Set environment variables
4. Deploy ✅

---

## 🔧 Management Commands

### View Logs
```bash
docker-compose logs -f
docker logs videomusic-generator
```

### Restart Application
```bash
docker-compose restart
```

### Stop Application
```bash
docker-compose down
```

### Update to New Version
```bash
# Pull latest image
docker-compose pull

# Restart with new image
docker-compose up -d
```

### Clean Old Images
```bash
docker image prune -a
```

---

## 📊 Verify Deployment

### Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy","version":"1.0"}
```

### Test Web Interface
Open browser: `http://YOUR_SERVER_IP:8000`

### Check Containers
```bash
docker ps
docker stats videomusic-generator
```

---

## 🔒 Security Best Practices

1. **Always change SESSION_SECRET_KEY** - Never use default
2. **Use environment variables** - Never hardcode API keys
3. **Enable firewall** (UFW):
```bash
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```
4. **Use reverse proxy** (Nginx) for HTTPS
5. **Regular updates**: Pull latest image weekly

---

## 📦 Docker Hub Commands

### Pull Image Directly
```bash
docker pull yourusername/videomusic-generator:latest
```

### Run Without Compose
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

---

## 🐛 Troubleshooting

### Container won't start
```bash
# Check logs
docker logs videomusic-generator

# Common issues:
# 1. Missing SUNO_API_KEY or SESSION_SECRET_KEY
# 2. Port 8000 already in use
# 3. Invalid API key format
```

### Port already in use
```bash
# Change HOST_PORT in .env
HOST_PORT=8001

# Restart
docker-compose up -d
```

### Out of disk space
```bash
# Check usage
df -h

# Clean Docker
docker system prune -a --volumes
```

### API Keys not working
```bash
# Test from UI: Click "Configuración" → "Validar Conectividad"
# Or check logs:
docker logs videomusic-generator | grep -i "error"
```

---

## 🌐 Domain & SSL Setup

### With Nginx Reverse Proxy

1. Install Nginx:
```bash
sudo apt install nginx
```

2. Create config:
```bash
sudo nano /etc/nginx/sites-available/videomusic
```

```nginx
server {
    listen 80;
    server_name videomusic.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

3. Enable & get SSL:
```bash
sudo ln -s /etc/nginx/sites-available/videomusic /etc/nginx/sites-enabled/
sudo systemctl restart nginx

# Install Certbot for SSL
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d videomusic.yourdomain.com
```

---

## 📈 Performance Tips

1. **Increase Docker resources** if generating many videos
2. **Use SSD storage** for output volume
3. **Monitor disk usage** - videos can be large
4. **Set up log rotation**:
```bash
docker run --log-driver json-file --log-opt max-size=10m --log-opt max-file=3
```

---

## ✅ Success Checklist

- [ ] Docker image built and pushed to Docker Hub
- [ ] `.env` file created with all required keys
- [ ] `docker-compose up -d` runs successfully
- [ ] Health check returns `{"status":"healthy"}`
- [ ] Web interface loads at `http://SERVER_IP:8000`
- [ ] Can login and access dashboard
- [ ] API connectivity validation passes
- [ ] Successfully generated a test song
- [ ] Files persist after container restart

---

## 🎉 You're Done!

Your VideoMusic Generator is now running in production with:
- ✅ FFmpeg for video processing
- ✅ Persistent storage for data and outputs
- ✅ Health monitoring
- ✅ Auto-restart on failure
- ✅ Easy updates from Docker Hub
- ✅ Professional web interface with Tailwind CSS

**Support:** Check logs first, then review this guide.
