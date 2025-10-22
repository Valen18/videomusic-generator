# Guía de Instalación y Configuración

## Requisitos Previos

### Sistema Operativo
- Windows 10/11
- macOS 10.14+
- Ubuntu 18.04+ (o distribuciones equivalentes)

### Software Requerido

#### Python
- **Versión**: 3.8 o superior
- **Verificación**: 
  ```bash
  python --version
  # o
  python3 --version
  ```

#### Conexión a Internet
- Requerida para comunicación con SunoAPI
- Requerida para descarga de archivos de audio

#### API Key de SunoAPI
- Obtenible en: https://sunoapi.org/api-key
- Requiere registro en la plataforma

## Instalación Paso a Paso

### 1. Obtener el Código

#### Opción A: Clonar Repositorio (Recomendado)
```bash
git clone <url-del-repositorio>
cd videomusic-generator
```

#### Opción B: Descargar ZIP
1. Descargar el archivo ZIP del proyecto
2. Extraer en directorio deseado
3. Navegar al directorio extraído

### 2. Configurar Entorno Python

#### Opción A: Entorno Virtual (Recomendado)
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```

#### Opción B: Instalación Global
```bash
# Instalar directamente en el sistema
pip install -r requirements.txt
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

#### Dependencias Incluidas
- `requests==2.31.0`: Cliente HTTP para APIs
- `python-dotenv==1.0.0`: Gestión de variables de entorno
- `aiohttp`: Cliente HTTP asíncrono (incluido en requests)

### 4. Configurar Variables de Entorno

#### Crear Archivo de Configuración
```bash
# Copiar plantilla
cp .env.template .env

# Editar archivo .env
nano .env  # En Linux/macOS
notepad .env  # En Windows
```

#### Configuración Básica
```bash
# .env
SUNO_API_KEY=tu_api_key_aqui
CALLBACK_URL=https://httpbin.org/post
```

#### Configuración Avanzada (Opcional)
```bash
# .env
SUNO_API_KEY=tu_api_key_aqui
CALLBACK_URL=https://httpbin.org/post
SUNO_BASE_URL=https://api.sunoapi.org
OUTPUT_DIRECTORY=output
MAX_CONCURRENT_REQUESTS=5
REQUEST_TIMEOUT=30
```

### 5. Obtener API Key de SunoAPI

#### Paso 1: Registro
1. Visita https://sunoapi.org
2. Crea una cuenta nueva
3. Verifica tu email si es requerido

#### Paso 2: Generar API Key
1. Accede a https://sunoapi.org/api-key
2. Genera una nueva API key
3. Copia la key generada

#### Paso 3: Configurar API Key
```bash
# En .env
SUNO_API_KEY=sk-1234567890abcdef...
```

### 6. Verificar Instalación

#### Test Básico
```bash
python main.py
```

#### Test de Configuración
```bash
python -c "from src.infrastructure.config.settings import Settings; print('Config OK:', Settings.from_env().suno_api_key[:8] + '...')"
```

## Configuración por Sistema Operativo

### Windows

#### Instalar Python
1. Descargar desde https://python.org
2. Ejecutar instalador
3. ✅ Marcar "Add Python to PATH"
4. Seleccionar "Install Now"

#### Configurar PowerShell (Opcional)
```powershell
# Habilitar ejecución de scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Comandos Windows
```cmd
# Activar entorno virtual
venv\Scripts\activate.bat

# Ejecutar aplicación
python main.py
```

### macOS

#### Instalar Python con Homebrew
```bash
# Instalar Homebrew si no está instalado
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar Python
brew install python
```

#### Configurar Terminal
```bash
# Agregar a ~/.zshrc o ~/.bash_profile
export PATH="/usr/local/opt/python/libexec/bin:$PATH"
```

### Linux (Ubuntu/Debian)

#### Instalar Dependencias del Sistema
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv python3-tk
```

#### Para CentOS/RHEL
```bash
sudo yum install python3 python3-pip python3-tkinter
```

## Configuración de Desarrollo

### Estructura de Directorios
```
videomusic-generator/
├── .env                    # Variables de entorno (crear)
├── .env.template           # Plantilla de variables
├── main.py                 # Punto de entrada
├── requirements.txt        # Dependencias Python
├── src/                    # Código fuente
├── output/                 # Canciones generadas (se crea automáticamente)
├── docs/                   # Documentación
└── tests/                  # Tests (futuro)
```

### Variables de Entorno Detalladas

#### SUNO_API_KEY (Requerido)
```bash
SUNO_API_KEY=sk-1234567890abcdef
```
- **Descripción**: Tu API key de SunoAPI
- **Formato**: Cadena alfanumérica que inicia con `sk-`
- **Dónde obtener**: https://sunoapi.org/api-key

#### CALLBACK_URL (Requerido)
```bash
CALLBACK_URL=https://httpbin.org/post
```
- **Descripción**: URL donde SunoAPI enviará notificaciones de completion
- **Por defecto**: `https://httpbin.org/post` (servicio de prueba)
- **Cuándo cambiar**: Si tienes un webhook server propio para recibir notificaciones

