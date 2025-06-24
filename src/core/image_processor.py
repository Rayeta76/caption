"""
Procesador de imágenes con Florence-2
Este archivo procesa las imágenes y genera las descripciones
"""
from PIL import Image
import torch
from pathlib import Path
from typing import Dict, List

class ImageProcessor:
    """Clase que procesa imágenes con Florence-2"""
    
    def __init__(self, model_manager):
        """
        Inicializa el procesador
        model_manager: instancia de Florence2Manager
        """
        self.model_manager = model_manager
        
    def procesar_imagen(self, ruta_imagen: str) -> Dict:
        """
        Procesa una imagen y genera descripción
        ruta_imagen: ruta completa a la imagen
        Retorna: diccionario con los resultados
        """
        try:
            # Verificar que el modelo esté cargado
            if not self.model_manager.model:
                return {"error": "Modelo no cargado"}
            
            # Cargar la imagen
            imagen = Image.open(ruta_imagen).convert('RGB')
            
            # Preparar las tareas
            resultados = {}
            
            # Generar descripción detallada
            descripcion = self._generar_descripcion(imagen, "<MORE_DETAILED_CAPTION>")
            resultados['descripcion'] = descripcion
            
            # Detectar objetos
            objetos = self._generar_descripcion(imagen, "<OD>")
            resultados['objetos'] = objetos
            
            # Añadir metadatos
            resultados['archivo'] = Path(ruta_imagen).name
            resultados['ruta_completa'] = str(ruta_imagen)
            resultados['tamaño'] = imagen.size
            
            return resultados
            
        except Exception as e:
            return {
                "error": f"Error al procesar imagen: {str(e)}",
                "archivo": Path(ruta_imagen).name
            }
    
    def _generar_descripcion(self, imagen: Image.Image, tarea: str) -> str:
        """
        Genera una descripción para la tarea especificada
        imagen: imagen PIL
        tarea: tipo de tarea (<MORE_DETAILED_CAPTION>, <OD>, etc.)
        """
        # Preparar entrada
        inputs = self.model_manager.processor(
            text=tarea,
            images=imagen,
            return_tensors="pt"
        ).to(self.model_manager.device)
        
        # Generar respuesta
        with torch.no_grad():
            generated_ids = self.model_manager.model.generate(
                input_ids=inputs["input_ids"],
                pixel_values=inputs["pixel_values"],
                max_new_tokens=1024,
                do_sample=False,
                num_beams=3
            )
        
        # Decodificar respuesta
        generated_text = self.model_manager.processor.batch_decode(
            generated_ids, 
            skip_special_tokens=False
        )[0]
        
        # Procesar respuesta
        parsed_answer = self.model_manager.processor.post_process_generation(
            generated_text,
            task=tarea,
            image_size=(imagen.width, imagen.height)
        )
        
        # Retornar según el tipo de tarea
        if isinstance(parsed_answer, dict):
            return parsed_answer.get(tarea, str(parsed_answer))
        return str(parsed_answer)
    
    def extraer_keywords(self, resultado: Dict) -> List[str]:
        """
        Extrae palabras clave del resultado
        resultado: diccionario con los resultados del procesamiento
        """
        keywords = []
        
        # Extraer de la descripción
        descripcion = resultado.get('descripcion', '')
        if descripcion:
            # Palabras comunes a ignorar
            palabras_ignorar = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
                'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were',
                'el', 'la', 'los', 'las', 'un', 'una', 'y', 'o', 'pero'
            }
            
            # Extraer palabras significativas
            palabras = descripcion.lower().split()
            for palabra in palabras:
                palabra_limpia = palabra.strip('.,!?;:')
                if len(palabra_limpia) > 3 and palabra_limpia not in palabras_ignorar:
                    keywords.append(palabra_limpia)
        
        # Extraer de objetos detectados
        objetos = resultado.get('objetos', {})
        if isinstance(objetos, dict) and 'labels' in objetos:
            keywords.extend(objetos['labels'])
        
        # Eliminar duplicados y retornar
        return list(set(keywords))[:20]  # Máximo 20 keywords