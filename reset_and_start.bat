@echo off
echo ============================================================
echo   Reiniciando VideoMusic Generator
echo ============================================================
echo.

echo [1/3] Deteniendo procesos Python...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/3] Limpiando base de datos de sesiones antiguas...
if exist videomusic.db (
    python -c "from database import Database; db = Database(); db.cleanup_expired_sessions(); print('  Sesiones expiradas limpiadas')"
)

echo [3/3] Iniciando servidor...
echo.
echo ============================================================
echo   Servidor iniciando...
echo ============================================================
echo.
echo Para acceder: http://localhost:8000
echo Usuario: admin
echo Password: admin123
echo.
echo IMPORTANTE: Limpia la cache del navegador antes de acceder:
echo   - Chrome/Edge: CTRL + SHIFT + DELETE
echo   - Firefox: CTRL + SHIFT + DELETE
echo   - O usa modo incognito: CTRL + SHIFT + N
echo.
echo Presiona CTRL+C para detener el servidor
echo ============================================================
echo.

python start_server.py
