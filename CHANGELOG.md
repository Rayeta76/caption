# 📋 Changelog - StockPrep Pro

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-06-28

### 🚀 Agregado
- **Niveles de detalle de descripción**: 3 niveles configurables (mínimo, medio, largo)
- **Optimizaciones TF32**: Soporte completo para RTX 4090 con aceleración ~1.6x
- **Interfaz PySide6**: Interfaz moderna estilo Windows 11
- **Procesamiento en lote**: Soporte para carpetas completas de imágenes
- **Carpeta de salida personalizable**: Configuración flexible de salida
- **Renombrado inteligente**: Renombrado automático basado en descripciones
- **Base de datos SQLite**: Almacenamiento local de resultados
- **Exportación múltiple**: JSON, CSV, XML y archivos .txt
- **Detección automática de GPU**: Selección inteligente del mejor dispositivo
- **Gestión optimizada de memoria**: Configuración CUDA avanzada

### 🔧 Mejorado
- **Parámetros de generación**: Optimizados para descripciones más largas y detalladas
- **Manejo de errores**: Sistema robusto de fallbacks y recuperación
- **Interfaz de usuario**: Diseño moderno y responsive
- **Rendimiento**: Optimizaciones específicas para GPU NVIDIA
- **Compatibilidad**: Soporte para múltiples versiones de Python y PyTorch

### 🐛 Corregido
- **Problemas de memoria**: Gestión mejorada de VRAM
- **Carga de modelos**: Compatibilidad con diferentes variantes de Florence-2
- **Interfaz gráfica**: Corrección de bugs en PySide6 y Tkinter
- **Procesamiento de objetos**: Mejor detección y formateo de resultados

### 🔄 Refactorizado
- **Arquitectura modular**: Separación de componentes en módulos reutilizables
- **Código base**: Limpieza y organización del código fuente
- **Configuración**: Sistema de configuración centralizado
- **Documentación**: Documentación completa y actualizada

### 📚 Documentación
- **README completo**: Guía de instalación y uso detallada
- **Documentación técnica**: Especificaciones de API y configuración
- **Ejemplos de uso**: Casos de uso prácticos y tutoriales
- **Guías de optimización**: Configuración para máximo rendimiento

## [1.0.0] - 2024-12-15

### 🚀 Agregado
- **Procesamiento básico de imágenes** con Florence-2
- **Interfaz Tkinter** básica
- **Extracción de keywords** con YAKE
- **Detección de objetos** básica
- **Exportación a archivos de texto**

---

## 🔮 Próximas Versiones

### [2.1.0] - Planificado
- **Soporte para más modelos**: Integración con otros modelos de visión
- **API REST**: Servicio web para procesamiento remoto
- **Plugins**: Sistema de plugins para funcionalidades extendidas
- **Análisis de sentimiento**: Detección de emociones en imágenes

### [2.2.0] - Planificado
- **Procesamiento de video**: Soporte para archivos de video
- **OCR integrado**: Reconocimiento de texto en imágenes
- **Análisis facial**: Detección y análisis de rostros
- **Exportación a la nube**: Integración con servicios cloud

---

## 📝 Notas de Versión

### Migración desde v1.0
- **Compatible**: Todos los proyectos v1.0 son compatibles con v2.0
- **Configuración**: Los archivos de configuración existentes se migran automáticamente
- **Base de datos**: La estructura de la base de datos se actualiza automáticamente

### Requisitos de Sistema
- **Python**: 3.8 o superior
- **PyTorch**: 2.1+ con soporte CUDA
- **GPU**: NVIDIA con 8GB+ VRAM (recomendado)
- **RAM**: 8GB mínimo, 16GB recomendado

### Rendimiento
- **RTX 4090**: ~2-3 segundos por imagen
- **RTX 3080**: ~3-5 segundos por imagen
- **CPU**: ~30-60 segundos por imagen

---

**StockPrep Pro v2.0** - Potenciando la creatividad con IA 🚀 