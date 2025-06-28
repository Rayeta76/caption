"""
Gestor robusto de imágenes para evitar el error 'pyimage1 doesn't exist'
SOLUCIÓN COMPLETA IMPLEMENTADA
"""

from PIL import Image, ImageTk
from pathlib import Path
from typing import Dict, Optional, Tuple, List
import logging
import threading
import tkinter as tk

logger = logging.getLogger(__name__)

class SafeImageManager:
    """Gestor centralizado y robusto de imágenes para Tkinter"""
    
    # Formatos soportados
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    
    def __init__(self):
        self._images: Dict[str, ImageTk.PhotoImage] = {}
        self._counter = 0
        self._lock = threading.Lock()  # Para thread safety
        self._closing = False
        
    def create_photo(self, image_path: str, size: Tuple[int, int] = (300, 300)) -> Tuple[Optional[ImageTk.PhotoImage], Optional[str]]:
        """
        Crea y almacena una PhotoImage de forma segura
        
        Aplica todas las soluciones:
        1. Verificación de existencia del archivo
        2. Mantener referencias fuertes
        3. Manejo de errores robusto
        4. Threading correcto
        5. Validación de formatos
        
        Args:
            image_path: Ruta de la imagen
            size: Tamaño máximo (ancho, alto)
            
        Returns:
            Tupla (PhotoImage, key) o (None, None) si hay error
        """
        if self._closing:
            return None, None
            
        try:
            # SOLUCIÓN 1: Verificar existencia del archivo
            if not self._verify_file_exists(image_path):
                logger.warning(f"Archivo no existe: {image_path}")
                return None, None
            
            # SOLUCIÓN 5: Validación de formatos
            if not self._validate_image_format(image_path):
                logger.warning(f"Formato no soportado: {image_path}")
                return None, None
            
            # SOLUCIÓN 4: Threading correcto - usar lock para thread safety
            with self._lock:
                # Cargar imagen con context manager para manejo seguro
                with Image.open(image_path) as img:
                    # Crear copia para evitar problemas de contexto
                    img_copy = img.copy()
                    img_copy.thumbnail(size, Image.Resampling.LANCZOS)
                    
                    # SOLUCIÓN 3: Verificar que la imagen se cargó correctamente
                    if img_copy.size == (0, 0):
                        raise ValueError("Imagen inválida o corrupta")
                    
                    # Convertir a PhotoImage
                    photo = ImageTk.PhotoImage(img_copy)
                    
                    # SOLUCIÓN 3: Verificar que PhotoImage se creó correctamente
                    if not photo or not hasattr(photo, 'tk'):
                        raise ValueError("Error creando PhotoImage")
                    
                    # SOLUCIÓN 2: Almacenar referencia permanente
                    self._counter += 1
                    key = f"safe_img_{self._counter}"
                    self._images[key] = photo
                    
                    logger.info(f"Imagen creada y almacenada: {key} ({image_path})")
                    return photo, key
                    
        except FileNotFoundError:
            logger.error(f"Archivo no encontrado: {image_path}")
        except PermissionError:
            logger.error(f"Sin permisos para leer: {image_path}")
        except Image.UnidentifiedImageError:
            logger.error(f"Formato de imagen no reconocido: {image_path}")
        except Exception as e:
            logger.error(f"Error creando imagen {image_path}: {e}")
            
        return None, None
    
    def _verify_file_exists(self, image_path: str) -> bool:
        """SOLUCIÓN 1: Verificar que el archivo existe y es accesible"""
        try:
            path = Path(image_path)
            return path.exists() and path.is_file() and path.stat().st_size > 0
        except Exception:
            return False
    
    def _validate_image_format(self, image_path: str) -> bool:
        """SOLUCIÓN 5: Validar formato de imagen"""
        try:
            path = Path(image_path)
            return path.suffix.lower() in self.SUPPORTED_FORMATS
        except Exception:
            return False
    
    def get_image(self, key: str) -> Optional[ImageTk.PhotoImage]:
        """Obtiene una imagen almacenada por su clave (thread-safe)"""
        if self._closing:
            return None
            
        with self._lock:
            return self._images.get(key)
    
    def remove_image(self, key: str) -> bool:
        """Elimina una imagen específica (thread-safe)"""
        try:
            with self._lock:
                if key in self._images:
                    photo_ref = self._images[key]
                    if photo_ref and hasattr(photo_ref, 'tk'):
                        del photo_ref
                    del self._images[key]
                    logger.info(f"Imagen eliminada: {key}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error eliminando imagen {key}: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Limpia todas las referencias de imágenes (thread-safe)"""
        try:
            with self._lock:
                count = len(self._images)
                for key, photo_ref in self._images.items():
                    try:
                        if photo_ref and hasattr(photo_ref, 'tk'):
                            del photo_ref
                    except:
                        pass
                
                self._images.clear()
                self._counter = 0
                logger.info(f"Limpiadas {count} referencias de imágenes")
                return True
                
        except Exception as e:
            logger.error(f"Error limpiando todas las imágenes: {e}")
            return False
    
    def get_count(self) -> int:
        """Retorna el número de imágenes almacenadas (thread-safe)"""
        with self._lock:
            return len(self._images)
    
    def get_supported_formats(self) -> List[str]:
        """Retorna lista de formatos soportados"""
        return list(self.SUPPORTED_FORMATS)
    
    def set_closing(self, closing: bool = True):
        """Marca el gestor como cerrándose"""
        self._closing = closing
        if closing:
            self.clear_all()
    
    def is_valid_image_file(self, file_path: str) -> bool:
        """Verifica si un archivo es una imagen válida"""
        return (self._verify_file_exists(file_path) and 
                self._validate_image_format(file_path))
    
    def get_stats(self) -> Dict[str, any]:
        """Obtiene estadísticas del gestor"""
        with self._lock:
            return {
                'total_images': len(self._images),
                'image_counter': self._counter,
                'closing': self._closing,
                'supported_formats': len(self.SUPPORTED_FORMATS)
            }

# Instancia global singleton para uso compartido
_safe_image_manager = None
_manager_lock = threading.Lock()

def get_safe_image_manager() -> SafeImageManager:
    """Obtiene la instancia singleton del SafeImageManager (thread-safe)"""
    global _safe_image_manager
    if _safe_image_manager is None:
        with _manager_lock:
            if _safe_image_manager is None:  # Double-check locking
                _safe_image_manager = SafeImageManager()
    return _safe_image_manager

def create_safe_photoimage(image_path: str, size: Tuple[int, int] = (300, 300)) -> Tuple[Optional[ImageTk.PhotoImage], Optional[str]]:
    """
    Función utilitaria para crear PhotoImage de forma segura
    
    IMPLEMENTA TODAS LAS SOLUCIONES:
    ✅ Verificación de existencia del archivo
    ✅ Referencias fuertes mantenidas automáticamente
    ✅ Manejo de errores robusto con try-catch específicos
    ✅ Threading correcto con locks
    ✅ Validación de formatos de imagen
    
    Args:
        image_path: Ruta al archivo de imagen
        size: Tamaño máximo (ancho, alto)
        
    Returns:
        Tupla (PhotoImage, key) o (None, None) si hay error
    """
    manager = get_safe_image_manager()
    return manager.create_photo(image_path, size)

def cleanup_photoimage(key: str) -> bool:
    """
    Función utilitaria para limpiar una PhotoImage específica
    
    Args:
        key: Clave de la imagen a limpiar
        
    Returns:
        True si se limpió exitosamente
    """
    manager = get_safe_image_manager()
    return manager.remove_image(key)

def cleanup_all_photoimages() -> bool:
    """
    Función utilitaria para limpiar todas las PhotoImages
    
    Returns:
        True si se limpiaron exitosamente
    """
    manager = get_safe_image_manager()
    return manager.clear_all()

def is_valid_image_file(file_path: str) -> bool:
    """
    Verifica si un archivo es una imagen válida
    
    Args:
        file_path: Ruta al archivo
        
    Returns:
        True si es una imagen válida
    """
    manager = get_safe_image_manager()
    return manager.is_valid_image_file(file_path)

def get_image_manager_stats() -> Dict[str, any]:
    """Obtiene estadísticas del gestor de imágenes"""
    manager = get_safe_image_manager()
    return manager.get_stats()

# Función para uso en el cierre de aplicaciones
def shutdown_image_manager():
    """Cierra el gestor de imágenes de forma segura"""
    global _safe_image_manager
    if _safe_image_manager:
        _safe_image_manager.set_closing(True)
        _safe_image_manager = None
