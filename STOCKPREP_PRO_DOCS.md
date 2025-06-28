# StockPrep Pro - Sistema Inteligente de Procesamiento de Imágenes

## 📋 Descripción General

StockPrep Pro es un sistema todo-en-uno que utiliza el modelo **Microsoft Florence-2** para procesar imágenes de forma inteligente, generando:

- 🤖 **Captions descriptivos** usando IA
- 🎯 **Detección de objetos** con coordenadas
- 🔍 **Extracción de keywords** relevantes con YAKE
- 💾 **Almacenamiento en SQLite** para búsquedas posteriores
- 📄 **Exportación múltiple** (JSON, CSV, XML)

## 🚀 Características Principales

### 1. Procesamiento con Florence-2
- Carga modelos en formato `.safetensors`
- Compatible con GPU (CUDA) y CPU
- Procesamiento por lotes optimizado

### 2. Extracción de Información
- **Caption**: Descripción detallada de la imagen
- **Keywords**: Palabras clave extraídas con YAKE
- **Objects**: Lista de objetos detectados con bounding boxes

### 3. Almacenamiento de Resultados
- **Archivos .txt separados**:
  - `imagen_caption.txt`: Descripción
  - `imagen_keywords.txt`: Palabras clave (una por línea)
  - `imagen_objects.txt`: Objetos detectados
- **Base de datos SQLite** con índices para búsquedas rápidas
- **Renombrado inteligente** basado en el contenido

### 4. Interfaz Moderna
- **Estilo Windows 11** con PySide6
- **Fallback a Tkinter** si PySide6 no está disponible
- **Progreso en tiempo real** con estadísticas
- **Soporte multiidioma** (ES, EN, FR)

## 📦 Instalación

### Opción 1: Desde Código Fuente

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/stockprep-pro.git
cd stockprep-pro

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python main.py
```

### Opción 2: Ejecutable Pre-compilado

1. Descargar `StockPrepPro-Windows.zip` desde [Releases](https://github.com/tu-usuario/stockprep-pro/releases)
2. Extraer el archivo
3. Ejecutar `StockPrepPro.exe`

## 🛠️ Configuración

### Configuración del Modelo

Editar `config/settings.yaml`:

```yaml
modelo:
  nombre: Florence-2-large
  tipo: safetensors
  ruta_local: models/Florence-2-large-ft-safetensors
  dtype: float32
```

### Variables de Entorno

```bash
# Ruta alternativa al modelo
export FLORENCE2_MODEL_PATH=/ruta/a/florence2

# Configurar CUDA (opcional)
export CUDA_VISIBLE_DEVICES=0
```

## 📖 Uso

### 1. Cargar el Modelo
- Click en "🤖 Cargar Modelo Florence-2"
- Esperar a que se cargue (primera vez ~30s)

### 2. Seleccionar Carpetas
- **Entrada**: Carpeta con imágenes a procesar
- **Salida**: Donde se guardarán los resultados

### 3. Configurar Opciones
- ✅ **Detectar objetos**: Activa detección de objetos
- ✅ **Renombrar archivos**: Renombra según contenido
- ✅ **Generar archivos .txt**: Crea los 3 archivos
- ✅ **Generar informe HTML**: Crea resumen visual

### 4. Procesar
- Click en "🚀 Procesar Imágenes"
- Ver progreso en tiempo real
- Revisar resultados en carpeta de salida

## 🔧 Construcción del Ejecutable

### Requisitos
- Python 3.11+
- PyInstaller 6.0+

### Generar .exe

```bash
# Instalar PyInstaller
pip install pyinstaller

# Generar ejecutable
pyinstaller stockprep.spec --noconfirm

