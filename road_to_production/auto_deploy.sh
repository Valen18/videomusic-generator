#!/bin/bash
# Auto-deployment script sin interacción
# Password: MasKil0s

echo "=================================="
echo "  Auto Deploy - VideoMusic"
echo "=================================="

# Variables
SERVER="root@158.220.94.179"
REMOTE_PATH="~/videomusic/videomusic-generator/road_to_production"
PASSWORD="MasKil0s"

# Install sshpass if needed (Windows Git Bash might not have it)
if ! command -v sshpass &> /dev/null; then
    echo "⚠️  sshpass no disponible - usando SSH directo"
    echo "📝 Por favor ingresa la contraseña cuando se solicite: MasKil0s"
    ssh -o StrictHostKeyChecking=no $SERVER "cd $REMOTE_PATH && bash update.sh"
else
    echo "✅ Usando sshpass para deployment automático"
    sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER "cd $REMOTE_PATH && bash update.sh"
fi

echo "✅ Deployment completado"
