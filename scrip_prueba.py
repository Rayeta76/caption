import torch
from transformers import AutoProcessor, AutoModelForCausalLM

# Verificar GPU
print("CUDA disponible:", torch.cuda.is_available())
print("Versión PyTorch:", torch.__version__)
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))
else:
    print("No GPU found")

# Cargar modelo Florence-2
try:
    model = AutoModelForCausalLM.from_pretrained(
        "mrhendrey/Florence-2-large-ft-safetensors",
        use_safetensors=True,
        trust_remote_code=True,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    print("✅ Modelo cargado correctamente")
except Exception as e:
    print("❌ Error:", str(e))
