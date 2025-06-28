# 📦 Guía de Instalación - StockPrep Pro v2.0

## 🎯 Requisitos del Sistema

### **Requisitos Mínimos**
- **Sistema Operativo**: Windows 10/11, Linux, macOS
- **Python**: 3.8 o superior
- **RAM**: 8GB mínimo
- **Almacenamiento**: 10GB de espacio libre

### **Requisitos Recomendados**
- **GPU**: NVIDIA RTX 30xx/40xx con 8GB+ VRAM
- **RAM**: 16GB o más
- **Almacenamiento**: SSD con 20GB+ de espacio libre
- **CUDA**: 12.1 o superior (para GPU)

## 🚀 Instalación Rápida

### **Opción 1: Instalación Automática (Recomendada)**

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/stockprep-pro.git
cd stockprep-pro

# 2. Ejecutar instalación automática
python setup_stockprep.py
```

### **Opción 2: Instalación Manual**

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/stockprep-pro.git
cd stockprep-pro

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Instalar PySide6 (para interfaz moderna)
pip install PySide6
```

## 🔧 Configuración de GPU (Opcional)

### **Verificar CUDA**
```bash
# Verificar si CUDA está disponible
python -c "import torch; print(f'CUDA disponible: {torch.cuda.is_available()}')"
```

### **Instalar PyTorch con CUDA**
```bash
# Para CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Para CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### **Verificar Instalación GPU**
```python
import torch
print(f"PyTorch versión: {torch.__version__}")
print(f"CUDA disponible: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name()}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
```

## 📥 Descarga del Modelo

### **Descarga Automática**
El modelo se descarga automáticamente en la primera ejecución.

### **Descarga Manual**
```python
from src.core.model_manager import Florence2Manager

# Descargar modelo manualmente
manager = Florence2Manager()
manager.cargar_modelo()
```

### **Ubicación del Modelo**
- **Windows**: `%USERPROFILE%\.cache\huggingface\hub`
- **Linux/Mac**: `~/.cache/huggingface/hub`

## 🧪 Verificar Instalación

### **Test Básico**
```bash
# Ejecutar test de sistema
python test_system.py
```

### **Test de GPU**
```bash
# Verificar optimizaciones GPU
python test_gpu_model.py
```

### **Test de Interfaz**
```bash
# Probar interfaz gráfica
python main.py
```

## ⚙️ Configuración Avanzada

### **Variables de Entorno**
```bash
# Configurar ruta personalizada del modelo
export FLORENCE2_MODEL_PATH="/ruta/a/tu/modelo"

# Configurar memoria CUDA
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:512"

# Configurar nivel de logging
export STOCKPREP_LOG_LEVEL="INFO"
```

### **Archivo de Configuración**
Editar `config/settings.yaml`:
```yaml
modelo:
  nombre: Florence-2-large-ft-safetensors
  ruta_local: models/Florence-2-large-ft-safetensors
  dtype: float32
  device: auto

ruta_salida: output/
formato_salida: JSON
exportar_txt: true
copiar_renombrar: true

gui:
  preferida: pyside6
  fallback: tkinter
```

## 🐛 Solución de Problemas

### **Error: CUDA no disponible**
```bash
# Verificar drivers NVIDIA
nvidia-smi

# Reinstalar PyTorch con CUDA
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### **Error: PySide6 no disponible**
```bash
# Instalar PySide6
pip install PySide6

# O usar Tkinter como fallback
python main.py --gui tkinter
```

### **Error: Memoria insuficiente**
```python
# Reducir batch size en config/settings.yaml
modelo:
  batch_size: 1
  max_memory: 0.8
```

### **Error: Modelo no descarga**
```bash
# Limpiar cache de Hugging Face
rm -rf ~/.cache/huggingface/hub

# Descargar manualmente
python -c "from transformers import AutoModel; AutoModel.from_pretrained('microsoft/florence2-large-ft')"
```

## 📋 Checklist de Instalación

- [ ] Python 3.8+ instalado
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] PySide6 instalado (opcional)
- [ ] CUDA configurado (opcional)
- [ ] Modelo descargado
- [ ] Test de sistema ejecutado
- [ ] Interfaz gráfica funcionando

## 🆘 Soporte

Si encuentras problemas durante la instalación:

1. **Revisar logs**: Los logs se guardan en `logs/`
2. **Verificar requisitos**: Ejecutar `python test_system.py`
3. **Consultar documentación**: Revisar otros archivos en `docs/`
4. **Crear issue**: Reportar en [GitHub Issues](https://github.com/tu-usuario/stockprep-pro/issues)

---

**¡Listo para usar StockPrep Pro v2.0! 🚀** 