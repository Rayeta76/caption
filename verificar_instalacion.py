clsimport sys
import platform

print(f"Python: {sys.version}")
print(f"Plataforma: {platform.system()} {platform.release()}")

try:
    import torch
    print(f"\n✅ PyTorch: {torch.__version__}")
    print(f"   CUDA disponible: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print(f"   Versión CUDA de PyTorch: {torch.version.cuda}")
except ImportError:
    print("\n❌ PyTorch no instalado")

try:
    import transformers
    print(f"\n✅ Transformers: {transformers.__version__}")
except ImportError:
    print("\n❌ Transformers no instalado")

try:
    from PIL import Image
    print(f"\n✅ Pillow: {Image.__version__}")
except ImportError:
    print("\n❌ Pillow no instalado")

print("\n--------------------------------------------------")
if torch.cuda.is_available():
    print("✅ ¡Entorno listo para la aceleración por GPU! Estás listo para continuar.")
else:
    print("⚠️  Atención: PyTorch funciona, pero no puede detectar la GPU. El proceso será muy lento.")