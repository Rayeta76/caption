#!/usr/bin/env python3
"""
Script de corrección rápida para el error 'pyimage1 doesn't exist'
Ejecutar: python fix_pyimage_error.py
"""

import os
import re
from pathlib import Path

def fix_photoimage_references():
    """Corrige referencias de PhotoImage en archivos GUI"""
    
    gui_files = [
        'src/gui/modern_gui_stockprep.py',
        'src/gui/database_gui.py',
        'src/gui/inicio_gui.py',
        'src/gui/main_window.py'
    ]
    
    fixes_applied = 0
    
    for file_path in gui_files:
        if not Path(file_path).exists():
            print(f"⚠️  Archivo no encontrado: {file_path}")
            continue
            
        print(f"\n📝 Procesando: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Patrón 1: PhotoImage sin almacenar referencia
        pattern1 = r'(\s+)(photo\s*=\s*ImageTk\.PhotoImage\([^)]+\))\s*\n\s*(self\.[a-zA-Z_]+\.config\(image=photo[^)]*\))'
        replacement1 = r'\1\2\n\1self.\3.image = photo  # Mantener referencia\n\1\3'
        content = re.sub(pattern1, replacement1, content)
        
        # Patrón 2: PhotoImage en línea
        pattern2 = r'(self\.[a-zA-Z_]+\.config\(image=ImageTk\.PhotoImage\([^)]+\)[^)]*\))'
        def fix_inline(match):
            return f"# FIXME: PhotoImage inline - necesita refactorización\n        {match.group(1)}"
        content = re.sub(pattern2, fix_inline, content)
        
        if content != original_content:
            # Hacer backup
            backup_path = f"{file_path}.backup"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Escribir archivo corregido
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            fixes_applied += 1
            print(f"✅ Correcciones aplicadas. Backup en: {backup_path}")
        else:
            print("ℹ️  No se necesitaron correcciones")
    
    print(f"\n✨ Total de archivos corregidos: {fixes_applied}")
    
    # Crear ImageManager mejorado
    create_image_manager()

def create_image_manager():
    """Crea el archivo ImageManager mejorado"""
    
    manager_code = '''"""
Gestor robusto de imágenes para evitar el error 'pyimage1 doesn't exist'
"""

from PIL import Image, ImageTk
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class ImageManager:
    """Gestor centralizado de imágenes para Tkinter"""
    
    def __init__(self):
        self._images: Dict[str, ImageTk.PhotoImage] = {}
        self._counter = 0
        
    def create_photo(self, image_path: str, size: Tuple[int, int] = (300, 300)) -> Tuple[Optional[ImageTk.PhotoImage], Optional[str]]:
        """
        Crea y almacena una PhotoImage de forma segura
        
        Args:
            image_path: Ruta de la imagen
            size: Tamaño máximo (ancho, alto)
            
        Returns:
            Tupla (PhotoImage, key) o (None, None) si hay error
        """
        try:
            with Image.open(image_path) as img:
                # Crear copia para evitar problemas de contexto
                img_copy = img.copy()
                img_copy.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Convertir a PhotoImage
                photo = ImageTk.PhotoImage(img_copy)
                
                # Almacenar referencia permanente
                self._counter += 1
                key = f"img_{self._counter}"
                self._images[key] = photo
                
                logger.info(f"Imagen creada y almacenada: {key}")
                return photo, key
                
        except Exception as e:
            logger.error(f"Error creando imagen {image_path}: {e}")
            return None, None
    
    def get_image(self, key: str) -> Optional[ImageTk.PhotoImage]:
        """Obtiene una imagen almacenada por su clave"""
        return self._images.get(key)
    
    def remove_image(self, key: str) -> bool:
        """Elimina una imagen específica"""
        if key in self._images:
            try:
                del self._images[key]
                logger.info(f"Imagen eliminada: {key}")
                return True
            except Exception as e:
                logger.error(f"Error eliminando imagen {key}: {e}")
        return False
    
    def clear_all(self):
        """Limpia todas las referencias de imágenes"""
        count = len(self._images)
        self._images.clear()
        self._counter = 0
        logger.info(f"Limpiadas {count} referencias de imágenes")
    
    def get_count(self) -> int:
        """Retorna el número de imágenes almacenadas"""
        return len(self._images)

# Instancia global singleton
_image_manager = None

def get_image_manager() -> ImageManager:
    """Obtiene la instancia singleton del ImageManager"""
    global _image_manager
    if _image_manager is None:
        _image_manager = ImageManager()
    return _image_manager
'''
    
    manager_path = Path('src/utils/safe_image_manager.py')
    manager_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(manager_path, 'w', encoding='utf-8') as f:
        f.write(manager_code)
    
    print(f"\n✅ ImageManager creado en: {manager_path}")

if __name__ == "__main__":
    print("🔧 Script de Corrección Rápida para Error 'pyimage1'")
    print("=" * 50)
    
    fix_photoimage_references()
    
    print("\n📌 Próximos pasos:")
    print("1. Revisar los archivos marcados con FIXME")
    print("2. Integrar ImageManager en los componentes GUI")
    print("3. Probar la aplicación completa")
    print("\n✨ Corrección completada!")