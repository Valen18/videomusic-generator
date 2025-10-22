# 🎵 VideoMusic Generator - Aplicación Web Completa

**Versión 2.0 - Con autenticación, validación de APIs y múltiples opciones de despliegue**

## ✨ ¿Qué incluye esta versión?

### 🔐 **Autenticación completa**
- ✅ Sistema de login/registro
- ✅ Sesiones seguras con cookies HTTP-only
- ✅ Múltiples usuarios independientes
- ✅ Cada usuario tiene sus propias API keys
- ✅ Archivos aislados por usuario

### 🔍 **Validación de APIs en tiempo real**
- ✅ Verifica conectividad con Suno API
- ✅ Valida token de Replicate
- ✅ Comprueba API key de OpenAI
- ✅ Botón "Validar Conectividad" en la interfaz

### 💾 **Base de datos SQLite**
- ✅ Gestión de usuarios
- ✅ Sesiones de autenticación
- ✅ Configuración de API por usuario
- ✅ Historial de generaciones

### 🎨 **Interfaz moderna**
- ✅ Tema oscuro profesional
- ✅ Responsive (móvil y desktop)
- ✅ Progreso en tiempo real con WebSockets
- ✅ Notificaciones toast elegantes

## 📁 Estructura de Archivos

```
videomusic-generator/
├── web_app.py                 # Versión básica (sin auth)
├── web_app_secure.py          # ⭐ Versión con autenticación
├── database.py                # Gestión de base de datos
├── api_validator.py           # Validador de conectividad de APIs
├── videomusic.db              # Base de datos SQLite (se crea automáticamente)
│
├── web/                       # Frontend
│   ├── index.html            # Aplicación principal
│   ├── login.html            # Página de login/registro
│   ├── styles.css            # Estilos
│   ├── app.js                # JavaScript básico
│   └── app_secure.js         # ⭐ JavaScript con autenticación
│
├── src/                      # Lógica de negocio (sin cambios)
│   ├── domain/
│   ├── application/
│   │   └── use_cases/       # Casos de uso
│   ├── infrastructure/
│   │   └── adapters/        # Adaptadores de APIs
│   └── presentation/
│
├── output/                   # Archivos generados
│   └── user_{id}/           # Archivos por usuario
│
├── requirements-web.txt      # Dependencias
├── README-WEB.md            # Documentación básica
├── DEPLOY.md                # ⭐ Guía completa de despliegue
└── README_FINAL.md          # Este archivo
```

## 🚀 Inicio Rápido

### 1. Instalar dependencias

```bash
pip install -r requirements-web.txt
```

### 2. Ejecutar la aplicación

```bash
# Versión segura (recomendada)
python web_app_secure.py

# O versión básica (sin autenticación)
python web_app.py
```

### 3. Abrir en el navegador

```
http://localhost:8000
```

### 4. Iniciar sesión

**Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: `admin123`

⚠️ **CAMBIA LA CONTRASEÑA INMEDIATAMENTE**

## 📖 Guía de Uso

### Primer uso

1. **Login** con las credenciales por defecto
2. **Ir a Configuración** (botón ⚙️)
3. **Agregar tus API keys:**
   - Suno API Key (requerido)
   - Replicate API Token (opcional)
   - OpenAI API Key (opcional)
4. **Guardar configuración**
5. **Validar conectividad** (botón 🔍 Validar Conectividad)

### Generar música

1. **Descripción** → Escribir descripción (ej: "canción alegre para niños")
2. **Generar Letra con IA** (si OpenAI está configurado)
3. **Configurar canción:**
   - Título
   - Estilo musical
   - Modelo (V4.5 recomendado)
   - Opciones (instrumental, imagen, etc.)
4. **Generar Canción** → Esperar (2-5 minutos)
5. **Ver resultado** en Historial

### Agregar imagen/video a una canción existente

1. Ir a **Historial**
2. Buscar tu canción
3. Hacer clic en:
   - **📸 Imagen** para generar portada
   - **🎬 Video** para animar la portada
   - **🔄 Recrear bucle** para regenerar el bucle de video

## 🔧 Características Técnicas

### Backend (FastAPI)

- **Framework:** FastAPI 0.104+
- **WebSockets:** Progreso en tiempo real
- **Base de datos:** SQLite (fácil migración a PostgreSQL)
- **Autenticación:** Sesiones con cookies HTTP-only
- **Validación:** Conectividad de APIs en tiempo real
- **APIs:**
  - REST para CRUD
  - WebSocket para operaciones largas

### Frontend (Vanilla JS)

- **Sin frameworks:** HTML + CSS + JavaScript puro
- **WebSocket client:** Comunicación bidireccional
- **Responsive:** Mobile-first design
- **Tema:** Dark mode profesional

### APIs Externas

- **SunoAPI:** Generación de música
- **Replicate:** Imágenes (FLUX) y videos (WAN)
- **OpenAI:** Generación de letras con Assistant

## 🌐 Opciones de Despliegue

### Fácil (Sin servidor propio)

1. **Render** ⭐ Recomendado
   - Gratis con límites
   - SSL automático
   - Auto-deploy desde Git

2. **Railway**
   - $5 de crédito gratis
   - Muy fácil de configurar

3. **Heroku**
   - Plan gratuito limitado
   - Bien documentado

### Medio (Con VPS)