#### SUNO_BASE_URL (Opcional)
```bash
SUNO_BASE_URL=https://api.sunoapi.org
```
- **Descripción**: URL base de la API de Suno
- **Por defecto**: `https://api.sunoapi.org`
- **Cuándo cambiar**: Solo para testing con APIs mock

#### OUTPUT_DIRECTORY (Opcional)
```bash
OUTPUT_DIRECTORY=output
```
- **Descripción**: Directorio donde guardar canciones generadas
- **Por defecto**: `output`
- **Formato**: Ruta relativa o absoluta

#### MAX_CONCURRENT_REQUESTS (Opcional)
```bash
MAX_CONCURRENT_REQUESTS=5
```
- **Descripción**: Máximo número de requests simultáneos
- **Por defecto**: `5`
- **Rango recomendado**: 1-10

#### REQUEST_TIMEOUT (Opcional)
```bash
REQUEST_TIMEOUT=30
```
- **Descripción**: Timeout para requests HTTP en segundos
- **Por defecto**: `30`
- **Rango recomendado**: 15-120

## Solución de Problemas

### Error: "Python no encontrado"

#### Windows
```cmd
# Verificar instalación
where python
python --version

# Si no funciona, reinstalar Python con "Add to PATH"
```

#### macOS/Linux
```bash
# Verificar instalación
which python3
python3 --version

# Crear alias si es necesario
echo "alias python=python3" >> ~/.zshrc
source ~/.zshrc
```

### Error: "pip no encontrado"

```bash
# Windows
python -m ensurepip --upgrade

# macOS
brew install python

# Ubuntu/Debian
sudo apt install python3-pip
```

### Error: "tkinter no encontrado"

#### Ubuntu/Debian
```bash
sudo apt install python3-tk
```

#### CentOS/RHEL
```bash
sudo yum install tkinter
```

#### macOS (con Homebrew)
```bash
brew install python-tk
```

### Error: "No module named 'requests'"

```bash
# Verificar entorno virtual activado
pip install -r requirements.txt

# Si persiste el error
pip install --upgrade pip
pip install requests python-dotenv aiohttp
```

### Error: "SUNO_API_KEY environment variable is required"

1. Verificar que existe el archivo `.env`
2. Verificar que contiene `SUNO_API_KEY=...`
3. Verificar que no hay espacios extra
4. Verificar que la API key es válida

### Error de conexión con SunoAPI

#### Verificar Conectividad
```bash
# Test básico de conectividad
curl -I https://api.sunoapi.org

# Test con API key
curl -H "Authorization: Bearer tu_api_key" https://api.sunoapi.org/api/test
```

#### Verificar API Key
1. Acceder a dashboard de SunoAPI
2. Verificar que la key está activa
3. Verificar límites de uso no superados

### Problemas con Permisos de Archivos

#### Windows
```cmd
# Ejecutar como administrador si es necesario
# Verificar permisos en carpeta del proyecto
```

#### macOS/Linux
```bash
# Verificar permisos
ls -la

# Cambiar permisos si es necesario
chmod 755 .
chmod 644 .env
```

## Configuración para Producción

### Configuración Segura

#### Variables de Entorno del Sistema
```bash
# En lugar de archivo .env, usar variables del sistema
export SUNO_API_KEY="tu_api_key"
export OUTPUT_DIRECTORY="/var/app/output"
```

#### Archivos de Log
```bash
# Crear directorio de logs
mkdir logs

# Configurar logging en el código
LOG_LEVEL=INFO
LOG_FILE=logs/videomusic.log
```

### Optimizaciones

#### Configuración de Red
```bash
REQUEST_TIMEOUT=60
MAX_CONCURRENT_REQUESTS=10
```

#### Almacenamiento
```bash
OUTPUT_DIRECTORY=/data/music-output
# Asegurar suficiente espacio en disco
```

## Verificación Final

### Checklist de Instalación

- [ ] Python 3.8+ instalado
- [ ] Dependencias instaladas (`pip list`)
- [ ] Archivo `.env` configurado
- [ ] API key de SunoAPI válida
- [ ] Conectividad a internet verificada
- [ ] Permisos de escritura en directorio output
- [ ] Aplicación ejecuta sin errores

### Test de Funcionalidad

```bash
# 1. Ejecutar aplicación
python main.py

# 2. Verificar que se abre la interfaz gráfica
# 3. Intentar generar una canción de prueba
# 4. Verificar que se guarda en output/
```

## Soporte Adicional

### Logs de Debug

```bash
# Activar modo debug
export DEBUG=1
python main.py

# Ver logs detallados
tail -f logs/debug.log
```

### Información del Sistema

```bash
# Información útil para soporte
python --version
pip --version
pip list | grep -E "(requests|python-dotenv)"
ls -la .env
echo $SUNO_API_KEY | head -c 8
```

Para soporte adicional, incluir esta información en tu reporte de problemas.