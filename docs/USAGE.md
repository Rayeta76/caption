# 🎮 Guía de Uso - StockPrep Pro v2.0

## 🚀 Inicio Rápido

### **Ejecutar la Aplicación**
```bash
# Interfaz moderna (PySide6)
python main.py

# Interfaz clásica (Tkinter)
python main.py --gui tkinter

# Modo línea de comandos
python main.py --cli
```

## 🖥️ Interfaz Gráfica

### **Pestaña Principal**

#### **1. Cargar Modelo**
- Haz clic en **"🧠 Cargar Modelo Florence-2"**
- Espera a que el botón cambie a verde ✅
- El modelo se carga una sola vez por sesión

#### **2. Seleccionar Imágenes**
- **Imagen individual**: Haz clic en **"🖼️ Seleccionar Imagen"**
- **Carpeta completa**: Haz clic en **"📂 Seleccionar Carpeta de Imágenes"**

#### **3. Configurar Nivel de Detalle**
- **🟢 Mínimo**: Descripción rápida (10-15 palabras)
- **🟡 Medio**: Balanceado (20-40 palabras)
- **🔴 Largo**: Detallado (50+ palabras)

#### **4. Configurar Salida**
- **Carpeta de salida**: Selecciona dónde guardar resultados
- **Renombrar**: Activa para renombrar imágenes automáticamente

#### **5. Procesar**
- Haz clic en **"🚀 Procesar Imagen"** o **"🚀 Procesar X Imágenes"**
- Observa el progreso en tiempo real
- Los resultados aparecen en el panel derecho

### **Pestaña Historial**
- **Ver resultados anteriores**: Todos los procesamientos guardados
- **Actualizar**: Refrescar lista de resultados
- **Limpiar**: Eliminar historial completo

### **Pestaña Estadísticas**
- **Procesamiento**: Imágenes procesadas, tasa de éxito, tiempo promedio
- **Base de datos**: Registros, tamaño, última actualización

## 💻 Línea de Comandos

### **Uso Básico**
```python
from src.core.model_manager import Florence2Manager
from src.core.image_processor import ImageProcessor

# Inicializar
manager = Florence2Manager()
manager.cargar_modelo()

# Procesar imagen
processor = ImageProcessor(manager)
result = processor.process_image("imagen.jpg", "largo")

# Mostrar resultados
print(f"Descripción: {result['caption']}")
print(f"Keywords: {result['keywords']}")
print(f"Objetos: {result['objects']}")
```

### **Ejemplos CLI (terminal)**
```bash
# Windows (CMD)
python main.py --cli --image test_images\manual_test.jpg --detail largo

# Linux/Mac (Bash)
python main.py --cli --image test_images/manual_test.jpg --detail medio

# Niveles de detalle soportados: minimo | medio | largo
```

### **Procesamiento en Lote**
```python
from src.core.batch_engine import BatchEngine

# Configurar procesamiento en lote
# Nota: BatchEngine recibe un ImageProcessor y process_folder acepta solo la ruta
batch = BatchEngine(processor)
batch.process_folder("carpeta_imagenes/")
```

### **Configuración Personalizada**
```python
# Configuración avanzada de generación se asigna automáticamente por nivel de detalle.
# Para personalizar parámetros, modifica ImageProcessor._get_generation_params.
result = processor.process_image("imagen.jpg", "largo")
```

## 📊 Niveles de Detalle

### **🟢 Mínimo**
```python
# Configuración automática
{
    "max_new_tokens": 256,
    "do_sample": False,
    "num_beams": 2,
    "temperature": 0.7
}
```
**Ideal para**: Procesamiento rápido, catalogación básica

### **🟡 Medio**
```python
# Configuración automática
{
    "max_new_tokens": 512,
    "do_sample": True,
    "num_beams": 3,
    "temperature": 0.8,
    "top_p": 0.9
}
```
**Ideal para**: Descripciones balanceadas, uso general

### **🔴 Largo**
```python
# Configuración automática
{
    "max_new_tokens": 2048,
    "do_sample": True,
    "num_beams": 5,
    "temperature": 0.9,
    "length_penalty": 1.3,
    "min_length": 50
}
```
**Ideal para**: Descripciones detalladas, análisis profundo

## 📁 Formatos de Salida

### **Archivos Individuales**
```
output/
├── imagen1_caption.txt      # Descripción completa
├── imagen1_keywords.txt     # Keywords (una por línea)
├── imagen1_objects.txt      # Objetos detectados
├── imagen1.json            # Resultado completo en JSON
└── imagen1_renamed.jpg     # Imagen renombrada (si está activado)
```

