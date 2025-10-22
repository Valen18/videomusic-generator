# 🎵 VideoMusic Generator - Guía de Despliegue en Linux

## 📋 Requisitos Previos

- **Sistema Operativo**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- **Python**: 3.8 o superior
- **Memoria RAM**: Mínimo 2GB, recomendado 4GB
- **Espacio en Disco**: Mínimo 5GB libres
- **Acceso a Internet**: Para instalar dependencias y acceder a las APIs

## 🚀 Instalación Rápida

### Paso 1: Clonar o transferir el proyecto

```bash
# Si usas git
git clone <tu-repositorio>
cd videomusic-generator

# O si transfieres los archivos manualmente
scp -r videomusic-generator user@server:/path/to/destination
ssh user@server
cd /path/to/destination/videomusic-generator
```

### Paso 2: Dar permisos de ejecución a los scripts

```bash
chmod +x install.sh start_web.sh deploy_linux.sh
```

### Paso 3: Ejecutar la instalación

```bash
bash install.sh
```

Este script:
- ✅ Verifica que Python 3 esté instalado
- ✅ Crea un entorno virtual
- ✅ Instala todas las dependencias
- ✅ Crea la base de datos SQLite
- ✅ Prepara el directorio de salida

## 🖥️ Desarrollo / Pruebas Locales

Para ejecutar la aplicación en modo desarrollo:

```bash
bash start_web.sh
```

La aplicación estará disponible en: **http://localhost:8000**

**Credenciales por defecto**:
- Usuario: `admin`
- Contraseña: `admin123`

⚠️ **IMPORTANTE**: Cambia la contraseña inmediatamente después del primer inicio de sesión.

## 🌐 Despliegue en Producción

Para desplegar en un servidor Linux con nginx y systemd:

```bash
sudo bash deploy_linux.sh
```

Este script realiza las siguientes acciones:

1. ✅ Instala dependencias del sistema (Python, nginx)
2. ✅ Configura el entorno virtual
3. ✅ Crea un servicio systemd para la aplicación
4. ✅ Configura nginx como proxy reverso
5. ✅ Inicia los servicios automáticamente

Después del despliegue, la aplicación estará disponible en: **http://IP-DEL-SERVIDOR**

## 🔧 Gestión del Servicio

### Ver el estado del servicio

```bash
sudo systemctl status videomusic-generator
```

### Ver logs en tiempo real

```bash
sudo journalctl -u videomusic-generator -f
```

### Reiniciar el servicio

```bash
sudo systemctl restart videomusic-generator
```

### Detener el servicio

```bash
sudo systemctl stop videomusic-generator
```

### Iniciar el servicio

```bash
sudo systemctl start videomusic-generator
```

### Deshabilitar inicio automático

```bash
sudo systemctl disable videomusic-generator
```

## 🔐 Configuración de Seguridad

### 1. Cambiar contraseña del usuario admin

Después del primer inicio de sesión:
1. Haz clic en tu nombre de usuario (👤 admin)
2. Selecciona "Cambiar contraseña"
3. Ingresa una contraseña segura

### 2. Configurar HTTPS (Recomendado para producción)

Si tienes un dominio, puedes configurar HTTPS con Let's Encrypt:

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com
```

### 3. Configurar Firewall

```bash
# Permitir HTTP y HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## 🔑 Configuración de API Keys

Después de iniciar sesión:

1. Haz clic en **⚙️ Configuración**
2. Ingresa tus API Keys:
   - **Suno API Key**: Requerida para generar música
   - **Replicate API Token**: Opcional, para generar imágenes y videos
   - **OpenAI API Key**: Opcional, para generar letras con IA
3. Haz clic en **💾 Guardar**
4. Valida la conectividad con **🔍 Validar Conectividad**

### Obtener API Keys

