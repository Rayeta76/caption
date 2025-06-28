# StockPrep - Generador de Descripciones de Imágenes con IA

StockPrep es una aplicación de escritorio que utiliza el modelo de inteligencia artificial **Florence-2** para generar automáticamente descripciones detalladas de imágenes, detectar objetos y extraer palabras clave. Perfecto para procesar lotes de imágenes y crear contenido descriptivo para stock photography, catálogos de productos, o cualquier colección de imágenes.

## 🌟 Características Principales

- **Interfaz gráfica intuitiva** construida con Tkinter
- **Procesamiento por lotes** de múltiples imágenes
- **Descripciones automáticas** generadas con Florence-2
- **Detección de objetos** en las imágenes
- **Extracción de palabras clave** automática
- **Renombrado inteligente** de archivos basado en el contenido
- **Múltiples formatos de salida**: JSON, CSV, XML
- **Generación de archivos de texto** con metadatos por imagen
- **Monitoreo de memoria en tiempo real**
- **Procesamiento asíncrono** sin bloquear la interfaz

## 🗂️ Estructura del Proyecto

```
Caption/
├── main.py                    # Archivo principal de la aplicación
├── requirements.txt           # Dependencias de Python
├── LICENSE                    # Licencia MIT
├── README.md                  # Esta documentación
├── verificar_instalacion.py   # Script para verificar la instalación
├── config/
│   └── settings.yaml         # Configuración del proyecto
├── src/
│   ├── core/                 # Lógica principal del procesamiento
│   │   ├── __init__.py
│   │   ├── model_manager.py  # Gestión del modelo Florence-2
│   │   ├── image_processor.py # Procesamiento de imágenes
│   │   └── batch_engine.py   # Motor de procesamiento por lotes
│   ├── gui/                  # Interfaz gráfica de usuario
│   │   ├── __init__.py
│   │   └── main_window.py    # Ventana principal de la aplicación
│   ├── io/                   # Entrada y salida de datos
│   │   └── output_handler.py # Manejo de archivos de salida
│   └── utils/                # Utilidades generales
│       └── __init__.py
├── models/                   # Modelos de IA (descargados localmente)
│   ├── Florence-2-large-ft-safetensors/  # Modelo optimizado (recomendado)
│   └── Florence2-large/                  # Modelo original
├── output/                   # Carpeta de salida predeterminada
├── temp/                     # Archivos temporales
└── config_safetensors.py     # Herramientas de configuración del modelo
```

## 🚀 Instalación y Configuración

### Prerrequisitos

- **Python 3.8+** (se recomienda Python 3.11)
- **CUDA** (opcional, para aceleración con GPU)
- **Git LFS** (para descargar los modelos)

### Instalación Paso a Paso

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/Caption.git
   cd Caption
   ```

2. **Crea un entorno virtual (recomendado):**
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En Linux/Mac:
   source venv/bin/activate
   ```

3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Descarga el modelo Florence-2:**
   ```bash
   # Opción 1: Modelo optimizado con safetensors (recomendado)
   git lfs clone https://huggingface.co/microsoft/Florence-2-large-ft models/Florence-2-large-ft-safetensors
   
   # Opción 2: Modelo original
   git lfs clone https://huggingface.co/microsoft/Florence-2-large models/Florence2-large
   ```

5. **Verifica la instalación:**
   ```bash
   python verificar_instalacion.py
   ```

## 🎯 Uso de la Aplicación

### Ejecutar StockPrep

```bash
python main.py
```

### Flujo de Trabajo

1. **Cargar el Modelo**: Presiona el botón "1. Cargar Modelo Florence-2" y espera a que se complete la carga
2. **Seleccionar Imágenes**: Elige la carpeta que contiene las imágenes a procesar
3. **Configurar Opciones**:
   - Formato de salida (JSON, CSV, XML)
   - Activar/desactivar detección de objetos
   - Activar/desactivar renombrado automático
4. **Procesar**: Presiona "2. Procesar Imágenes" y observa el progreso en tiempo real

### Formatos de Imagen Soportados

- **JPG/JPEG**
- **PNG**
- **BMP**
- **WEBP**

## ⚙️ Configuración

El archivo `config/settings.yaml` permite personalizar el comportamiento de la aplicación:

```yaml
# Carpeta de salida predeterminada
ruta_salida: output/

# Formato de exportación predeterminado
formato_salida: JSON

# Generar archivos .txt individuales
exportar_txt: true

# Configuración del modelo Florence-2
modelo:
  nombre: Florence-2-large
  tipo: safetensors
  ruta_local: models/Florence-2-large-ft-safetensors
  dtype: float32
  flash_attn_enabled: false  # Desactivado para compatibilidad con Windows
```

## 📋 Resultados y Salidas

### Archivos Generados

1. **Archivo de resultados**: `stockprep_resultados_YYYYMMDD_HHMMSS.json/csv/xml`
2. **Imágenes renombradas**: Copiadas a la carpeta de salida con nombres descriptivos
3. **Archivos de texto individuales**: Un archivo `.txt` por imagen con metadatos completos

### Estructura de Resultados (JSON)

```json
{
  "metadata": {
    "total_imagenes": 25,
    "fecha_procesamiento": "2024-01-15T10:30:00",
    "modelo": "Florence-2-large-ft-safetensors",
    "formato": "JSON"
  },
  "resultados": [
    {
      "archivo": "imagen001.jpg",
      "descripcion": "A beautiful sunset over a tranquil lake with mountains in the background",
      "objetos": {
        "labels": ["sky", "water", "mountain", "sunset"]
      },
      "keywords": ["sunset", "lake", "mountain", "nature", "landscape"],
      "archivo_renombrado": "a-beautiful-sunset-over-a-tranquil-lake_001.jpg"
    }
  ]
}
```

## 🛠️ Dependencias Principales

### Librerías de IA y Procesamiento
- **transformers**: 4.52.1 - Modelo Florence-2
- **torch**: 2.1.1+cu121 - PyTorch con CUDA
- **torchvision**: 0.16.1+cu121 - Procesamiento de imágenes
- **pillow**: 10.4.0 - Manipulación de imágenes
- **safetensors**: 0.5.3 - Carga eficiente de modelos

### Interfaz y Utilidades
- **ttkbootstrap**: 1.13.11 - Interfaz gráfica moderna
- **pyyaml**: 6.0.2 - Configuración
- **psutil**: 7.0.0 - Monitoreo de sistema

## 🔧 Solución de Problemas

### Problemas Comunes

**Error de memoria insuficiente:**
- Reduce el tamaño del lote de procesamiento
- Cierra otras aplicaciones que consuman memoria
- Usa el modelo con `dtype: float16` en lugar de `float32`

**Modelo no se carga:**
- Verifica que la ruta en `config/settings.yaml` sea correcta
- Asegúrate de haber descargado completamente el modelo con Git LFS
- Comprueba que tengas suficiente espacio en disco

**Interfaz no responde:**
- La aplicación procesa en hilos separados, el procesamiento continúa en segundo plano
- Revisa el área de log para ver el progreso actual

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Reconocimientos

- **Microsoft** por el modelo Florence-2
- **Hugging Face** por la plataforma de modelos y transformers
- **PyTorch** por el framework de deep learning

## 📞 Soporte

Para reportar problemas o solicitar nuevas características, por favor usa el sistema de Issues de GitHub.

---

**¿Te resulta útil StockPrep?** ⭐ ¡Dale una estrella al repositorio! 