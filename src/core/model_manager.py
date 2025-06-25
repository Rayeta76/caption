"""
Gestor del modelo Florence‑2 (versión parcheada para RTX 4090 y dtype coherente)
"""

from pathlib import Path
from unittest.mock import patch

import gc
import os

import torch
from transformers import AutoModelForCausalLM, AutoProcessor
from transformers.dynamic_module_utils import get_imports

# Activar optimizaciones Tensor Cores (TF32) – opcional, no afecta al dtype elegido
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True


class Florence2Manager:
    """Carga y gestiona un checkpoint local de Florence‑2."""

    def __init__(self):
        self.model = None
        self.processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_id = str(
            Path("E:/Proyectos/Caption/models/Florence-2-large-ft-safetensors").resolve()
        )

    # ---------------------------------------------------------------------
    #  Utilidad para evitar que Flash‑Attn se cargue si no está disponible
    # ---------------------------------------------------------------------
    def _fixed_get_imports(self, filename):
        imports = get_imports(filename)
        if str(filename).endswith("modeling_florence2.py") and "flash_attn" in imports:
            imports = [imp for imp in imports if imp != "flash_attn"]
        return imports


    # ---------------------------------------------------------------------
    #  Carga de modelo y processor
    # ---------------------------------------------------------------------
    def cargar_modelo(self, callback=None):
        """Carga Florence‑2 en **float32** para evitar errores de tipo mezclado."""
        try:
            if callback:
                callback("🧠 Cargando modelo desde carpeta local (dtype float32)…")

            with patch(
                "transformers.dynamic_module_utils.get_imports", self._fixed_get_imports
            ):
                # Processor (tokenizer + image processor)
                self.processor = AutoProcessor.from_pretrained(
                    self.model_id, trust_remote_code=True
                )

                # Modelo – TODO: usa siempre float32 para coherencia con las entradas
                self.model = (
                    AutoModelForCausalLM.from_pretrained(
                        self.model_id,
                        trust_remote_code=True,
                        use_safetensors=True,
                        torch_dtype=torch.float32,  #  <-- forzamos fp32
                        device_map="auto",
                    )
                    .to(self.device)
                    .eval()
                )

                torch.cuda.empty_cache()

                if callback:
                    callback("✅ Modelo cargado correctamente")
                    if self.device == "cuda":
                        callback(
                            f"💾 Uso de VRAM: {torch.cuda.memory_allocated() / 1024 ** 3:.1f} GB"
                        )
            return True

        except Exception as exc:
            if callback:
                callback(f"❌ Error al cargar modelo: {exc}")
            return False

    # ------------------------------------------------------------------
    #  Liberar recursos
    # ------------------------------------------------------------------
    def descargar_modelo(self):
        if self.model is not None:
            del self.model
            self.model = None
        if self.processor is not None:
            del self.processor
            self.processor = None

        if self.device == "cuda":
            torch.cuda.empty_cache()
        gc.collect()

    # ------------------------------------------------------------------
    #  Info de memoria
    # ------------------------------------------------------------------
    def obtener_uso_memoria(self):
        if self.device == "cuda":
            alloc = torch.cuda.memory_allocated() / 1024 ** 3
            reserv = torch.cuda.memory_reserved() / 1024 ** 3
            return f"GPU: {alloc:.1f} GB usado / {reserv:.1f} GB reservado"
        return "Modo CPU"
