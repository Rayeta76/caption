"""
Gestor de Imágenes para Tkinter - StockPrep Pro v2.0
Manejo robusto de PhotoImage para evitar errores de referencia
"""

import tkinter as tk
from PIL import Image, ImageTk
from pathlib import Path
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class TkinterImageManager:
    """
    Gestor robusto de imágenes para Tkinter que evita errores de PhotoImage
    """
    
    def __init__(self):
        """Inicializa el gestor de imágenes"""
        self.image_references: Dict[str, ImageTk.PhotoImage] = {}
        self.image_counter = 0
        self.closing = False
    
    def load_image(self, image_path: str, max_size: tuple = (300, 300)) -> Optional[tuple]:
        """
        Carga una imagen de forma segura
        
        Args:
            image_path: Ruta al archivo de imagen
            max_size: Tamaño máximo (ancho, alto)
            
        Returns:
            Tupla (PhotoImage, key) o None si hay error
        """
        try:
            if not Path(image_path).exists():
                logger.warning(f"Archivo de imagen no existe: {image_path}")
                return None
            
            # Cargar y procesar imagen
            with Image.open(image_path) as image:
                # Crear copia para evitar problemas de contexto
                image_copy = image.copy()
                
                # Redimensionar manteniendo proporción
                image_copy.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Convertir a PhotoImage
                photo = ImageTk.PhotoImage(image_copy)
                
                # Almacenar referencia
                key = self._store_reference(photo)
                
                if key:
                    return photo, key
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Error cargando imagen {image_path}: {e}")
            return None
    
    def _store_reference(self, photo: ImageTk.PhotoImage) -> Optional[str]:
        """Almacena una referencia de imagen de forma segura"""
        try:
            self.image_counter += 1
            key = f"img_{self.image_counter}"
            self.image_references[key] = photo
            return key
        except Exception as e:
            logger.error(f"Error almacenando referencia: {e}")
            return None
    
    def get_image(self, key: str) -> Optional[ImageTk.PhotoImage]:
        """Obtiene una imagen por su clave"""
        try:
            return self.image_references.get(key)
        except:
            return None
    
    def remove_image(self, key: str) -> bool:
        """Elimina una imagen específica"""
        try:
            if key in self.image_references:
                photo_ref = self.image_references[key]
                if photo_ref and hasattr(photo_ref, 'tk'):
                    del photo_ref
                del self.image_references[key]
                return True
            return False
        except Exception as e:
            logger.error(f"Error eliminando imagen {key}: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Limpia todas las referencias de imágenes"""
        try:
            for key, photo_ref in self.image_references.items():
                try:
                    if photo_ref and hasattr(photo_ref, 'tk'):
                        del photo_ref
                except:
                    pass
            
            self.image_references.clear()
            self.image_counter = 0
            return True
            
        except Exception as e:
            logger.error(f"Error limpiando todas las imágenes: {e}")
            return False
    
    def set_closing(self, closing: bool = True):
        """Marca el gestor como cerrándose"""
        self.closing = closing
        if closing:
            self.clear_all()
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del gestor"""
        return {
            'total_images': len(self.image_references),
            'image_counter': self.image_counter,
            'closing': self.closing
        }
    
    def __del__(self):
        """Destructor que limpia las referencias"""
        try:
            self.clear_all()
        except:
            pass

# Instancia global del gestor para uso compartido
global_image_manager = TkinterImageManager()

def create_safe_photoimage(image_path: str, max_size: tuple = (300, 300)) -> Optional[tuple]:
    """
    Función utilitaria para crear PhotoImage de forma segura
    
    Args:
        image_path: Ruta al archivo de imagen
        max_size: Tamaño máximo (ancho, alto)
        
    Returns:
        Tupla (PhotoImage, key) o None si hay error
    """
    return global_image_manager.load_image(image_path, max_size)

def cleanup_photoimage(key: str) -> bool:
    """
    Función utilitaria para limpiar una PhotoImage específica
    
    Args:
        key: Clave de la imagen a limpiar
        
    Returns:
        True si se limpió exitosamente
    """
    return global_image_manager.remove_image(key)

def cleanup_all_photoimages() -> bool:
    """
    Función utilitaria para limpiar todas las PhotoImages
    
    Returns:
        True si se limpiaron exitosamente
    """
    return global_image_manager.clear_all() 