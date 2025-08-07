# 🚀 StockPrep Pro v2.0

Sistema inteligente de procesamiento de imágenes con IA usando Microsoft Florence-2.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-2.2%2B-red)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Características Principales

- 🤖 **Generación automática de captions** descriptivos con Florence-2
- 🎯 **Detección de objetos** con coordenadas precisas
- 🔍 **Extracción de keywords** inteligente con YAKE
- 💾 **Base de datos SQLite** integrada para búsquedas
- 📄 **3 archivos .txt separados**: caption, keywords, objects
- 🎨 **Interfaz moderna** estilo Windows 11 (PySide6) con fallback a Tkinter
- 📊 **Exportación múltiple**: JSON, CSV, XML
- 🌐 **Multiidioma**: Español, Inglés, Francés

## 🛠️ Instalación Rápida

### Opción 1: Script Automatizado (Recomendado)

```bash
# Windows
python setup_stockprep.py

# Linux/Mac
python3 setup_stockprep.py
```

El script:
- ✅ Verifica Python 3.9+
- ✅ Crea entorno virtual
- ✅ Instala todas las dependencias
- ✅ Crea estructura de carpetas
- ✅ Genera scripts de lanzamiento

### Opción 2: Instalación Manual

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/stockprep-pro.git
cd stockprep-pro

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Ejecutar
python main.py
```

## 📦 Modelo Florence-2

### Descargar el Modelo

1. Visita [Microsoft Florence-2 Large](https://huggingface.co/microsoft/Florence-2-large)
2. Descarga todos los archivos
3. Colócalos en `models/Florence-2-large-ft-safetensors/`

Archivos necesarios:
- `model.safetensors`
- `config.json`
- `tokenizer.json`
- `preprocessor_config.json`
- Otros archivos del modelo

## 🖥️ Uso

### 1. Iniciar la Aplicación

```bash
# Windows
run_stockprep.bat

# Linux/Mac
./run_stockprep.sh

# O directamente
python main.py
```

### 2. Cargar el Modelo

Click en "🤖 Cargar Modelo Florence-2" y esperar ~30 segundos.

### 3. Seleccionar Carpetas

- **Entrada**: Carpeta con tus imágenes
- **Salida**: Donde se guardarán los resultados

### 4. Configurar Opciones

- ✅ **Detectar objetos**: Activa detección con bounding boxes
- ✅ **Renombrar archivos**: Nombres descriptivos basados en contenido
- ✅ **Generar archivos .txt**: Crea los 3 archivos por imagen
- ✅ **Generar informe HTML**: Resumen visual de resultados

### 5. Procesar

Click en "🚀 Procesar Imágenes" y observa el progreso.

## 📁 Estructura de Salida

Para cada imagen `foto.jpg`:

```
salida/
├── a-woman-wearing-a-red-dress-standing-in-a-garden.jpg
├── a-woman-wearing-a-red-dress-standing-in-a-garden_caption.txt
├── a-woman-wearing-a-red-dress-standing-in-a-garden_keywords.txt
├── a-woman-wearing-a-red-dress-standing-in-a-garden_objects.txt
├── stockprep_resultados_20250625_143022.json
└── informe_procesamiento.html
```

### Contenido de los Archivos

**_caption.txt**:
```
A woman wearing a red dress standing in a garden surrounded by colorful flowers
```

**_keywords.txt**:
```
woman
red dress
garden
colorful flowers
standing
outdoor
nature
```

**_objects.txt**:
```
Objetos detectados:
----------------------------------------

1. person
   Posición: [125, 50, 380, 450]

2. dress
   Posición: [150, 120, 350, 400]

3. flower
   Posición: [20, 300, 100, 380]
```

## 🗄️ Base de Datos SQLite

### Estructura

```sql
CREATE TABLE images (
    id INTEGER PRIMARY KEY,
    file TEXT NOT NULL,
    caption TEXT,
    keywords TEXT,  -- JSON array
    objects TEXT,   -- JSON object
    created_at TIMESTAMP,
    width INTEGER,
    height INTEGER,
    renamed_file TEXT
);
```

### Consultas de Ejemplo

```python
from src.core.sqlite_database import SQLiteImageDatabase

db = SQLiteImageDatabase()

# Buscar por keyword
results = db.buscar_imagenes(keywords_contains="garden")

# Buscar por caption
results = db.buscar_imagenes(caption_contains="woman")

# Últimas 10 procesadas
results = db.buscar_imagenes(limit=10)
```

## 🔧 Crear Ejecutable (.exe)

```bash
# Instalar PyInstaller
pip install pyinstaller

# Generar ejecutable
pyinstaller stockprep.spec --noconfirm

# El .exe estará en dist/StockPrepPro.exe
```

## 🐳 GitHub Actions

El proyecto incluye workflow automático:

```yaml
# Se ejecuta en cada push a main
# Genera releases automáticas con el .exe
# Ver .github/workflows/build-exe.yml
```

## ⚙️ Configuración Avanzada

### config/settings.yaml

```yaml
modelo:
  nombre: Florence-2-large
  tipo: safetensors
  ruta_local: models/Florence-2-large-ft-safetensors
  dtype: float32
  
# Personalizar rutas
ruta_salida: output/
formato_salida: JSON
exportar_txt: true
```

### Variables de Entorno

```bash
# Modelo alternativo
export FLORENCE2_MODEL_PATH=/path/to/model

# GPU específica
export CUDA_VISIBLE_DEVICES=0

# Desactivar GPU
export CUDA_VISIBLE_DEVICES=-1
```

## 🚨 Solución de Problemas

### CUDA Out of Memory

```python
# Reducir uso de memoria en config
torch.cuda.empty_cache()
```

### Modelo no encontrado

1. Verificar ruta en `config/settings.yaml`
2. Confirmar que existe `model.safetensors`
3. Revisar permisos de lectura

### Antivirus bloquea el .exe

```powershell
# Windows Defender - Agregar excepción
Add-MpPreference -ExclusionPath "C:\StockPrepPro"
```

## 📊 Rendimiento

| GPU | VRAM | Velocidad | Batch Size |
|-----|------|-----------|------------|
| RTX 4090 | 24GB | ~120 img/min | 8 |
| RTX 3080 | 10GB | ~60 img/min | 4 |
| RTX 3060 | 12GB | ~40 img/min | 4 |
| CPU (i7) | RAM | ~5 img/min | 1 |

## 🤝 Contribuir

1. Fork el proyecto
2. Crea tu rama (`git checkout -b feature/NuevaCaracteristica`)
3. Commit cambios (`git commit -m 'Agregar característica'`)
4. Push a la rama (`git push origin feature/NuevaCaracteristica`)
5. Abre un Pull Request

## 📝 Licencia

MIT License - ver [LICENSE](LICENSE)

## 🙏 Agradecimientos

- Microsoft por el modelo Florence-2
- Comunidad de Hugging Face
- Desarrolladores de PyTorch
- Contribuidores del proyecto

---

**StockPrep Pro v2.0** - Desarrollado con ❤️ para profesionales del stock photography