"""
Gestor del modelo Florence-2
Este archivo maneja la carga y descarga del modelo de IA
"""
import torch
from transformers import AutoModelForCausalLM, AutoProcessor
from unittest.mock import patch
from transformers.dynamic_module_utils import get_imports
import gc

class Florence2Manager:
    """Clase que gestiona el modelo Florence-2"""
    
    def __init__(self):
        """Inicializa el gestor del modelo"""
        self.model = None
        self.processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_id = "models/florence-2-safetensors-local"
        
    def fixed_get_imports(self, filename):
        """Arregla el problema de flash_attn en Windows"""
        if not str(filename).endswith("modeling_florence2.py"):
            return get_imports(filename)
        imports = get_imports(filename)
        if "flash_attn" in imports:
            imports.remove("flash_attn")
        return imports
    
    def cargar_modelo(self, callback=None):
        """
        Carga el modelo Florence-2
        callback: función para actualizar el progreso
        """
        try:
            if callback:
                callback("Iniciando carga del modelo...")
            
            # Aplicar el parche para Windows
            with patch("transformers.dynamic_module_utils.get_imports", self.fixed_get_imports):
                if callback:
                    callback("Descargando modelo (puede tardar varios minutos)...")
                
                # Cargar el procesador
                self.processor = AutoProcessor.from_pretrained(
                    self.model_id,
                    trust_remote_code=True
                )
                
                if callback:
                    callback("Cargando modelo en memoria...")
                
                # Cargar el modelo
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_id,
                    trust_remote_code=True,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    attn_implementation="sdpa"
                ).to(self.device)
                
                # Poner el modelo en modo evaluación
                self.model.eval()
                
                if callback:
                    callback("✅ Modelo cargado correctamente")
                
                return True
                
        except Exception as e:
            if callback:
                callback(f"❌ Error al cargar modelo: {str(e)}")
            return False
    
    def descargar_modelo(self):
        """Libera el modelo de la memoria"""
        if self.model is not None:
            del self.model
            self.model = None
        if self.processor is not None:
            del self.processor
            self.processor = None
        
        # Limpiar memoria GPU
        if self.device == "cuda":
            torch.cuda.empty_cache()
        gc.collect()
    
    def obtener_uso_memoria(self):
        """Obtiene información sobre el uso de memoria"""
        if self.device == "cuda":
            allocated = torch.cuda.memory_allocated() / 1024**3
            reserved = torch.cuda.memory_reserved() / 1024**3
            return f"GPU: {allocated:.1f}GB usado de {reserved:.1f}GB reservado"
        return "Modo CPU"