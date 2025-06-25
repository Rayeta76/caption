"""
Configuracion para usar Florence-2 Safetensors
"""
# En tu model_manager.py, cambia la linea del modelo a:
MODEL_ID = "mrhendrey/Florence-2-large-ft-safetensors"

# O usa este codigo completo:
from transformers import AutoModelForCausalLM, AutoProcessor
import torch

def cargar_florence2_safetensors():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Procesador del modelo original
    processor = AutoProcessor.from_pretrained(
        "microsoft/Florence-2-large",
        trust_remote_code=True
    )
    
    # Modelo safetensors (m�s compatible)
    model = AutoModelForCausalLM.from_pretrained(
        "mrhendrey/Florence-2-large-ft-safetensors",
        trust_remote_code=True,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32
    ).to(device)
    
    return processor, model
