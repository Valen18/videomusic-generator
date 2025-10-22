@echo off
echo Deteniendo todos los procesos de Python que ejecutan web_app_secure.py...
taskkill /F /FI "WINDOWTITLE eq *python*web_app_secure*" 2>nul
timeout /t 2 /nobreak >nul

echo Iniciando servidor...
cd /d "%~dp0"
python web_app_secure.py
