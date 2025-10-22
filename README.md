# VideoMusic Generator 🎵🖼️

Generador de música y imágenes usando SunoAPI y Replicate, con una interfaz gráfica intuitiva.

## ✨ Características

- 🎵 **Generación de Música**: Crea canciones usando SunoAPI con diferentes modelos y estilos
- 🖼️ **Generación de Imágenes**: Crea imágenes de portada coloridas e infantiles usando seedream-4 de Replicate
- ⚡ **Procesamiento Paralelo**: Genera música e imagen simultáneamente para mayor eficiencia
- 🎧 **Historial Visual Profesional**: Interfaz moderna con tarjetas, reproductor integrado y miniaturas
- 🔍 **Búsqueda y Filtros Avanzados**: Encuentra canciones rápidamente con búsqueda en tiempo real
- 🔄 **Generación Retroactiva**: Genera imágenes para canciones creadas anteriormente
- 📱 **UX Moderna**: Interfaz responsive con controles intuitivos y feedback visual
- 🎨 **Personalización**: Control completo sobre estilos, modelos y configuraciones

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone <tu-repositorio>
cd videomusic-generator
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Copia el archivo de ejemplo:
```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:
```env
# Obligatorio para generar música
SUNO_API_KEY=tu_suno_api_key_aqui

# Opcional para generar imágenes
REPLICATE_API_TOKEN=tu_replicate_api_token_aqui

# Configuración adicional
OUTPUT_DIRECTORY=output
CALLBACK_URL=https://httpbin.org/post
```

### 4. Obtener las claves API

#### SunoAPI (Obligatorio)
1. Visita [SunoAPI](https://sunoapi.org)
2. Crea una cuenta y obtén tu API key
3. Configura `SUNO_API_KEY` en tu archivo `.env`

#### Replicate (Opcional - Para imágenes)
1. Visita [Replicate](https://replicate.com)
2. Crea una cuenta y obtén tu API token
3. Configura `REPLICATE_API_TOKEN` en tu archivo `.env`

> **Nota**: Sin Replicate token, solo podrás generar música. La opción de imágenes aparecerá deshabilitada.

## 🚀 Uso

### Ejecutar la aplicación
```bash
python main.py
```

### Funcionalidades principales

#### 1. **Generar Nueva Canción + Imagen**
- Ingresa la letra de la canción
- Especifica título y estilo musical
- Selecciona el modelo de IA (V3.5, V4, V4.5)
- Marca "Generar imagen de portada" si está disponible
- ¡Haz clic en "Generar Canción"!

#### 2. **Generar Imagen para Canción Existente**
- Ve a la pestaña "Historial"
- Selecciona una canción que no tenga imagen
- Haz clic en "Generar Imagen"
- La imagen se creará basada en la letra y título de la canción

#### 3. **Explorar Historial Visual**
- **Vista de tarjetas**: Cada canción se muestra en una tarjeta profesional con miniatura
- **Reproductor multi-track**: Controles para reproducir ambos tracks generados por Suno
  - Botones Previous/Next para cambiar entre tracks
  - Contador visual "Track 1/2" 
  - Reproducción independiente de cada variación
- **Búsqueda instantánea**: Busca por título, estilo o letra en tiempo real
- **Filtros inteligentes**: "Con música", "Con imagen", "Sin imagen", etc.
- **Ordenación**: Por fecha, alfabético, etc.
- **Acciones rápidas**: Generar imagen, ver detalles, abrir carpeta
- **Estados visuales**: Badges de colores para identificar el estado fácilmente

## 🎨 Características de las Imágenes

Las imágenes generadas tienen las siguientes características:

- **Formato**: 16:9 (ideal para videos)
- **Estilo**: Infantil y colorido estilo cartoon
- **Contenido**: Basado en la letra y título de la canción
- **Calidad**: Alta resolución usando seedream-4
- **Almacenamiento**: Se guardan como `{session_id}_cover.png`

## 📁 Estructura del Proyecto

```
videomusic-generator/
├── src/
│   ├── domain/              # Entidades y puertos del dominio
│   ├── application/         # Casos de uso
│   ├── infrastructure/      # Adaptadores y configuración
│   └── presentation/
│       └── gui/
│           ├── components/  # Componentes reutilizables (SessionCard, SearchBar)
│           ├── styles.py    # Sistema de estilos y temas
│           ├── history_tab.py # Historial visual mejorado
│           └── main_window.py # Ventana principal
├── output/                  # Archivos generados
├── docs/                    # Documentación
├── requirements.txt         # Dependencias (incluye Pillow, pygame)
├── .env.example            # Ejemplo de configuración
└── main.py                # Punto de entrada
```

## 🔧 Desarrollo

### Arquitectura
- **Clean Architecture**: Separación clara de responsabilidades
- **Async/Await**: Operaciones no bloqueantes
- **Threading**: UI responsiva durante generaciones largas

### Testing
```bash
# Probar configuración de Replicate
python test_replicate.py

# Probar GUI sin Replicate
python test_gui_without_replicate.py
```

## ❗ Solución de Problemas

### La opción de imagen aparece deshabilitada
- Verifica que `REPLICATE_API_TOKEN` esté configurado en tu `.env`
- Asegúrate de que el token sea válido
- Ejecuta `python test_replicate.py` para diagnosticar

### Error al generar música
- Verifica tu `SUNO_API_KEY`
- Revisa tu saldo/créditos en SunoAPI
- Comprueba tu conexión a internet

### Error al generar imagen
- Verifica tu token de Replicate
- Comprueba que el modelo seedream-4 esté disponible
- Revisa los logs para errores específicos

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu característica (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Distribuido bajo la Licencia MIT. Ver `LICENSE` para más información.

## 🙏 Agradecimientos

- [SunoAPI](https://sunoapi.org) - Por la generación de música
- [Replicate](https://replicate.com) - Por la generación de imágenes
- [seedream-4](https://replicate.com/bytedance/seedream-4) - Modelo de generación de imágenes