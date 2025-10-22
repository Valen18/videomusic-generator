@echo off
echo Iniciando VideoMusic Generator...
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Por favor instala Python 3.8+ desde https://python.org
    pause
    exit /b 1
)

REM Verificar si existe .env
if not exist .env (
    echo ERROR: No se encontró el archivo .env
    echo Por favor copia .env.template a .env y configura tu API key
    pause
    exit /b 1
)

REM Instalar dependencias si es necesario
echo Verificando dependencias...
pip install -r requirements.txt >nul 2>&1

REM Ejecutar aplicación
echo Ejecutando aplicación...
python main.py

pause