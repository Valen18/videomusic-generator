#!/bin/bash

echo "Iniciando VideoMusic Generator..."
echo

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 no está instalado"
    echo "Por favor instala Python 3.8+ desde tu gestor de paquetes"
    exit 1
fi

# Verificar si existe .env
if [ ! -f .env ]; then
    echo "ERROR: No se encontró el archivo .env"
    echo "Por favor copia .env.template a .env y configura tu API key"
    exit 1
fi

# Instalar dependencias si es necesario
echo "Verificando dependencias..."
pip3 install -r requirements.txt > /dev/null 2>&1

# Ejecutar aplicación
echo "Ejecutando aplicación..."
python3 main.py