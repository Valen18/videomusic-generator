#!/bin/bash
# Deploy VideoMusic Generator on Linux Server
# This script sets up the application as a systemd service

echo "🎵 VideoMusic Generator - Deployment Script"
echo "============================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  Este script debe ejecutarse con sudo para configurar el servicio systemd"
    echo "Uso: sudo bash deploy_linux.sh"
    exit 1
fi

# Get the current directory
CURRENT_DIR=$(pwd)
USER_NAME=$(logname)

echo "📂 Directorio de instalación: $CURRENT_DIR"
echo "👤 Usuario: $USER_NAME"
echo ""

# Install system dependencies
echo "📦 Instalando dependencias del sistema..."
apt-get update
apt-get install -y python3 python3-pip python3-venv nginx

# Create virtual environment as the user
echo "🔧 Configurando entorno virtual..."
sudo -u $USER_NAME python3 -m venv venv
sudo -u $USER_NAME venv/bin/pip install --upgrade pip
sudo -u $USER_NAME venv/bin/pip install -r requirements.txt

# Create output directory
mkdir -p output
chown -R $USER_NAME:$USER_NAME output

# Create systemd service file
echo "⚙️  Creando servicio systemd..."
cat > /etc/systemd/system/videomusic-generator.service << EOF
[Unit]
Description=VideoMusic Generator Web Application
After=network.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$CURRENT_DIR
Environment="PATH=$CURRENT_DIR/venv/bin"
ExecStart=$CURRENT_DIR/venv/bin/python web_app_secure.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create nginx configuration
echo "🌐 Configurando nginx como proxy reverso..."
cat > /etc/nginx/sites-available/videomusic-generator << EOF
server {
    listen 80;
    server_name _;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    location /ws {
        proxy_pass http://127.0.0.1:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF

# Enable nginx site
ln -sf /etc/nginx/sites-available/videomusic-generator /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
echo "🔍 Verificando configuración de nginx..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Configuración de nginx correcta"
else
    echo "❌ Error en la configuración de nginx"
    exit 1
fi

# Reload systemd and start services
echo "🚀 Iniciando servicios..."
systemctl daemon-reload
systemctl enable videomusic-generator
systemctl start videomusic-generator
systemctl restart nginx

# Check service status
sleep 2
if systemctl is-active --quiet videomusic-generator; then
    echo "✅ Servicio VideoMusic Generator iniciado correctamente"
else
    echo "❌ Error al iniciar el servicio"
    echo "Ver logs con: journalctl -u videomusic-generator -f"
    exit 1
fi

echo ""
echo "✅ ¡Despliegue completado!"
echo ""
echo "🌐 La aplicación está disponible en: http://$(hostname -I | awk '{print $1}')"
echo "👤 Credenciales por defecto: admin / admin123"
echo "⚠️  CAMBIA LA CONTRASEÑA INMEDIATAMENTE!"
echo ""
echo "Comandos útiles:"
echo "  - Ver logs: journalctl -u videomusic-generator -f"
echo "  - Reiniciar: sudo systemctl restart videomusic-generator"
echo "  - Detener: sudo systemctl stop videomusic-generator"
echo "  - Estado: sudo systemctl status videomusic-generator"
echo ""
