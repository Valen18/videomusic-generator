# 🔧 Configuración de APIs y Dashboard de Gastos

## 📋 Resumen

Se ha implementado un sistema completo de configuración de APIs y tracking de gastos que incluye:

- ⚙️ **Interfaz de configuración elegante** para todas las APIs
- 📊 **Dashboard de gastos en tiempo real**
- 💾 **Persistencia de configuración** en archivo JSON
- 🔍 **Tracking automático** de todas las llamadas a APIs
- 📈 **Visualización de estadísticas** con gráficos

## 🚀 Nuevas Funcionalidades

### 1. Pantalla de Configuración

Accede desde: **Archivo → ⚙️ Configuración**

**Características:**
- 🎵 Configuración de SunoAPI (generación de música)
- 🖼️ Configuración de Replicate (imágenes y videos)
- 🤖 Configuración de OpenAI (generación de letras)
- 🔗 Enlaces directos para obtener API keys
- 🧪 Prueba de conectividad para cada API
- 💾 Guardado automático en `api_config.json`

### 2. Dashboard de Gastos

Accede desde: **Herramientas → 📊 Dashboard de Gastos**

**Métricas incluidas:**
- 💰 Gastos totales por API
- 📞 Número de llamadas realizadas
- 🔤 Tokens consumidos
- 📊 Promedio de costo por llamada
- ❌ Llamadas fallidas
- 📈 Gráficos de gastos diarios

### 3. Tracking Automático

**Se registra automáticamente:**
- ⏰ Timestamp de cada llamada
- 🔍 Detalles de request y response
- 💵 Costos estimados por operación
- ✅ Estado de éxito/error
- 🏷️ Asociación por sesión

## 🔑 APIs Configurables

### SunoAPI - Generación de Música
- **URL para API Key**: https://sunoapi.org/api-key
- **Costo estimado**: ~$0.015 por generación
- **Endpoint**: `/api/v1/generate`

### Replicate - Imágenes y Videos
- **URL para API Token**: https://replicate.com/account/api-tokens
- **Modelos soportados**:
  - `bytedance/seedream-4` (~$0.005 por imagen)
  - `wan-video/wan-2.2-i2v-fast` (~$0.02 por video)

### OpenAI - Generación de Letras
- **URL para API Key**: https://platform.openai.com/api-keys
- **Modelo**: GPT-4 Assistant
- **Costo**: ~$0.03 por 1K tokens

## 💾 Archivos de Configuración

### `api_config.json`
```json
{
  "suno_api_key": "tu_suno_api_key_aqui",
  "suno_base_url": "https://api.sunoapi.org",
  "replicate_api_token": "tu_replicate_token_aqui",
  "replicate_base_url": "https://api.replicate.com/v1",
  "openai_api_key": "tu_openai_key_aqui",
  "openai_assistant_id": "asst_tR6OL8QLpSsDDlc6hKdBmVNU",
  "openai_base_url": "https://api.openai.com/v1"
}
```

### `usage_tracking.db`
Base de datos SQLite que almacena:
- Histórico de llamadas a APIs
- Costos y estadísticas de uso
- Detalles de errores y fallos

## 🎨 Interfaz Mejorada

### Elementos de Diseño
- 🎨 **Tema moderno** con colores elegantes
- 📱 **Responsive design** que se adapta al tamaño
- 🔗 **Enlaces clickeables** para obtener API keys
- 📊 **Gráficos interactivos** con matplotlib
- ✨ **Animaciones suaves** y feedback visual

### Usabilidad
- 👆 **Pestañas organizadas** para fácil navegación
- 🔍 **Tooltips informativos** en elementos clave
- ⚡ **Actualización en tiempo real** de estadísticas
- 💾 **Guardado automático** de configuración

## 🛠️ Uso Práctico

### Primera configuración
1. Ejecuta la aplicación
2. Ve a **Archivo → ⚙️ Configuración**
3. Introduce tus API keys usando los enlaces proporcionados
4. Haz clic en **🧪 Probar Conexiones**
5. Guarda con **💾 Guardar Configuración**

### Monitoreo de gastos
1. Utiliza la aplicación normalmente
2. Ve a **Herramientas → 📊 Dashboard de Gastos**
3. Revisa estadísticas y gráficos en tiempo real
4. Haz clic en **🔄 Actualizar Datos** para refrescar

## 🔧 Instalación de Dependencias

Instala las nuevas dependencias:

```bash
pip install matplotlib>=3.5.0
```

## ⚡ Funcionalidades Avanzadas

### Tracking Personalizado
- Cada generación se asocia automáticamente a una sesión
- Los costos se calculan basándose en modelos reales de precios
- Se mantiene un historial completo para análisis posterior

### Configuración Flexible
- Soporte para múltiples entornos (desarrollo/producción)
- URLs base configurables para cada API
- Fallback automático a variables de entorno

### Dashboard Inteligente
- Cálculos automáticos de promedios y totales
- Filtrado por períodos de tiempo
- Alertas visuales para gastos elevados

## 🎯 Beneficios

- ✅ **Visibilidad total** de costos de API
- ✅ **Configuración centralizada** y fácil
- ✅ **Interfaz profesional** y moderna
- ✅ **Tracking automático** sin intervención manual
- ✅ **Análisis detallado** de patrones de uso
- ✅ **Control de presupuesto** en tiempo real

---

*💡 La configuración se guarda automáticamente y persiste entre sesiones. El dashboard se actualiza en tiempo real conforme uses las funcionalidades de generación.*