#!/usr/bin/env python3
"""
Script de post-construcción para crear el paquete final
"""
import os
import shutil
from pathlib import Path

def create_final_package():
    """Crea el paquete final con archivos adicionales"""

    print("Post-build: Creando paquete final...")

    dist_dir = Path("dist/VideoMusic Generator")

    if not dist_dir.exists():
        print("Error: No se encontró el directorio de distribución")
        return False

    # Crear archivo de inicio rápido
    start_script = """@echo off
title VideoMusic Generator
cls
echo ================================================
echo          VideoMusic Generator v1.0
echo ================================================
echo.
echo Iniciando aplicacion...
echo.
echo Si es la primera vez que ejecutas la aplicacion:
echo 1. Ve a Archivo ^> Configuracion
echo 2. Configura tus API Keys (enlaces incluidos)
echo 3. Haz clic en "Probar Conexiones"
echo 4. Guarda la configuracion
echo.
echo Presiona cualquier tecla para continuar...
pause > nul
cls
echo Abriendo VideoMusic Generator...
"VideoMusic Generator.exe"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: La aplicacion no pudo iniciarse correctamente.
    echo Verifica que todos los archivos esten presentes.
    echo.
    pause
)
"""

    with open(dist_dir / "EJECUTAR_AQUI.bat", "w", encoding="utf-8") as f:
        f.write(start_script)

    # Crear README para el usuario final
    readme_content = """VideoMusic Generator - Guia de Usuario

INICIO RAPIDO
=============

1. EJECUTAR LA APLICACION:
   - Haz doble clic en "EJECUTAR_AQUI.bat"
   - O ejecuta directamente "VideoMusic Generator.exe"

2. PRIMERA CONFIGURACION:
   - Ve a: Archivo > Configuracion
   - Introduce tus API Keys usando los enlaces proporcionados
   - Haz clic en "Probar Conexiones" para verificar
   - Guarda la configuracion

3. CREAR TU PRIMER VIDEO MUSICAL:
   - Describe la musica que quieres en el campo principal
   - (Opcional) Genera letra automaticamente con OpenAI
   - Haz clic en "Generar Cancion"
   - Espera a que se complete el proceso automatico

APIS NECESARIAS
===============

Para usar todas las funcionalidades necesitas estas APIs:

1. SunoAPI (Generacion de Musica) - OBLIGATORIO
   - URL: https://sunoapi.org/api-key
   - Costo: ~$0.015 por cancion

2. Replicate (Imagenes y Videos) - OPCIONAL
   - URL: https://replicate.com/account/api-tokens
   - Costo: ~$0.005 imagenes, ~$0.02 videos

3. OpenAI (Generacion de Letras) - OPCIONAL
   - URL: https://platform.openai.com/api-keys
   - Costo: ~$0.03 por 1000 tokens

CARACTERISTICAS PRINCIPALES
===========================

- Generacion de musica con IA (SunoAPI)
- Creacion automatica de imagenes de portada
- Produccion de videos musicales completos
- Generacion de letras con IA
- Dashboard de gastos en tiempo real
- Historial de todas tus creaciones
- Configuracion visual y sencilla

MONITOREO DE GASTOS
===================

- Ve a: Herramientas > Dashboard de Gastos
- Revisa cuanto gastas por API
- Monitorea costos diarios y totales
- Ve estadisticas de uso detalladas

FLUJO DE TRABAJO TIPICO
=======================

1. Describe tu idea musical
2. (Opcional) Genera letra con IA
3. Crear la cancion con SunoAPI
4. Generar imagen de portada automaticamente
5. Producir video musical
6. Revisar resultado en el historial
7. Monitorear gastos en el dashboard

COSTO ESTIMADO POR VIDEO COMPLETO
=================================

- Letra (OpenAI): ~$0.01
- Musica (SunoAPI): ~$0.015
- Imagen (Replicate): ~$0.005
- Video (Replicate): ~$0.02
- TOTAL: ~$0.05 por video musical completo

RESOLUCION DE PROBLEMAS
=======================

Error: "No se puede conectar"
- Verifica conexion a internet
- Comprueba API keys en configuracion
- Revisa que tengas saldo en las cuentas

Error: "Configuracion incompleta"
- Ve a Archivo > Configuracion
- Introduce al menos la API key de SunoAPI
- Guarda la configuracion

La aplicacion no abre
- Ejecuta como administrador
- Verifica que Windows Defender no este bloqueando
- Asegura que toda la carpeta este descomprimida

Problemas de rendimiento
- Cierra otras aplicaciones pesadas
- Verifica tener al menos 4GB RAM libres
- Usa SSD para mejor rendimiento

ARCHIVOS IMPORTANTES
====================

- VideoMusic Generator.exe: Aplicacion principal
- EJECUTAR_AQUI.bat: Inicio rapido
- _internal/: Archivos del sistema (NO MOVER)
- api_config.json: Tu configuracion (se crea automaticamente)
- usage_tracking.db: Base de datos de gastos
- output/: Carpeta con tus creaciones

SEGURIDAD Y PRIVACIDAD
======================

- Tus API keys se guardan solo en tu computadora
- No se envian datos a terceros
- Todo el contenido generado es privado
- El tracking es solo para control de gastos local

SOPORTE
=======

Si tienes problemas:
1. Revisa esta guia completa
2. Verifica configuracion de APIs
3. Consulta el dashboard para errores
4. Contacta soporte tecnico si es necesario

===============================================
VideoMusic Generator v1.0
Generacion de contenido multimedia con IA
===============================================
"""

    with open(dist_dir / "LEEME.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)

    # Crear archivo de configuración de ejemplo
    env_example = """# VideoMusic Generator - Configuracion de APIs
# Puedes configurar las APIs aqui o usar la interfaz grafica

# SunoAPI - Generacion de musica (OBLIGATORIO)
SUNO_API_KEY=tu_suno_api_key_aqui
SUNO_BASE_URL=https://api.sunoapi.org

# Replicate - Imagenes y videos (OPCIONAL)
REPLICATE_API_TOKEN=tu_replicate_token_aqui

# OpenAI - Generacion de letras (OPCIONAL)
OPENAI_API_KEY=tu_openai_key_aqui
OPENAI_ASSISTANT_ID=asst_tR6OL8QLpSsDDlc6hKdBmVNU

# Configuracion del sistema
OUTPUT_DIRECTORY=output
MAX_CONCURRENT_REQUESTS=5
REQUEST_TIMEOUT=30
"""

    with open(dist_dir / ".env.example", "w", encoding="utf-8") as f:
        f.write(env_example)

    # Crear script de verificación
    verify_script = """@echo off
title Verificacion de VideoMusic Generator
cls
echo ================================================
echo      Verificacion de VideoMusic Generator
echo ================================================
echo.
echo Verificando archivos...
echo.

if exist "VideoMusic Generator.exe" (
    echo [OK] Aplicacion principal encontrada
) else (
    echo [ERROR] Falta VideoMusic Generator.exe
)

if exist "_internal\" (
    echo [OK] Archivos del sistema encontrados
) else (
    echo [ERROR] Faltan archivos del sistema
)

if exist "LEEME.txt" (
    echo [OK] Documentacion encontrada
) else (
    echo [WARNING] Falta documentacion
)

echo.
echo Verificacion completada.
echo.
echo Si ves errores, vuelve a descomprimir el archivo completo.
echo.
pause
"""

    with open(dist_dir / "VERIFICAR_INSTALACION.bat", "w", encoding="utf-8") as f:
        f.write(verify_script)

    print("   ✓ Archivo de inicio rapido creado")
    print("   ✓ Guia del usuario creada")
    print("   ✓ Configuracion de ejemplo creada")
    print("   ✓ Script de verificacion creado")
    print("   ✓ Paquete final completado")

    return True

def get_package_size():
    """Obtiene el tamaño del paquete final"""
    dist_dir = Path("dist/VideoMusic Generator")
    if not dist_dir.exists():
        return "N/A"

    total_size = 0
    for dirpath, dirnames, filenames in os.walk(dist_dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)

    # Convertir a MB
    size_mb = total_size / (1024 * 1024)
    return f"{size_mb:.1f} MB"

if __name__ == "__main__":
    print("VideoMusic Generator - Post-Build")
    print("=" * 40)

    if create_final_package():
        size = get_package_size()
        print(f"\nPaquete final creado exitosamente!")
        print(f"Tamaño: {size}")
        print(f"Ubicacion: dist/VideoMusic Generator/")
        print("\nListo para distribucion!")
    else:
        print("\nError en la creacion del paquete final")

    print("\nPresiona Enter para salir...")
    input()