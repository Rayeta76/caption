"""
Procesador de imágenes con Florence‑2.

— Revisión junio 2025 —
• Asegura coherencia de **dtype** y **device** con el modelo (float32)
• Mantiene la misma API pública
• Integración con YAKE para extracción avanzada de keywords
• Soporte para niveles de detalle configurables
"""
from pathlib import Path
from typing import Dict, List

import torch
from PIL import Image
from utils.keyword_extractor import KeywordExtractor


class ImageProcessor:
    """Procesa una imagen con Florence‑2 a través de un `Florence2Manager`."""

    def __init__(self, model_manager, keyword_extractor=None, idioma: str = "es"):
        """`model_manager` debe exponer `.model`, `.processor` y `.model.device`."""
        self.manager = model_manager
        self.keyword_extractor = keyword_extractor or KeywordExtractor(language=idioma)

    # ------------------------------------------------------------------
    #  API pública
    # ------------------------------------------------------------------
    def process_image(self, image_path: str, detail_level: str = "largo") -> Dict:
        """
        Procesa imagen y devuelve caption, keywords y objetos.
        
        Args:
            image_path: Ruta de la imagen
            detail_level: Nivel de detalle ("minimo", "medio", "largo")
        """
        if self.manager.model is None:
            return {"error": "Modelo no cargado", "archivo": Path(image_path).name}

        try:
            image = Image.open(image_path).convert("RGB")
            
            # Mapear nivel de detalle a prompt de PromptGen v2.0
            # PromptGen v2.0 tiene mejoras específicas en estos prompts
            prompt_map = {
                "minimo": "<CAPTION>",                    # Caption simple de una línea
                "medio": "<DETAILED_CAPTION>",            # Caption estructurado con posiciones
                "largo": "<MORE_DETAILED_CAPTION>"        # Descripción muy detallada (mejorada en v2.0)
            }
            
            caption_prompt = prompt_map.get(detail_level, "<MORE_DETAILED_CAPTION>")
            
            # Generar caption con el nivel de detalle seleccionado
            caption = self._generar_descripcion(image, caption_prompt, detail_level)
            
            # Generar objetos detectados (usar parámetros específicos para OD)
            objects_raw = self._generar_descripcion(image, "<OD>", "objects")
            objects = self._format_objects(objects_raw)
            
            # Extraer keywords del caption
            keywords = self.keyword_extractor.extract_keywords(caption)
            
            return {
                "caption": caption,
                "keywords": keywords,
                "objects": objects,
                "file_path": str(image_path),
                "file_name": Path(image_path).name,
                "image_size": image.size,
                "detail_level": detail_level
            }

        except Exception as exc:
            return {"error": f"Error al procesar imagen: {exc}", "archivo": Path(image_path).name}
    
    def procesar_imagen(self, ruta_imagen: str, detail_level: str = "largo") -> Dict:
        """Método de compatibilidad con la API anterior."""
        return self.process_image(ruta_imagen, detail_level)

    # ------------------------------------------------------------------
    #  Descripción / objetos
    # ------------------------------------------------------------------
    def _generar_descripcion(self, image: Image.Image, task_tag: str, detail_level: str = "largo"):
        """Genera texto u objeto detectado conforme a la tag solicitada."""
        # 1. Preparar tensores (always float32 to match model)
        inputs = self.manager.processor(text=task_tag, images=image, return_tensors="pt")
        inputs = inputs.to(self.manager.model.device, dtype=self.manager.model.dtype)

        # 2. Parámetros optimizados según el nivel de detalle
        generation_params = self._get_generation_params(detail_level)

        # 3. Generar salida (sin grad) con parámetros optimizados
        with torch.no_grad():
            gen_ids = self.manager.model.generate(
                input_ids=inputs["input_ids"],
                pixel_values=inputs["pixel_values"],
                **generation_params
            )

        # 4. Decodificar y post‑procesar
        gen_text = self.manager.processor.batch_decode(gen_ids, skip_special_tokens=False)[0]
        parsed = self.manager.processor.post_process_generation(
            gen_text, task=task_tag, image_size=(image.width, image.height)
        )
        # Florence‑2 devuelve dict en OC / OD tareas
        if isinstance(parsed, dict):
            return parsed.get(task_tag, str(parsed))
        return str(parsed)
    
    def _get_generation_params(self, detail_level: str) -> Dict:
        """
        Obtiene parámetros de generación optimizados para PromptGen v2.0.
        Este modelo está específicamente entrenado para generar descripciones más largas.
        """
        if detail_level == "minimo":
            # <CAPTION> - Una línea simple pero descriptiva
            return {
                "max_new_tokens": 128,   # Optimizado para captions concisos
                "do_sample": False,      # Determinístico para consistencia
                "num_beams": 3,          # Suficiente para calidad
                "repetition_penalty": 1.1
            }
        elif detail_level == "medio":
            # <DETAILED_CAPTION> - Caption estructurado con posiciones (OPTIMIZADO para más detalle)
            return {
                "max_new_tokens": 1024,  # Aumentado para más detalle
                "do_sample": True,       # Permitir variabilidad
                "num_beams": 4,          # Más beams para mejor calidad
                "temperature": 0.8,      # Más creativo
                "top_p": 0.92,          # Nucleus sampling amplio
                "repetition_penalty": 1.04,
                "length_penalty": 1.1,   # Ligera preferencia por descripciones más largas
                "min_length": 25        # Mínimo para asegurar detalle
            }
        elif detail_level == "objects":
            # <OD> - Detección de objetos
            return {
                "max_new_tokens": 1024,
                "do_sample": False,      # Determinístico para detección
                "num_beams": 3
            }
        else:  # largo
            # <MORE_DETAILED_CAPTION> - Descripción muy detallada (OPTIMIZADA para descripciones largas)
            return {
                "max_new_tokens": 2048,     # Aumentado para descripciones muy largas
                "do_sample": True,          # Activar para creatividad y variabilidad
                "num_beams": 5,             # Más beams para mejor calidad
                "temperature": 0.9,         # Más creatividad para descripciones ricas
                "top_p": 0.95,             # Nucleus sampling amplio
                "top_k": 50,               # Top-k sampling para diversidad
                "repetition_penalty": 1.05, # Evitar repeticiones
                "length_penalty": 1.3,      # Penalizar descripciones cortas fuertemente
                "no_repeat_ngram_size": 3,  # Evitar repetir n-gramas
                "early_stopping": False,    # NO parar temprano
                "min_length": 50           # Mínimo de tokens para forzar descripciones largas
            }

    # ------------------------------------------------------------------
    #  Formateo de objetos
    # ------------------------------------------------------------------
    def _format_objects(self, objects_raw) -> List[Dict]:
        """Formatea los objetos detectados en una lista estructurada."""
        if not objects_raw:
            return []
        
        try:
            # Si es un dict con información de detección (formato estándar de Florence-2)
            if isinstance(objects_raw, dict):
                formatted_objects = []
                
                # Verificar si tiene las claves esperadas
                if 'labels' in objects_raw and 'bboxes' in objects_raw:
                    labels = objects_raw.get('labels', [])
                    boxes = objects_raw.get('bboxes', [])
                    
                    for i, label in enumerate(labels):
                        bbox = boxes[i] if i < len(boxes) else [0, 0, 0, 0]
                        
                        formatted_objects.append({
                            "name": str(label),
                            "bbox": bbox,
                            "confidence": 1.0  # Florence-2 OD no siempre devuelve scores
                        })
                
                # Formato alternativo con 'boxes' en lugar de 'bboxes'
                elif 'labels' in objects_raw and 'boxes' in objects_raw:
                    labels = objects_raw.get('labels', [])
                    boxes = objects_raw.get('boxes', [])
                    scores = objects_raw.get('scores', [1.0] * len(labels))
                    
                    for i, label in enumerate(labels):
                        bbox = boxes[i] if i < len(boxes) else [0, 0, 0, 0]
                        score = scores[i] if i < len(scores) else 1.0
                        
                        formatted_objects.append({
                            "name": str(label),
                            "bbox": bbox,
                            "confidence": float(score)
                        })
                
                # Si el dict contiene directamente la tarea OD
                elif '<OD>' in objects_raw:
                    od_result = objects_raw['<OD>']
                    return self._format_objects(od_result)  # Recursión
                
                else:
                    # Formato desconocido, intentar extraer información
                    formatted_objects = [{"name": str(objects_raw), "bbox": [0, 0, 0, 0], "confidence": 1.0}]
                
                return formatted_objects
            
            # Si es un string, intentar parsearlo
            elif isinstance(objects_raw, str):
                # Florence-2 a veces devuelve texto plano con objetos
                if objects_raw.strip():
                    # Dividir por comas o líneas nuevas
                    objects_list = [obj.strip() for obj in objects_raw.replace('\n', ',').split(',') if obj.strip()]
                    return [{"name": obj, "bbox": [0, 0, 0, 0], "confidence": 1.0} for obj in objects_list]
                else:
                    return []
            
            # Si es una lista, procesarla
            elif isinstance(objects_raw, list):
                return [{"name": str(obj), "bbox": [0, 0, 0, 0], "confidence": 1.0} for obj in objects_raw]
            
            else:
                return [{"name": str(objects_raw), "bbox": [0, 0, 0, 0], "confidence": 1.0}]
                
        except Exception as e:
            print(f"❌ Error formateando objetos: {e}")
            return [{"name": f"Error: {str(objects_raw)}", "bbox": [0, 0, 0, 0], "confidence": 1.0}]
    
    # ------------------------------------------------------------------
    #  Keywords avanzadas con YAKE
    # ------------------------------------------------------------------
    def extract_keywords(self, text: str) -> List[str]:
        """Extrae keywords usando YAKE (Yet Another Keyword Extractor)"""
        return self.keyword_extractor.extract_keywords(text)
    
    def change_language(self, new_language: str):
        """Cambia el idioma para la extracción de keywords"""
        self.keyword_extractor = KeywordExtractor(language=new_language)
