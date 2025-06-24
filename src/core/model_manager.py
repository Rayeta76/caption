"""
Gestor del modelo Florence-2 - VERSIÓN CORREGIDA
Este archivo incluye los parches necesarios para funcionar con timm 1.0.15
"""
import os
import torch
from transformers import AutoModelForCausalLM, AutoProcessor
from unittest.mock import patch
from transformers.dynamic_module_utils import get_imports
import gc
import warnings

class Florence2Manager:
    """Clase que gestiona el modelo Florence-2"""
    
    def __init__(self, model_id: str | None = None):
        """Inicializa el gestor del modelo

        Parameters
        ----------
        model_id: str | None, optional
            Ruta o identificador del modelo Florence-2. Si no se indica se
            utilizará el valor de la variable de entorno ``FLORENCE2_MODEL_ID``
            o la ruta local por defecto.
        """
        self.model = None
        self.processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # Ruta por defecto si no se especifica ninguna
        env_model = os.getenv("FLORENCE2_MODEL_ID")
        self.model_id = model_id or env_model or r"E:\Proyectos\Caption\models\Florence2-large"
        
    def fixed_get_imports(self, filename):
        """Arregla el problema de flash_attn en Windows"""
        if not str(filename).endswith("modeling_florence2.py"):
            return get_imports(filename)
        imports = get_imports(filename)
        if "flash_attn" in imports:
            imports.remove("flash_attn")
        return imports
    
    def _patch_davit_model(self):
        """Parche para hacer DaViT compatible con timm 1.0.15"""
        def dummy_initialize_weights(self, module=None):
            """Función vacía para reemplazar _initialize_weights"""
            pass
        
        # Intentar parchear la clase DaViT si existe
        try:
            import sys
            # Buscar el módulo DaViT en los módulos cargados
            for name, module in sys.modules.items():
                if 'davit' in name.lower() and hasattr(module, 'DaViT'):
                    davit_class = getattr(module, 'DaViT')
                    if not hasattr(davit_class, '_initialize_weights'):
                        davit_class._initialize_weights = dummy_initialize_weights
                        print("✅ Parche aplicado a DaViT para compatibilidad con timm 1.0.15")
        except Exception as e:
            print(f"⚠️ No se pudo aplicar parche preventivo a DaViT: {e}")
    
    def cargar_modelo(self, callback=None):
        """
        Carga el modelo Florence-2 con todos los parches necesarios
        callback: función para actualizar el progreso
        """
        try:
            if callback:
                callback("Iniciando carga del modelo...")
            
            # Suprimir warnings molestos
            warnings.filterwarnings('ignore', category=FutureWarning)
            warnings.filterwarnings('ignore', category=UserWarning)
            
            # Aplicar el parche para Windows (flash_attn)
            with patch("transformers.dynamic_module_utils.get_imports", self.fixed_get_imports):
                if callback:
                    callback("Descargando modelo (puede tardar varios minutos)...")
                
                # Cargar el procesador primero
                self.processor = AutoProcessor.from_pretrained(
                    self.model_id,
                    trust_remote_code=True
                )
                
                if callback:
                    callback("Aplicando parches de compatibilidad...")
                
                # Aplicar parche para DaViT ANTES de cargar el modelo
                self._patch_davit_model()
                
                # Crear un contexto especial para la carga del modelo
                original_init = None
                try:
                    # Intentar parchear dinámicamente durante la carga
                    def patched_getattr(obj, name):
                        if name == '_initialize_weights':
                            return lambda *args, **kwargs: None
                        return object.__getattribute__(obj, name)
                    
                    # Temporalmente reemplazar __getattribute__ para DaViT
                    import builtins
                    original_getattr = builtins.getattr
                    
                    def custom_getattr(obj, name):
                        if hasattr(obj, '__class__') and obj.__class__.__name__ == 'DaViT' and name == '_initialize_weights':
                            return lambda *args, **kwargs: None
                        return original_getattr(obj, name)
                    
                    builtins.getattr = custom_getattr
                    
                    if callback:
                        callback("Cargando modelo en memoria...")
                    
                    # Cargar el modelo con configuración especial
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_id,
                        trust_remote_code=True,
                        torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                        attn_implementation="sdpa",
                        # Desactivar la inicialización de pesos si es posible
                        _init_weights=False,
                        ignore_mismatched_sizes=True
                    )
                    
                finally:
                    # Restaurar getattr original
                    if 'original_getattr' in locals():
                        builtins.getattr = original_getattr
                
                # Mover modelo a dispositivo
                self.model = self.model.to(self.device)
                
                # Poner el modelo en modo evaluación
                self.model.eval()
                
                # Aplicar parche post-carga si es necesario
                if hasattr(self.model, 'vision_tower') and hasattr(self.model.vision_tower, '__class__'):
                    vision_model = self.model.vision_tower
                    if vision_model.__class__.__name__ == 'DaViT' and not hasattr(vision_model, '_initialize_weights'):
                        vision_model._initialize_weights = lambda *args, **kwargs: None
                        if callback:
                            callback("✅ Parche post-carga aplicado correctamente")
                
                if callback:
                    callback("✅ Modelo cargado correctamente")
                
                return True
                
        except AttributeError as e:
            if "'DaViT' object has no attribute '_initialize_weights'" in str(e):
                if callback:
                    callback("⚠️ Aplicando solución alternativa para timm 1.0.15...")
                
                # Intento de recuperación
                try:
                    # Buscar el objeto DaViT en el modelo cargado
                    if hasattr(self.model, 'vision_tower'):
                        vision_tower = self.model.vision_tower
                        if not hasattr(vision_tower, '_initialize_weights'):
                            # Añadir el método que falta
                            vision_tower._initialize_weights = lambda *args, **kwargs: None
                            if callback:
                                callback("✅ Parche de recuperación aplicado")
                            return True
                except Exception as recovery_error:
                    if callback:
                        callback(f"❌ Error en recuperación: {recovery_error}")
                    
            if callback:
                callback(f"❌ Error al cargar modelo: {str(e)}")
            return False
            
        except Exception as e:
            if callback:
                callback(f"❌ Error al cargar modelo: {str(e)}")
            
            # Intento final con versión alternativa
            if "timm" in str(e).lower() or "davit" in str(e).lower():
                if callback:
                    callback("🔄 Intentando carga alternativa...")
                    callback("💡 NOTA: Si el error persiste, considera usar una versión local del modelo")
                    callback("   Descarga los archivos de: https://huggingface.co/microsoft/Florence-2-large")
                    callback("   Y modifica model_id para apuntar a la carpeta local")
            
            return False
    
    def descargar_modelo(self):
        """Libera el modelo de la memoria"""
        if self.model is not None:
            del self.model
            self.model = None
        if self.processor is not None:
            del self.processor
            self.processor = None
        
        # Limpiar memoria GPU
        if self.device == "cuda":
            torch.cuda.empty_cache()
        gc.collect()
    
    def obtener_uso_memoria(self):
        """Obtiene información sobre el uso de memoria"""
        if self.device == "cuda":
            allocated = torch.cuda.memory_allocated() / 1024**3
            reserved = torch.cuda.memory_reserved() / 1024**3
            return f"GPU: {allocated:.1f}GB usado de {reserved:.1f}GB reservado"
        return "Modo CPU"