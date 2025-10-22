#!/usr/bin/env python3
"""
Script para construir el ejecutable de VideoMusic Generator
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
        print("Error: No se encuentra main.py. Ejecuta este script desde el directorio raiz del proyecto.")
        return False

    # Limpiar builds anteriores
    print("\nLimpiando builds anteriores...")
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"   Eliminado: {dir_name}")

    # Verificar dependencias principales
    print("\nVerificando dependencias...")
    required_modules = [
        "tkinter",
        "matplotlib",
        "requests",
        "aiohttp",
        "openai",
        "python_dotenv",
        "pygame",
        "PIL"
    ]

    missing_modules = []
    for module in required_modules:
        try:
            if module == "python_dotenv":
                __import__("dotenv")
            else:
                __import__(module)
            print(f"   OK: {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"   FALTA: {module}")

    if missing_modules:
        print(f"\n❌ Faltan dependencias: {', '.join(missing_modules)}")
        print("   Ejecuta: pip install -r requirements.txt")
        return False

    # Construir con PyInstaller
    print("\n[BUILD] Construyendo ejecutable...")
    print("   Esto puede tomar varios minutos...")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        "videomusic_generator.spec"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")

        if result.returncode == 0:
            print("   ✅ Construcción exitosa!")

            # Verificar que el ejecutable se creó
            exe_path = Path("dist/VideoMusic Generator/VideoMusic Generator.exe")
            if exe_path.exists():
                print(f"\n✨ Ejecutable creado: {exe_path.absolute()}")

                # Crear archivos adicionales
                create_additional_files()

                print("\n📦 Paquete completo creado en: dist/VideoMusic Generator/")
                print("   El usuario solo necesita esta carpeta para ejecutar la aplicación.")
                return True
            else:
                print("❌ Error: No se encontró el ejecutable generado")
                return False
        else:
            print("❌ Error en la construcción:")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"❌ Error ejecutando PyInstaller: {e}")
        return False

def create_additional_files():
    """Crear archivos adicionales para el paquete"""
    dist_dir = Path("dist/VideoMusic Generator")

    # Crear archivo de inicio rápido
    start_script = """@echo off
title VideoMusic Generator
echo Iniciando VideoMusic Generator...
echo.
echo Si es la primera vez que ejecutas la aplicación:
echo 1. Ve a Archivo ^> Configuración
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
    readme_content = """# 🎵 VideoMusic Generator

## 🚀 Inicio Rápido

1. **Ejecuta la aplicación:**
   - Haz doble clic en `EJECUTAR_AQUI.bat`
   - O ejecuta directamente `VideoMusic Generator.exe`

2. **Primera configuración:**
   - Ve a `Archivo → ⚙️ Configuración`
   - Introduce tus API Keys (enlaces incluidos)
   - Haz clic en `🧪 Probar Conexiones`
   - Guarda la configuración

3. **¡Empieza a crear!**
   - Genera música, imágenes y videos con IA
   - Monitorea tus gastos en el Dashboard

## 🔑 APIs Necesarias

- **SunoAPI**: https://sunoapi.org/api-key
- **Replicate**: https://replicate.com/account/api-tokens
- **OpenAI**: https://platform.openai.com/api-keys

## 📊 Funcionalidades

✅ Generación de música con IA
✅ Creación de imágenes automática
✅ Producción de videos
✅ Dashboard de gastos
✅ Configuración visual
✅ Historial de sesiones

## 🆘 Soporte

Si tienes problemas:
1. Verifica tu conexión a internet
2. Comprueba que tus API keys sean válidas
3. Revisa el Dashboard para ver errores

---
**VideoMusic Generator** - Generación de contenido multimedia con IA
"""

    with open(dist_dir / "LEEME.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)

    # Crear archivo de configuración de ejemplo
    env_example = """# Configuración de APIs - VideoMusic Generator
# Puedes configurar las APIs aquí o usar la interfaz gráfica

# SunoAPI - Generación de música
SUNO_API_KEY=tu_suno_api_key_aqui
SUNO_BASE_URL=https://api.sunoapi.org

# Replicate - Imágenes y videos
REPLICATE_API_TOKEN=tu_replicate_token_aqui

# OpenAI - Generación de letras
OPENAI_API_KEY=tu_openai_key_aqui
OPENAI_ASSISTANT_ID=asst_tR6OL8QLpSsDDlc6hKdBmVNU

# Directorio de salida
OUTPUT_DIRECTORY=output

# Configuración avanzada
MAX_CONCURRENT_REQUESTS=5
REQUEST_TIMEOUT=30
"""

    with open(dist_dir / ".env.example", "w", encoding="utf-8") as f:
        f.write(env_example)

    print("   ✅ Archivos de usuario creados")
    print("   ✅ Script de inicio creado")
    print("   ✅ Documentación incluida")

if __name__ == "__main__":
    success = main()

    print("\n" + "=" * 55)
    if success:
        print("🎉 ¡Construcción completada exitosamente!")
        print("📦 Paquete listo para distribución")
    else:
        print("❌ La construcción falló")

    print("\nPresiona Enter para salir...")
    input()