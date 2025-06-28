# 🚀 StockPrep Pro v2.0

**Sistema de procesamiento de imágenes con IA basado en Microsoft Florence-2**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.1+-red.svg)](https://pytorch.org)
[![CUDA](https://img.shields.io/badge/CUDA-12.1+-green.svg)](https://developer.nvidia.com/cuda-toolkit)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Características Principales

### ✨ **Procesamiento Inteligente de Imágenes**
- **Descripciones detalladas** con 3 niveles de detalle (mínimo, medio, largo)
- **Detección de objetos** con coordenadas y confianza
- **Extracción de keywords** automática con YAKE
- **Procesamiento en lote** de carpetas completas

### 🎮 **Optimizado para GPU**
- **TF32 habilitado** para RTX 4090 (aceleración ~1.6x)
- **cuDNN benchmark** para máximo rendimiento
- **Gestión inteligente de memoria** CUDA
- **Detección automática** de GPU disponible

### 🖥️ **Interfaces Modernas**
- **PySide6** - Interfaz Windows 11 nativa
- **Tkinter** - Interfaz clásica (fallback)
- **Diseño responsive** y moderno
- **Progreso en tiempo real**

### 💾 **Gestión de Datos**
- **Base de datos SQLite** integrada
- **Exportación múltiple** (JSON, CSV, XML)
- **Renombrado inteligente** de imágenes
- **Historial completo** de procesamiento

## 🚀 Instalación Rápida

### Requisitos del Sistema
- **Python 3.8+**
- **CUDA 12.1+** (opcional, para GPU)
- **GPU NVIDIA** (recomendado: RTX 30xx/40xx)
- **8GB RAM** mínimo, 16GB recomendado

### Instalación Automática
```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/stockprep-pro.git
cd stockprep-pro

# Instalación automática
python setup_stockprep.py
```

### Instalación Manual
```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Descargar modelo (opcional)
python -c "from src.core.model_manager import Florence2Manager; Florence2Manager().cargar_modelo()"
```

## 🎮 Uso Rápido

### Interfaz Gráfica
```bash
# Ejecutar con PySide6 (recomendado)
python main.py

# Ejecutar con Tkinter (fallback)
python main.py --gui tkinter
```

### Línea de Comandos
```python
from src.core.model_manager import Florence2Manager
from src.core.image_processor import ImageProcessor

# Cargar modelo
manager = Florence2Manager()
manager.cargar_modelo()

# Procesar imagen
processor = ImageProcessor(manager)
result = processor.process_image("imagen.jpg", "largo")

print(f"Descripción: {result['caption']}")
print(f"Keywords: {result['keywords']}")
print(f"Objetos: {result['objects']}")
```

## 📊 Niveles de Detalle

### 🟢 **Mínimo** (Rápido)
- Descripción básica de una línea
- Ideal para procesamiento rápido
- ~10-15 palabras

### 🟡 **Medio** (Balanceado)
- Descripción estructurada con posiciones
- Información contextual
- ~20-40 palabras

### 🔴 **Largo** (Detallado)
- Descripción muy detallada y rica
- Máximo detalle y contexto
- ~50-100+ palabras

## ⚙️ Configuración

### Archivo de Configuración
```yaml
# config/settings.yaml
modelo:
  nombre: Florence-2-large-ft-safetensors
  ruta_local: models/Florence-2-large-ft-safetensors
  dtype: float32

ruta_salida: output/
formato_salida: JSON
exportar_txt: true
```

### Variables de Entorno
```bash
# Ruta personalizada del modelo
export FLORENCE2_MODEL_PATH="/ruta/a/tu/modelo"

# Configuración de memoria CUDA
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:512"
```

## 🔧 Optimizaciones GPU

### RTX 4090 Optimizado
```python
# TF32 habilitado automáticamente
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

# Gestión de memoria optimizada
torch.backends.cuda.caching_allocator_settings = "max_split_size_mb:512"
torch.backends.cudnn.benchmark = True
```

### Rendimiento Esperado
- **RTX 4090**: ~2-3 segundos por imagen
- **RTX 3080**: ~3-5 segundos por imagen
- **CPU**: ~30-60 segundos por imagen

## 📁 Estructura del Proyecto

```
stockprep-pro/
├── src/
│   ├── core/                 # Núcleo del sistema
│   │   ├── model_manager.py  # Gestión del modelo
│   │   ├── image_processor.py # Procesamiento de imágenes
│   │   └── batch_engine.py   # Motor de procesamiento en lote
│   ├── gui/                  # Interfaces gráficas
│   │   ├── modern_gui_win11.py      # PySide6 Windows 11
│   │   ├── modern_gui_stockprep.py  # Tkinter clásico
│   │   └── components/       # Componentes reutilizables
│   ├── output/               # Gestión de salida
│   │   └── output_handler_v2.py
│   └── utils/                # Utilidades
│       └── keyword_extractor.py
├── models/                   # Modelos de IA
├── config/                   # Configuración
├── output/                   # Archivos de salida
└── docs/                     # Documentación
```

## 🎯 Casos de Uso

### 📸 **Fotógrafos Profesionales**
- Catalogación automática de portfolios
- Generación de metadatos descriptivos
- Organización inteligente de colecciones

### 🎨 **Artistas Digitales**
- Descripción de obras de arte
- Extracción de elementos visuales
- Documentación de procesos creativos

### 📚 **Bibliotecas y Archivos**
- Indexación automática de imágenes
- Búsqueda por contenido visual
- Catalogación masiva de colecciones

### 🏢 **Empresas**
- Procesamiento de inventarios visuales
- Análisis de productos
- Automatización de workflows

## 🤝 Contribuir

### Reportar Bugs
1. Usar el [issue tracker](https://github.com/tu-usuario/stockprep-pro/issues)
2. Incluir información del sistema
3. Adjuntar logs de error

### Solicitar Funciones
1. Crear issue con etiqueta `enhancement`
2. Describir caso de uso
3. Proponer implementación

### Contribuir Código
1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcion`
3. Commit cambios: `git commit -am 'Agregar nueva función'`
4. Push a la rama: `git push origin feature/nueva-funcion`
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- **Microsoft** por Florence-2
- **Hugging Face** por Transformers
- **PySide6** por la interfaz moderna
- **Comunidad open source** por las contribuciones

## 📞 Soporte

- **Documentación**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/tu-usuario/stockprep-pro/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/tu-usuario/stockprep-pro/discussions)

---

**Desarrollado con ❤️ para la comunidad de IA**

*StockPrep Pro v2.0 - Potenciando la creatividad con IA* 