import gc
import json
import os
import re
import time
from pathlib import Path

import torch
from PIL import Image
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info

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
        
        # Detección de dispositivo optimizada
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.bfloat16 if self.device == "cuda" else torch.float32
        
        self.initialized = True

    def cargar_modelo(self, callback=None):
        """Carga el modelo en memoria VRAM usando bfloat16 y device_map='auto'."""
        if self.model is not None and self.processor is not None:
            if callback: callback("✅ Qwen2-VL ya está activo en memoria.")
            return True
            
        try:
            if callback: callback("📝 Cargando procesador de Qwen2-VL...")
            self.processor = AutoProcessor.from_pretrained(self.model_id)
            
            if callback: callback(f"🔄 Cargando pesos base de {self.model_id} en {self.dtype}...")
            # Auto-mapping aprovecha al máximo la arquitectura accelerate en la GPU
            self.model = Qwen2VLForConditionalGeneration.from_pretrained(
                self.model_id,
                torch_dtype=self.dtype,
                device_map="auto"
            )
            
            if callback: callback("✅ Modelo Qwen2-VL cargado y listo en GPU.")
            return True
        except Exception as e:
            if callback: callback(f"❌ Error crítico al cargar Qwen2-VL: {e}")
            return False

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

    def generar_metadatos(self, imagen_path: str, custom_prompt: str = None) -> dict:
        """
        Analiza una imagen y devuelve captions/keywords bilingues.
        Ejecución súper rápida (~8s) usando max_pixels y decodificación determinista.
        """
        if not self.model or not self.processor:
            raise RuntimeError("El modelo no está cargado. Llama a cargar_modelo() primero.")

        # Verificar que la imagen es accesible
        img_path = Path(imagen_path).resolve()
        if not img_path.is_file():
            raise FileNotFoundError(f"No se encontró la imagen: {img_path}")

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

        # Empaquetado visual para el procesador multimodal
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image", 
                        "image": str(img_path),
                        # Limitamos los píxeles (720p/1080p aprox) para acelerar inferencia
                        # manteniendo el 100% de la semántica visual para tagging
                        "max_pixels": 512 * 28 * 28 
                    },
                    {"type": "text", "text": prompt_base}
                ]
            }
        ]

        # Ensamblado del prompt
        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        image_inputs, video_inputs = process_vision_info(messages)
        
        # Mapear inputs a GPU
        inputs = self.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt"
        ).to(self.device)

        # Inferencia determinista con margen suficiente para JSON bilingue.
        with torch.no_grad():
            generated_ids = self.model.generate(
                **inputs,
                max_new_tokens=520,
                do_sample=False
            )

        # Decodificación y recorte de la instrucción base
        generated_ids_trimmed = [
            out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        output_text = self.processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )[0]

        return self._parsear_salida(output_text)

    def _parsear_salida(self, text: str) -> dict:
        """
        Procesa el bloque de texto crudo de Qwen.
        Prefiere JSON bilingue, con fallback para el formato legacy.
        """
        json_data = self._extract_json(text)
        if json_data:
            caption_en = str(json_data.get("caption_en") or json_data.get("caption") or "").strip()
            caption_es = str(json_data.get("caption_es") or "").strip()
            keywords_en = self._clean_keywords(json_data.get("keywords_en") or json_data.get("keywords") or [])
            keywords_es = self._clean_keywords(json_data.get("keywords_es") or [])
            return {
                "caption": caption_en,
                "descripcion": caption_en,
                "caption_en": caption_en,
                "caption_es": caption_es,
                "keywords": keywords_en,
                "keywords_en": keywords_en,
                "keywords_es": keywords_es,
                "raw_output": text,
            }

        caption_en = ""
        caption_es = ""
        keywords_en = []
        keywords_es = []
        
        lines = text.split('\n')
        for line in lines:
            line_clean = line.strip()
            upper = line_clean.upper()
            if upper.startswith(("CAPTION_EN:", "ENGLISH CAPTION:", "CAPTION:")):
                caption_en = line_clean.split(":", 1)[1].strip()
            elif upper.startswith(("CAPTION_ES:", "SPANISH CAPTION:")):
                caption_es = line_clean.split(":", 1)[1].strip()
            elif upper.startswith(("KEYWORDS_EN:", "ENGLISH KEYWORDS:", "KEYWORDS:")):
                keywords_en = self._clean_keywords(line_clean.split(":", 1)[1])
            elif upper.startswith(("KEYWORDS_ES:", "SPANISH KEYWORDS:")):
                keywords_es = self._clean_keywords(line_clean.split(":", 1)[1])
                
        # Fallback de emergencia si el modelo ignoró las etiquetas
        if not caption_en and not keywords_en:
            caption_en = text.strip()
            
        return {
            "caption": caption_en,
            "descripcion": caption_en,
            "caption_en": caption_en,
            "caption_es": caption_es,
            "keywords": keywords_en,
            "keywords_en": keywords_en,
            "keywords_es": keywords_es,
            "raw_output": text,
        }

    def _extract_json(self, text: str) -> dict:
        """Extract the first JSON object found in model output."""
        try:
            parsed = json.loads(text)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            pass

        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            return {}
        try:
            parsed = json.loads(match.group(0))
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}

    def _clean_keywords(self, value) -> list[str]:
        if isinstance(value, str):
            value = [item.strip() for item in re.split(r"[,;\n]", value) if item.strip()]
        elif not isinstance(value, list):
            value = []

        keywords = [str(item).strip().lower() for item in value if str(item).strip()]
        return list(dict.fromkeys(keywords))