# El ejecutable estará en dist/StockPrepPro.exe
```

### GitHub Actions

El proyecto incluye workflow automático que genera el .exe en cada push:

```yaml
# .github/workflows/build-exe.yml
- Se ejecuta en cada push a main
- Genera releases automáticas en tags
- Soporta Windows y Linux
```

## ⚠️ Riesgos y Mitigaciones

### 1. VRAM Insuficiente

**Riesgo**: El modelo Florence-2 requiere ~4-6GB VRAM

**Mitigaciones**:
- Detección automática GPU/CPU
- Fallback a CPU si GPU no disponible
- Liberación de memoria entre lotes
- Configuración de batch_size ajustable

```python
# El sistema detecta automáticamente
if torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"
```

### 2. Antivirus / Windows Defender

**Riesgo**: Falsos positivos con ejecutables PyInstaller

**Mitigaciones**:
- Firmar digitalmente el ejecutable
- Agregar a excepciones del antivirus
- Usar instalador MSI (futuro)
- Documentar el proceso para usuarios

```powershell
# Agregar excepción en Windows Defender
Add-MpPreference -ExclusionPath "C:\StockPrepPro"
```

### 3. Drivers CUDA Incompatibles

**Riesgo**: Errores si CUDA/cuDNN no coinciden

**Mitigaciones**:
- Incluir versión CPU de PyTorch
- Verificación de compatibilidad al inicio
- Instrucciones claras de instalación
- Logs detallados de errores

```python
# Verificación automática
try:
    import torch
    print(f"PyTorch: {torch.__version__}")
    print(f"CUDA disponible: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA versión: {torch.version.cuda}")
except Exception as e:
    print(f"Error verificando CUDA: {e}")
```

### 4. Tamaño del Ejecutable

**Riesgo**: El .exe puede ser >2GB con modelo incluido

**Mitigaciones**:
- Opción de descarga separada del modelo
- Compresión UPX activada
- Build sin modelo (descarga al primer uso)
- Versión "portable" en carpeta

### 5. Permisos de Escritura

**Riesgo**: Errores al guardar en carpetas protegidas

**Mitigaciones**:
- Verificación de permisos antes de procesar
- Carpeta de salida por defecto en usuario
- Mensajes de error claros
- Opción de cambiar ubicación

### 6. Memoria RAM

**Riesgo**: Consumo alto con imágenes grandes

**Mitigaciones**:
- Redimensionado automático si >2048px
- Procesamiento secuencial (no paralelo)
- Liberación de memoria agresiva
- Límite configurable de tamaño

```python
# Redimensionar si es muy grande
if max(image.size) > 2048:
    image.thumbnail((2048, 2048), Image.Resampling.LANCZOS)
```

## 🐛 Solución de Problemas

### Error: "No se puede cargar el modelo"

1. Verificar ruta en `config/settings.yaml`
2. Comprobar que existe `model.safetensors`
3. Revisar logs para más detalles

### Error: "CUDA out of memory"

1. Cerrar otras aplicaciones GPU
2. Reducir batch_size
3. Usar modo CPU: eliminar CUDA_VISIBLE_DEVICES

### Error: "DLL no encontrada"

1. Instalar Visual C++ Redistributables
2. Verificar versión de Python (3.11 recomendado)
3. Reinstalar PyTorch

### El antivirus bloquea el ejecutable

1. Desactivar temporalmente para extraer
2. Agregar carpeta a excepciones
3. Usar versión desde código fuente

## 📊 Estructura de la Base de Datos

### Tabla: images

```sql
CREATE TABLE images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file TEXT NOT NULL,
    file_path TEXT NOT NULL,
    caption TEXT,
    keywords TEXT,  -- JSON array
    objects TEXT,   -- JSON object
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    width INTEGER,
    height INTEGER,
    file_size INTEGER,
    renamed_file TEXT,
    error TEXT
);
```

### Consultas de Ejemplo

```python
# Buscar imágenes con palabra clave
db.buscar_imagenes(keywords_contains="persona")

# Buscar por caption
db.buscar_imagenes(caption_contains="playa")

# Últimas 10 procesadas
db.buscar_imagenes(limit=10)
```

## 🔄 Actualizaciones Futuras

- [ ] Soporte para más modelos (BLIP-2, LLaVA)
- [ ] API REST para integración
- [ ] Procesamiento en la nube
- [ ] Búsqueda por similitud de imágenes
- [ ] Edición de metadatos post-procesamiento
- [ ] Exportación a plataformas de stock

## 📄 Licencia

MIT License - Ver archivo LICENSE

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea tu rama (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Soporte

- 📧 Email: soporte@stockprep.pro
- 💬 Discord: [Unirse al servidor](https://discord.gg/stockprep)
- 🐛 Issues: [GitHub Issues](https://github.com/tu-usuario/stockprep-pro/issues)

---

Desarrollado con ❤️ para profesionales del stock photography