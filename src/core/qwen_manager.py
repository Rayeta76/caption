import gc
import json
import os
import time
from pathlib import Path

import torch
from PIL import Image
from transformers import AutoProcessor
from qwen_vl_utils import process_vision_info
try:
    from src.utils.bilingual_metadata import parse_bilingual_model_output
except ImportError:
    from utils.bilingual_metadata import parse_bilingual_model_output

class Qwen2VLManager:
    """
    Gestor unificado del modelo Qwen2-VL (7B) optimizado para RTX 4090.
    Utiliza el patrón Singleton para asegurar una única instancia en memoria.
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Qwen2VLManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized') and self.initialized:
            return
            
        self.model = None
        self.processor = None
        self.model_id = "Qwen/Qwen2-VL-7B-Instruct"
        self.display_name = "Qwen2-VL 7B"
        self.max_pixels = 512 * 28 * 28
        self.max_new_tokens = 520
        
        # Detección de dispositivo optimizada
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.bfloat16 if self.device == "cuda" else torch.float32
        
        self.initialized = True

    def configure_model(
        self,
        model_id: str,
        display_name: str | None = None,
        max_pixels: int | None = None,
        max_new_tokens: int | None = None,
    ):
        """Configure the Hugging Face model before loading it."""
        model_changed = model_id and model_id != self.model_id
        if model_changed and (self.model is not None or self.processor is not None):
            self.descargar_modelo()

        if model_id:
            self.model_id = model_id
        self.display_name = display_name or self.model_id
        if max_pixels:
            self.max_pixels = max_pixels
        if max_new_tokens:
            self.max_new_tokens = max_new_tokens

    def cargar_modelo(self, callback=None):
        """Carga el modelo en memoria VRAM usando bfloat16 y device_map='auto'."""
        if self.model is not None and self.processor is not None:
            if callback: callback("✅ Qwen2-VL ya está activo en memoria.")
            return True
            
        try:
            if callback: callback(f"📝 Cargando procesador de {self.display_name}...")
            self.processor = AutoProcessor.from_pretrained(self.model_id)
            
            if callback: callback(f"🔄 Cargando pesos base de {self.model_id} en {self.dtype}...")
            model_class = self._resolve_model_class()
            # Auto-mapping aprovecha al máximo la arquitectura accelerate en la GPU
            self.model = model_class.from_pretrained(
                self.model_id,
                torch_dtype=self.dtype,
                device_map="auto"
            )
            
            if callback: callback(f"✅ Modelo {self.display_name} cargado y listo.")
            return True
        except Exception as e:
            if callback: callback(f"❌ Error crítico al cargar {self.display_name}: {e}")
            return False

    def _resolve_model_class(self):
        """Return the proper transformers class for the selected Qwen VL family."""
        if "Qwen2.5-VL" in self.model_id:
            try:
                from transformers import Qwen2_5_VLForConditionalGeneration

                return Qwen2_5_VLForConditionalGeneration
            except ImportError as exc:
                raise ImportError(
                    "Qwen2.5-VL requiere una version de transformers con "
                    "Qwen2_5_VLForConditionalGeneration."
                ) from exc

        from transformers import Qwen2VLForConditionalGeneration

        return Qwen2VLForConditionalGeneration

    def descargar_modelo(self, callback=None):
        """Libera la memoria VRAM destruyendo los punteros del modelo y forzando GC."""
        if self.model is not None:
            del self.model
            self.model = None
        if self.processor is not None:
            del self.processor
            self.processor = None
        
        if self.device == "cuda":
            torch.cuda.empty_cache()
            
        gc.collect()
        if callback: callback("🧹 Qwen2-VL descargado. Memoria VRAM liberada.")

    def get_device_info(self) -> dict:
        """Devuelve información del dispositivo para compatibilidad con la GUI."""
        return {"device": self.device}

    def get_gpu_name(self) -> str:
        """Devuelve el nombre de la GPU si está disponible."""
        if self.device == "cuda":
            return torch.cuda.get_device_name(0)
        return "CPU"

    def _run_image_prompt(
        self,
        imagen_path: str,
        prompt: str,
        max_new_tokens: int | None = None,
        max_pixels: int | None = None,
    ) -> str:
        """Run a deterministic image+text prompt and return raw model text."""
        if not self.model or not self.processor:
            raise RuntimeError("El modelo no está cargado. Llama a cargar_modelo() primero.")

        img_path = Path(imagen_path).resolve()
        if not img_path.is_file():
            raise FileNotFoundError(f"No se encontró la imagen: {img_path}")

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": str(img_path),
                        "max_pixels": max_pixels or self.max_pixels,
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ]

        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        image_inputs, video_inputs = process_vision_info(messages)

        inputs = self.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        ).to(self.device)

        with torch.no_grad():
            generated_ids = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens or self.max_new_tokens,
                do_sample=False,
            )

        generated_ids_trimmed = [
            out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        return self.processor.batch_decode(
            generated_ids_trimmed,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False,
        )[0]

    def generar_metadatos(self, imagen_path: str, custom_prompt: str = None) -> dict:
        """
        Analiza una imagen y devuelve captions/keywords bilingues.
        Ejecución súper rápida (~8s) usando max_pixels y decodificación determinista.
        """
        # Preparar instrucciones extra si el usuario escribió algo en la interfaz
        instrucciones_extra = f"\n\nCRITICAL USER INSTRUCTION: {custom_prompt}\n" if custom_prompt and custom_prompt.strip() else ""

        # Prompt base inquebrantable (Stock Premium y formato estricto)
        prompt_base = (
            "You are a professional stock photography metadata editor. Analyze this image extremely carefully."
            f"{instrucciones_extra}\n"
            "First, provide an English caption: a detailed, premium, search-engine-optimized description of the image in 1 to 2 sentences. "
            "Focus on what is happening, the subject, colors, lighting, setting, and mood. Avoid cliché buzzwords like \"stunning\", \"beautiful\", \"hyperrealistic\". "
            "If the image depicts specific cultural aspects, traditional clothing, regional festivals, or unique landmarks, identify them specifically.\n\n"
            "Second, translate/adapt that metadata into natural Spanish for a local gallery UI.\n"
            "Third, provide 30 highly relevant English keywords and 30 highly relevant Spanish keywords. Keywords should cover the main subjects, actions, setting, colors, atmosphere, emotions, concepts, and any specific clothing/accessory details.\n\n"
            "Return only valid JSON with these exact keys:\n"
            "{\n"
            "  \"caption_en\": \"English SEO caption\",\n"
            "  \"caption_es\": \"Spanish SEO caption\",\n"
            "  \"keywords_en\": [\"keyword 1\", \"keyword 2\"],\n"
            "  \"keywords_es\": [\"palabra clave 1\", \"palabra clave 2\"]\n"
            "}"
        )

        output_text = self._run_image_prompt(imagen_path, prompt_base)

        return self._parsear_salida(output_text)

    def verificar_atributos(self, imagen_path: str, custom_prompt: str = None) -> dict:
        """
        Segunda pasada para atributos visuales delicados.

        La regla importante: si no se ve claro, guardar incertidumbre en vez de
        inventar azul/verde/etc.
        """
        instrucciones_extra = f"\n\nUSER CONTEXT: {custom_prompt}\n" if custom_prompt and custom_prompt.strip() else ""
        prompt = (
            "You are a careful image attribute verifier for stock metadata."
            f"{instrucciones_extra}\n"
            "Inspect only visible evidence. Do not infer hidden details. "
            "For eye color, hair color, clothing, accessories, and scene, use cautious values. "
            "If a detail is not clearly visible, set value to \"uncertain\" and confidence below 0.5.\n\n"
            "Return only valid JSON with this exact structure:\n"
            "{\n"
            "  \"eye_color\": {\"value\": \"green|blue|brown|hazel|gray|dark|light|uncertain\", \"confidence\": 0.0, \"note\": \"short reason\"},\n"
            "  \"hair_color\": {\"value\": \"visible hair color or uncertain\", \"confidence\": 0.0, \"note\": \"short reason\"},\n"
            "  \"clothing\": {\"value\": \"short visible clothing description\", \"confidence\": 0.0},\n"
            "  \"accessories\": [\"visible accessory\"],\n"
            "  \"scene\": {\"value\": \"short scene description\", \"confidence\": 0.0},\n"
            "  \"needs_review\": false,\n"
            "  \"warnings\": [\"short warning if any\"]\n"
            "}"
        )
        output_text = self._run_image_prompt(
            imagen_path,
            prompt,
            max_new_tokens=360,
            max_pixels=max(self.max_pixels, 768 * 28 * 28),
        )
        return self._parsear_atributos(output_text)

    def _parsear_atributos(self, text: str) -> dict:
        """Parse the visual attribute JSON returned by the verifier pass."""
        try:
            parsed = json.loads(text)
            return parsed if isinstance(parsed, dict) else {"raw_output": text, "needs_review": True}
        except json.JSONDecodeError:
            pass

        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            try:
                parsed = json.loads(text[start : end + 1])
                return parsed if isinstance(parsed, dict) else {"raw_output": text, "needs_review": True}
            except json.JSONDecodeError:
                pass

        return {
            "raw_output": text,
            "needs_review": True,
            "warnings": ["Attribute verifier did not return valid JSON."],
        }

    def _parsear_salida(self, text: str) -> dict:
        """
        Procesa el bloque de texto crudo de Qwen.
        Prefiere JSON bilingue, con fallback para el formato legacy.
        """
        return parse_bilingual_model_output(text)