- **Suno**: [https://api.sunoapi.org](https://api.sunoapi.org)
- **Replicate**: [https://replicate.com/account/api-tokens](https://replicate.com/account/api-tokens)
- **OpenAI**: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

## 📁 Estructura de Archivos

```
videomusic-generator/
├── web/                    # Archivos estáticos del frontend
│   ├── index.html
│   ├── login.html
│   ├── app_secure.js
│   └── styles.css
├── src/                    # Código fuente de la aplicación
│   ├── domain/            # Entidades y lógica de negocio
│   ├── application/       # Casos de uso
│   ├── infrastructure/    # Adaptadores y configuración
│   └── presentation/      # Interfaz de usuario (GUI)
├── output/                 # Archivos generados
├── web_app_secure.py      # Servidor web FastAPI
├── database.py            # Gestión de base de datos
├── api_validator.py       # Validador de APIs
├── requirements.txt       # Dependencias Python
├── videomusic.db          # Base de datos SQLite
├── install.sh             # Script de instalación
├── start_web.sh           # Script de inicio (desarrollo)
└── deploy_linux.sh        # Script de despliegue (producción)
```

## 🐛 Solución de Problemas

### El servicio no inicia

```bash
# Ver logs detallados
sudo journalctl -u videomusic-generator -n 50

# Verificar permisos
ls -la /path/to/videomusic-generator

# Verificar que las dependencias estén instaladas
source venv/bin/activate
pip list
```

### Error de conexión a la base de datos

```bash
# Verificar que la base de datos existe y tiene permisos
ls -la videomusic.db
chmod 644 videomusic.db

# Reinicializar la base de datos (⚠️ ESTO BORRARÁ TODOS LOS DATOS)
rm videomusic.db
python3 -c "from database import Database; Database()"
```

### Nginx retorna 502 Bad Gateway

```bash
# Verificar que la aplicación está corriendo
sudo systemctl status videomusic-generator

# Verificar logs de nginx
sudo tail -f /var/log/nginx/error.log

# Reiniciar nginx
sudo systemctl restart nginx
```

### No se pueden generar canciones

1. Verifica que tu API Key de Suno sea válida
2. Ve a **⚙️ Configuración** y haz clic en **🔍 Validar Conectividad**
3. Revisa los logs del servicio para más detalles

### WebSocket se desconecta constantemente

```bash
# Aumentar el timeout de nginx
sudo nano /etc/nginx/sites-available/videomusic-generator

# Agregar estas líneas en la sección location /ws
proxy_read_timeout 86400;
proxy_send_timeout 86400;

# Reiniciar nginx
sudo systemctl restart nginx
```

## 📊 Monitoreo

### Espacio en disco

```bash
# Ver espacio usado por las generaciones
du -sh output/

# Limpiar archivos antiguos (opcional)
find output/ -type f -mtime +30 -delete
```

### Uso de recursos

```bash
# Ver uso de CPU y memoria
htop

# Ver procesos de Python
ps aux | grep python
```

## 🔄 Actualización

Para actualizar la aplicación:

```bash
# Detener el servicio
sudo systemctl stop videomusic-generator

# Actualizar el código
git pull  # o transferir los nuevos archivos

# Activar el entorno virtual y actualizar dependencias
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Reiniciar el servicio
sudo systemctl start videomusic-generator
```

## 📝 Backup

### Backup de la base de datos

```bash
# Crear backup
cp videomusic.db videomusic.db.backup.$(date +%Y%m%d)

# Restaurar backup
cp videomusic.db.backup.YYYYMMDD videomusic.db
sudo systemctl restart videomusic-generator
```

### Backup de archivos generados

```bash
# Crear backup comprimido
tar -czf output_backup_$(date +%Y%m%d).tar.gz output/

# Restaurar backup
tar -xzf output_backup_YYYYMMDD.tar.gz
```

## 🆘 Soporte

Si encuentras problemas:

1. Revisa esta guía de solución de problemas
2. Consulta los logs del sistema
3. Verifica que todas las API Keys sean válidas
4. Asegúrate de tener la última versión de las dependencias

## 📄 Licencia

[Especifica tu licencia aquí]

---

¡Disfruta generando música con VideoMusic Generator! 🎵🎬
