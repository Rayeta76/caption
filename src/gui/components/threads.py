"""
Hilos de procesamiento para la interfaz gráfica
"""
import logging
from typing import Dict
from PySide6.QtCore import QThread, Signal

logger = logging.getLogger(__name__)

class ModelLoadingThread(QThread):
    """Hilo para cargar el modelo sin bloquear la UI"""
    finished = Signal(bool)
    error = Signal(str)
    progress = Signal(str)
    
    def __init__(self, model_manager):
        super().__init__()
        self.model_manager = model_manager
    
    def run(self):
        """Ejecuta la carga del modelo"""
        try:
            def callback(mensaje):
                self.progress.emit(mensaje)
            
            self.progress.emit("🚀 Iniciando carga del modelo Florence-2...")
            success = self.model_manager.cargar_modelo(callback)
            self.finished.emit(success)
            
        except Exception as e:
            logger.error(f"Error cargando modelo: {e}")
            self.error.emit(str(e))

class ProcessingThread(QThread):
    """Hilo para procesar imágenes sin bloquear la UI"""
    finished = Signal(dict)
    error = Signal(str)
    progress = Signal(int)
    
    def __init__(self, image_path: str, processor, detail_level: str = "largo"):
        super().__init__()
        self.image_path = image_path
        self.processor = processor
        self.detail_level = detail_level
    
    def run(self):
        """Ejecuta el procesamiento de imagen"""
        try:
            self.progress.emit(10)
            
            # Procesar imagen con nivel de detalle específico
            results = self.processor.process_image(self.image_path, self.detail_level)
            
            self.progress.emit(100)
            self.finished.emit(results)
            
        except Exception as e:
            logger.error(f"Error procesando imagen: {e}")
            self.error.emit(str(e)) 