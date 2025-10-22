#!/usr/bin/env python3
"""
Script simple para construir el ejecutable de VideoMusic Generator
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("VideoMusic Generator - Construccion de Ejecutable")
    print("=" * 55)

    # Verificar que estamos en el directorio correcto
    if not Path("main.py").exists():
        print("Error: No se encuentra main.py. Ejecuta desde el directorio raiz.")
        return False

    # Limpiar builds anteriores
    print("\nLimpiando builds anteriores...")
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"   Eliminado: {dir_name}")

    # Construir con PyInstaller
    print("\nConstruyendo ejecutable...")
    print("Esto puede tomar varios minutos...")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        "videomusic_generator.spec"
    ]

    try:
        print("Ejecutando PyInstaller...")
        result = subprocess.run(cmd, capture_output=False, text=True, cwd=".")

        if result.returncode == 0:
            print("Construccion exitosa!")

            # Verificar que el ejecutable se creó
            exe_path = Path("dist/VideoMusic Generator/VideoMusic Generator.exe")
            if exe_path.exists():
                print(f"\nEjecutable creado: {exe_path.absolute()}")

                # Crear archivos adicionales
                create_additional_files()

                print("\nPaquete completo creado en: dist/VideoMusic Generator/")
                print("El usuario solo necesita esta carpeta.")
                return True
            else:
                print("Error: No se encontro el ejecutable generado")
                return False
        else:
            print("Error en la construccion")
            return False

    except Exception as e:
        print(f"Error ejecutando PyInstaller: {e}")
        return False

def create_additional_files():
    """Crear archivos adicionales para el paquete"""
    dist_dir = Path("dist/VideoMusic Generator")

    # Crear archivo de inicio rápido
    start_script = """@echo off
title VideoMusic Generator
echo Iniciando VideoMusic Generator...
echo.
echo Si es la primera vez que ejecutas la aplicacion:
echo 1. Ve a Archivo ^> Configuracion
echo 2. Configura tus API Keys
echo 3. Prueba las conexiones
echo.
echo Presiona cualquier tecla para continuar...
pause > nul
"VideoMusic Generator.exe"
"""

    with open(dist_dir / "EJECUTAR_AQUI.bat", "w", encoding="utf-8") as f:
        f.write(start_script)

    # Crear README para el usuario final
    readme_content = """VideoMusic Generator

INICIO RAPIDO:

1. Ejecuta la aplicacion:
   - Haz doble clic en EJECUTAR_AQUI.bat
   - O ejecuta directamente "VideoMusic Generator.exe"

2. Primera configuracion:
   - Ve a Archivo > Configuracion
   - Introduce tus API Keys (enlaces incluidos)
   - Haz clic en "Probar Conexiones"
   - Guarda la configuracion

3. Empieza a crear:
   - Genera musica, imagenes y videos con IA
   - Monitorea tus gastos en el Dashboard

APIs NECESARIAS:

- SunoAPI: https://sunoapi.org/api-key
- Replicate: https://replicate.com/account/api-tokens
- OpenAI: https://platform.openai.com/api-keys

FUNCIONALIDADES:

- Generacion de musica con IA
- Creacion de imagenes automatica
- Produccion de videos
- Dashboard de gastos
- Configuracion visual
- Historial de sesiones

SOPORTE:

Si tienes problemas:
1. Verifica tu conexion a internet
2. Comprueba que tus API keys sean validas
3. Revisa el Dashboard para ver errores

VideoMusic Generator - Generacion de contenido multimedia con IA
"""

    with open(dist_dir / "LEEME.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)

    print("   Archivos de usuario creados")
    print("   Script de inicio creado")
    print("   Documentacion incluida")

if __name__ == "__main__":
    success = main()

    print("\n" + "=" * 55)
    if success:
        print("Construccion completada exitosamente!")
        print("Paquete listo para distribucion")
    else:
        print("La construccion fallo")

    print("\nPresiona Enter para salir...")
    input()