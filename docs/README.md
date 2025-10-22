# VideoMusic Generator - SunoAPI

## Descripción

VideoMusic Generator es una aplicación de escritorio que permite generar canciones utilizando la API de Suno AI. La aplicación está construida siguiendo los principios de arquitectura hexagonal y SOLID, garantizando un código mantenible, escalable y testeable.

## Características

- 🎵 Generación de canciones con IA usando SunoAPI
- 🎛️ Interfaz gráfica intuitiva con todas las variables configurables
- 💾 Almacenamiento local automático de canciones generadas
- 📊 Historial completo de generaciones
- 🏗️ Arquitectura hexagonal para facilitar el escalado
- ⚙️ Configuración mediante variables de entorno

## Requisitos del Sistema

- Python 3.8 o superior
- Conexión a internet
- API Key de SunoAPI (obtenible en https://sunoapi.org/api-key)

## Instalación

1. **Clona o descarga el proyecto**
   ```bash
   git clone <repositorio>
   cd videomusic-generator
   ```

2. **Instala las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configura la API Key**
   - Copia el archivo `.env.template` a `.env`
   - Edita `.env` y añade tu API Key:
   ```
   SUNO_API_KEY=tu_api_key_aqui
   ```

4. **Ejecuta la aplicación**
   ```bash
   python main.py
   ```

## Uso de la Aplicación

### Pestaña "Generar Canción"

1. **Letra de la canción**: Pega o escribe la letra en el área de texto
2. **Configuración**:
   - **Título**: Nombre de la canción
   - **Estilo**: Género musical (ej: "rock", "pop", "jazz")
   - **Modelo**: Versión del modelo IA (V3.5, V4, V4.5)
   - **Modo personalizado**: Habilita configuraciones avanzadas
   - **Instrumental**: Genera solo música sin voz
3. **Generar**: Inicia el proceso de generación
4. **Progreso**: Muestra el estado actual del proceso

### Pestaña "Historial"

- Lista todas las generaciones realizadas
- Muestra detalles al seleccionar una sesión
- Permite explorar canciones generadas anteriormente

## Arquitectura del Proyecto

```
videomusic-generator/
├── src/
│   ├── domain/                 # Reglas de negocio y entidades
│   │   ├── entities/          # Entidades del dominio
│   │   └── ports/             # Interfaces/contratos
│   ├── application/           # Casos de uso
│   │   └── use_cases/         # Lógica de aplicación
│   ├── infrastructure/        # Adaptadores externos
│   │   ├── adapters/          # Implementaciones de puertos
│   │   └── config/            # Configuración
│   └── presentation/          # Interfaz de usuario
│       └── gui/               # Interfaz gráfica
├── output/                    # Canciones generadas
├── docs/                      # Documentación
├── main.py                    # Punto de entrada
├── requirements.txt           # Dependencias
└── .env                       # Variables de entorno
```

### Principios Aplicados

#### Arquitectura Hexagonal
- **Domain**: Contiene la lógica de negocio pura
- **Application**: Orquesta los casos de uso
- **Infrastructure**: Implementa detalles técnicos
- **Presentation**: Maneja la interacción con el usuario

#### Principios SOLID
- **SRP**: Cada clase tiene una única responsabilidad
- **OCP**: Extensible sin modificar código existente
- **LSP**: Las implementaciones son intercambiables
- **ISP**: Interfaces específicas y cohesivas
- **DIP**: Dependencias invertidas mediante puertos

## Escalabilidad

La arquitectura está preparada para:

### Separación Frontend/Backend
```
backend/
├── api/                       # REST API endpoints
├── src/                       # Lógica existente reutilizable
└── requirements_backend.txt

frontend/
├── web/                       # Aplicación web
├── mobile/                    # Aplicación móvil
└── desktop/                   # Aplicación de escritorio
```

### Nuevas Funcionalidades
- **Generación de video**: Nuevo puerto `VideoGeneratorPort`
- **Múltiples APIs**: Nuevos adaptadores para otras APIs de música
- **Base de datos**: Reemplazar `LocalFileStorage` con `DatabaseStorage`
- **Autenticación**: Nuevo puerto `AuthenticationPort`

## Configuración Avanzada

### Variables de Entorno Disponibles

```bash
SUNO_API_KEY=tu_api_key           # Requerido
SUNO_BASE_URL=https://api.sunoapi.org  # Opcional
OUTPUT_DIRECTORY=output               # Opcional
MAX_CONCURRENT_REQUESTS=5            # Opcional
REQUEST_TIMEOUT=30                   # Opcional
```

### Personalización de Modelos

Los modelos disponibles son:
- **V3.5**: Equilibrado con diversidad creativa
- **V4**: Mejor calidad de audio con estructura refinada
- **V4.5**: Mezcla superior de géneros con prompts inteligentes

## Solución de Problemas

### Error: "SUNO_API_KEY environment variable is required"
- Verifica que el archivo `.env` existe
- Asegúrate de que contiene `SUNO_API_KEY=tu_clave`

### Error de conexión
- Verifica tu conexión a internet
- Confirma que tu API Key es válida
- Revisa si hay límites en tu cuenta de SunoAPI

### Archivos no se descargan
- Verifica permisos de escritura en la carpeta `output/`
- Asegúrate de que hay espacio suficiente en disco

## Desarrollo

### Ejecutar Tests
```bash
python -m pytest tests/
```

### Estructura de Tests
```
tests/
├── unit/                      # Tests unitarios
│   ├── domain/
│   ├── application/
│   └── infrastructure/
├── integration/               # Tests de integración
└── e2e/                      # Tests end-to-end
```

### Contribuir

1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Añadir nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## Licencia

[Especificar licencia]

## Soporte

Para soporte y reportar bugs:
- GitHub Issues: [URL del repositorio]
- Email: [email de contacto]