4. **DigitalOcean / Linode / Vultr**
   - Desde $6/mes
   - Control total
   - Ver `DEPLOY.md` para instrucciones

### Avanzado

5. **Docker**
   - Dockerfile incluido
   - Docker Compose incluido
   - Portable y escalable

**Ver `DEPLOY.md` para instrucciones detalladas de cada opción.**

## 🔒 Seguridad

### Implementado

✅ Autenticación con sesiones
✅ Cookies HTTP-only
✅ Contraseñas hasheadas (SHA-256)
✅ Validación de tokens
✅ Expiración de sesiones (24h)
✅ Aislamiento de datos por usuario

### Recomendaciones para producción

- [ ] Usar HTTPS (obligatorio)
- [ ] Cambiar contraseña admin
- [ ] Configurar CORS correctamente
- [ ] Rate limiting (anti-abuse)
- [ ] Backup de base de datos
- [ ] Migrar a PostgreSQL (opcional)

## 📊 Comparación de Versiones

| Característica | `web_app.py` | `web_app_secure.py` ⭐ |
|----------------|--------------|----------------------|
| Autenticación | ❌ No | ✅ Sí |
| Multi-usuario | ❌ No | ✅ Sí |
| API keys por usuario | ❌ No | ✅ Sí |
| Validación de APIs | ❌ No | ✅ Sí |
| Base de datos | ❌ Archivos | ✅ SQLite |
| Seguridad | 🟡 Básica | 🟢 Alta |
| Recomendado para | Desarrollo | Producción |

## 🐛 Solución de Problemas

### Error: "Not authenticated"

**Solución:** Limpia las cookies del navegador o vuelve a iniciar sesión.

### Error: "Suno API not configured"

**Solución:**
1. Ve a Configuración
2. Ingresa tu Suno API Key
3. Haz clic en "Validar Conectividad"
4. Verifica que aparezca "✅ Suno API conectada"

### Los archivos no se guardan

**Solución:**
1. Verifica permisos de escritura en `output/`
2. En Docker, asegúrate de montar el volumen

### WebSocket no conecta

**Solución:**
1. Verifica que el puerto 8000 esté abierto
2. Si usas proxy (Nginx), configura WebSocket upgrade

### Base de datos bloqueada

**Solución:**
```bash
# Reiniciar aplicación
sudo systemctl restart videomusic

# O eliminar archivo .db-lock
rm videomusic.db-shm videomusic.db-wal
```

## 📚 Documentación Adicional

- **`README-WEB.md`** - Documentación de la versión básica
- **`DEPLOY.md`** - Guía completa de despliegue (⭐ muy detallada)
- **`API_DOCS.md`** - Documentación de la API REST (genera con FastAPI docs)

### API Documentation (Swagger)

Una vez ejecutando, accede a:
- Docs interactivos: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Contribuir

Si quieres mejorar la aplicación:

1. Fork el proyecto
2. Crea tu feature branch: `git checkout -b feature/AmazingFeature`
3. Commit: `git commit -m 'Add AmazingFeature'`
4. Push: `git push origin feature/AmazingFeature`
5. Abre un Pull Request

## 📝 Changelog

### v2.0.0 (Actual)
- ✅ Sistema de autenticación completo
- ✅ Multi-usuario con aislamiento de datos
- ✅ Validación de conectividad de APIs
- ✅ Base de datos SQLite
- ✅ Interfaz mejorada

### v1.0.0
- ✅ Versión básica sin autenticación
- ✅ Generación de música, imágenes y videos
- ✅ WebSocket para progreso
- ✅ Historial de sesiones

## 🎯 Roadmap

### Próximas características

- [ ] **Dashboard de estadísticas** (canciones generadas, uso de APIs, etc.)
- [ ] **Roles de usuario** (admin, user, viewer)
- [ ] **Límites por usuario** (quotas de generación)
- [ ] **Compartir canciones** (enlaces públicos)
- [ ] **Exportar a Spotify/YouTube**
- [ ] **Migración a PostgreSQL**
- [ ] **Docker multi-container** (web + db + redis)
- [ ] **Caché con Redis** (para sesiones y resultados)
- [ ] **API pública** (REST API para integraciones)
- [ ] **SDK de Python** (para automatización)

## 💰 Costos Estimados

### APIs Externas (pago por uso)

- **Suno API:** ~$0.08 por canción
- **Replicate (imágenes):** ~$0.002 por imagen
- **Replicate (videos):** ~$0.05 por video
- **OpenAI:** ~$0.01 por letra generada

**Ejemplo:** Generar 1 canción completa (audio + imagen + video + letra) ≈ $0.15

### Hosting

- **Gratis:** Render, Railway (con límites)
- **Económico:** DigitalOcean ($6/mes)
- **Profesional:** AWS/GCP (variable)

## 🆘 Soporte

¿Problemas? ¿Preguntas?

1. Revisa la documentación en `DEPLOY.md`
2. Consulta los logs de la aplicación
3. Abre un issue en GitHub (si aplica)

## 📜 Licencia

Este proyecto es de código abierto. Revisa los términos de servicio de:
- SunoAPI
- Replicate
- OpenAI

---

## 🎉 ¡Disfruta generando música con IA!

**Hecho con ❤️ para hacer la generación de música accesible a todos.**

**¿Te gusta el proyecto?** Dale una ⭐ en GitHub!
