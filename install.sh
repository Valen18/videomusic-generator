#!/bin/bash
# Simple installation script for VideoMusic Generator

echo "🎵 VideoMusic Generator - Instalación"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado"
    echo "Instálalo con: sudo apt-get install python3 python3-pip python3-venv"
    exit 1
fi

echo "✅ Python 3 encontrado: $(python3 --version)"
echo ""

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Error al crear el entorno virtual"
        exit 1
    fi
    echo "✅ Entorno virtual creado"
else
    echo "✅ Entorno virtual ya existe"
fi

# Activate virtual environment
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Upgrade pip
echo "📥 Actualizando pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Instalando dependencias..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Error al instalar dependencias"
    deactivate
    exit 1
fi

echo "✅ Dependencias instaladas correctamente"

# Create output directory
mkdir -p output
echo "✅ Directorio de salida creado"

# Initialize database
if [ ! -f "videomusic.db" ]; then
    echo "🗄️  Inicializando base de datos..."
    python3 -c "from database import Database; Database()"
    echo "✅ Base de datos creada"
else
    echo "✅ Base de datos ya existe"
fi

echo ""
echo "✅ ¡Instalación completada!"
echo ""
echo "Para iniciar la aplicación web:"
echo "  bash start_web.sh"
echo ""
echo "Para desplegar en producción (requiere sudo):"
echo "  sudo bash deploy_linux.sh"
echo ""