### **Base de Datos SQLite**
```sql
-- Tabla de imágenes procesadas
SELECT * FROM imagenes WHERE fecha > '2025-01-01';

-- Estadísticas
SELECT COUNT(*) as total, AVG(LENGTH(caption)) as avg_length 
FROM imagenes;
```

### **Exportación Masiva**
```python
from src.output.output_handler_v2 import OutputHandlerV2

handler = OutputHandlerV2()

# Exportar a JSON
handler.export_to_json("output/resultados.json")

# Exportar a CSV
handler.export_to_csv("output/resultados.csv")

# Exportar a XML
handler.export_to_xml("output/resultados.xml")
```

## ⚙️ Configuración Avanzada

### **Archivo de Configuración**
```yaml
# config/settings.yaml
modelo:
  nombre: Florence-2-large-ft-safetensors
  ruta_local: models/Florence-2-large-ft-safetensors
  dtype: float32
  device: auto
  max_memory: 0.9

procesamiento:
  batch_size: 1
  num_workers: 0
  prefetch_factor: 2

salida:
  ruta: output/
  formato: JSON
  exportar_txt: true
  copiar_renombrar: true
  comprimir: false

gui:
  preferida: pyside6
  fallback: tkinter
  tema: win11
  idioma: es
```

### **Variables de Entorno**
```bash
# Configurar ruta del modelo
export FLORENCE2_MODEL_PATH="/ruta/a/tu/modelo"

# Configurar memoria CUDA
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:512"

# Configurar logging
export STOCKPREP_LOG_LEVEL="DEBUG"
```

## 🎯 Casos de Uso Prácticos

### **📸 Fotógrafo Profesional**
```python
# Procesar portfolio completo
from src.core.image_processor import ImageProcessor
from src.core.batch_engine import BatchEngine

processor = ImageProcessor(manager)
batch = BatchEngine(processor)
batch.process_folder("portfolio/")

# Generar metadatos para web
from src.output.output_handler_v2 import OutputHandlerV2
handler = OutputHandlerV2()
handler.export_to_json("portfolio_metadata.json")
```

### **🎨 Artista Digital**
```python
# Analizar obra de arte
result = processor.process_image("obra_arte.jpg", "largo")

# Extraer elementos visuales
print("Elementos detectados:")
for obj in result['objects']:
    print(f"- {obj['name']}: {obj['confidence']:.2f}")
```

### **📚 Biblioteca**
```python
# Procesar colección completa
from src.core.image_processor import ImageProcessor
from src.core.batch_engine import BatchEngine

processor = ImageProcessor(manager)
batch = BatchEngine(processor)
batch.process_folder("coleccion/")

# Exportar índice de búsqueda (JSON)
from src.output.output_handler_v2 import OutputHandlerV2
handler = OutputHandlerV2()
handler.export_to_json("indice_busqueda.json")
```

## 🔧 Optimizaciones de Rendimiento

### **GPU Optimizado**
```python
# Verificar optimizaciones
import torch
print(f"TF32: {torch.backends.cuda.matmul.allow_tf32}")
print(f"cuDNN: {torch.backends.cudnn.benchmark}")

# Configurar memoria
torch.cuda.empty_cache()
torch.backends.cuda.caching_allocator_settings = "max_split_size_mb:512"
```

### **Procesamiento Eficiente**
```python
# Usar procesamiento en lote para múltiples imágenes
from src.core.image_processor import ImageProcessor
from src.core.batch_engine import BatchEngine

processor = ImageProcessor(manager)
batch = BatchEngine(processor)
batch.process_folder("imagenes/")
```

## 🐛 Solución de Problemas

### **Error: "Modelo no cargado"**
```python
# Verificar carga del modelo
if not manager.modelo_cargado:
    manager.cargar_modelo()
```

### **Error: "Memoria insuficiente"**
```python
"""
La configuración avanzada de generación se asigna automáticamente por nivel de detalle.
Si necesitas ajustar parámetros como `max_new_tokens` o `num_beams`, edita
`ImageProcessor._get_generation_params`.
"""
```

### **Error: "CUDA out of memory"**
```python
# Limpiar memoria GPU
torch.cuda.empty_cache()

# Usar CPU como fallback
# La selección de dispositivo es automática; si no hay GPU, el sistema usa CPU.
```

## 📞 Soporte

### **Logs de Debug**
```python
# El logging global se configura desde main.py leyendo STOCKPREP_LOG_LEVEL
# Salida en consola y en logs/stockprep.log (rotación)
```

### **Test de Sistema**
```bash
# Ejecutar tests completos
python test_system.py
python test_gpu_model.py
python test_detail_levels.py
```

---

**¡Disfruta usando StockPrep Pro v2.0! 🚀** 