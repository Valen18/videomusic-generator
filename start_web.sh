#!/bin/bash
# Start VideoMusic Generator Web Application

echo "🎵 VideoMusic Generator - Web Application"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Error al crear el entorno virtual"
        exit 1
    fi
fi

# Activate virtual environment
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Error al instalar dependencias"
    deactivate
    exit 1
fi

# Create output directory if it doesn't exist
mkdir -p output

# Check if database exists, if not create it
if [ ! -f "videomusic.db" ]; then
    echo "🗄️  Inicializando base de datos..."
    python3 -c "from database import Database; Database()"
fi

echo ""
echo "✅ Iniciando servidor web..."
echo "🌐 La aplicación estará disponible en: http://localhost:8000"
echo "👤 Credenciales por defecto: admin / admin123"
echo "⚠️  CAMBIA LA CONTRASEÑA INMEDIATAMENTE!"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo ""

# Start the web server
python3 web_app_secure.py
