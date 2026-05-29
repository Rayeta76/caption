"""
Módulo de manejo de salidas para StockPrep Pro v2.0

Este módulo contiene las clases y funciones para manejar la salida
de resultados del procesamiento de imágenes, incluyendo:
- Guardado en base de datos SQLite
- Generación de archivos TXT
- Exportación en múltiples formatos
- Copia y renombrado de imágenes
"""

from .output_handler_v2 import OutputHandlerV2, create_output_handler

__all__ = ['OutputHandlerV2', 'create_output_handler']
__version__ = '2.0.0' 