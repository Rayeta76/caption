import torch
import PIL
import timm
import transformers

print(f"✅ PyTorch: {torch.__version__}")
print(f"CUDA disponible: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"CUDA versión: {torch.version.cuda}")

print(f"✅ Pillow: {PIL.__version__}")
print(f"✅ Transformers: {transformers.__version__}")
print(f"✅ Timm: {timm.__version__}")
