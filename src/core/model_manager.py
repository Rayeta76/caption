"""
Gestor del modelo Florence‑2 (versión parcheada para RTX 4090 y dtype coherente)
"""

from pathlib import Path
from unittest.mock import patch

import gc
import os
import yaml

import torch
from transformers import AutoModelForCausalLM, AutoProcessor
from transformers.dynamic_module_utils import get_imports

# ============================================================================
# OPTIMIZACIONES GPU PARA RTX 4090 - MÁXIMO RENDIMIENTO
# ============================================================================

# 1. Activar optimizaciones Tensor Cores (TF32) para Ampere+
# Proporciona ~1.6x aceleración en operaciones matriciales con mínima pérdida de precisión
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

# 2. Optimizar asignación de memoria CUDA
# Reduce fragmentación y mejora eficiencia de memoria
torch.backends.cuda.caching_allocator_settings = "max_split_size_mb:512"

# 3. Habilitar fusión de operaciones en cuDNN (cuando esté disponible)
# Combina operaciones para reducir overhead
torch.backends.cudnn.benchmark = True

# 4. Configurar estrategia de memoria para modelos grandes
# Permite usar más memoria virtual si es necesario
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "max_split_size_mb:512,roundup_power2_divisions:16")


class Florence2Manager:
    """Carga y gestiona un checkpoint local de Florence‑2."""

    def __init__(self):
        self.model = None
        self.processor = None
        
        # Detección mejorada de dispositivo
        self.device = self._detect_best_device()
        self.gpu_info = self._get_gpu_info()
        
        env_path = os.getenv("FLORENCE2_MODEL_PATH")
        model_path: Path | None = None

        if env_path:
            model_path = Path(env_path)
        else:
            cfg_file = Path(__file__).resolve().parents[2] / "config/settings.yaml"
            if cfg_file.is_file():
                try:
                    with open(cfg_file, "r", encoding="utf-8") as f:
                        config = yaml.safe_load(f) or {}
                    ruta = config.get("modelo", {}).get("ruta_local")
                    if ruta:
                        model_path = Path(ruta)
                except Exception:
                    model_path = None

        if model_path is None:
            root_dir = Path(__file__).resolve().parents[2]
            model_path = root_dir / "models/Florence-2-large-ft-safetensors"

        self.model_id = str(model_path.expanduser().resolve())

    # ---------------------------------------------------------------------
    #  Utilidad para evitar que Flash‑Attn se cargue si no está disponible
    # ---------------------------------------------------------------------
    def _fixed_get_imports(self, filename):
        imports = get_imports(filename)
        if str(filename).endswith("modeling_florence2.py") and "flash_attn" in imports:
            imports = [imp for imp in imports if imp != "flash_attn"]
        return imports


    # ---------------------------------------------------------------------
    #  Carga de modelo y processor
    # ---------------------------------------------------------------------
    def cargar_modelo(self, callback=None):
        """Carga Florence‑2 en **float32** para evitar errores de tipo mezclado."""
        try:
            if callback:
                callback("🧠 Cargando modelo desde carpeta local (dtype float32)…")
                
                # Mostrar información de dispositivo
                if self.gpu_info["available"]:
                    gpu_name = self.gpu_info["name"]
                    free_memory = self.gpu_info["free_gb"]
                    callback(f"🎮 GPU detectada: {gpu_name}")
                    callback(f"💾 Memoria GPU libre: {free_memory} GB")
                    callback(f"🚀 Ejecutándose en: {self.device}")
                else:
                    callback("⚠️ GPU no disponible - Ejecutándose en CPU")
                    callback("   (El procesamiento será más lento)")

            with patch(
                "transformers.dynamic_module_utils.get_imports", self._fixed_get_imports
            ):
                # Processor (tokenizer + image processor)
                if callback:
                    callback("📝 Cargando tokenizer y processor...")
                    
                self.processor = AutoProcessor.from_pretrained(
                    self.model_id, trust_remote_code=True
                )

                # Modelo – TODO: usa siempre float32 para coherencia con las entradas
                if callback:
                    callback("🔄 Cargando modelo Florence-2 (esto puede tomar varios minutos)...")
                    
                # Cargar modelo con configuración robusta para diferentes variantes de Florence-2
                try:
                    self.model = (
                        AutoModelForCausalLM.from_pretrained(
                            self.model_id,
                            trust_remote_code=True,
                            use_safetensors=True,
                            torch_dtype=torch.float32,  #  <-- forzamos fp32
                            device_map="auto",
                            attn_implementation="eager",  # Usar implementación estándar de atención
                        )
                        .to(self.device)
                        .eval()
                    )
                except Exception as e:
                    if callback:
                        callback(f"⚠️ Reintentando carga con configuración alternativa...")
                    
                    # Fallback: cargar sin device_map para mayor compatibilidad
                    self.model = (
                        AutoModelForCausalLM.from_pretrained(
                            self.model_id,
                            trust_remote_code=True,
                            use_safetensors=True,
                            torch_dtype=torch.float32,
                            low_cpu_mem_usage=True,
                        )
                        .to(self.device)
                        .eval()
                    )

                # Limpiar caché y mostrar uso de memoria
                if self.device.startswith("cuda"):
                    torch.cuda.empty_cache()
                    
                    # Actualizar información de memoria después de cargar
                    current_device = torch.cuda.current_device()
                    allocated = torch.cuda.memory_allocated(current_device) / 1024**3
                    reserved = torch.cuda.memory_reserved(current_device) / 1024**3
                    
                    if callback:
                        callback("✅ Modelo cargado correctamente en GPU")
                        callback(f"💾 VRAM usada por el modelo: {allocated:.1f} GB")
                        callback(f"💾 VRAM reservada total: {reserved:.1f} GB")
                else:
                    if callback:
                        callback("✅ Modelo cargado correctamente en CPU")
                        
            return True

        except Exception as exc:
            if callback:
                callback(f"❌ Error al cargar modelo: {exc}")
                if "out of memory" in str(exc).lower():
                    callback("💡 Sugerencia: Cierra otras aplicaciones que usen GPU")
                    callback("💡 O considera usar un modelo más pequeño")
            return False

    # ------------------------------------------------------------------
    #  Liberar recursos
    # ------------------------------------------------------------------
    def descargar_modelo(self):
        if self.model is not None:
            del self.model
            self.model = None
        if self.processor is not None:
            del self.processor
            self.processor = None

        if self.device == "cuda":
            torch.cuda.empty_cache()
        gc.collect()

    # ------------------------------------------------------------------
    #  Info de memoria
    # ------------------------------------------------------------------
    def obtener_uso_memoria(self):
        if self.device.startswith("cuda"):
            alloc = torch.cuda.memory_allocated() / 1024 ** 3
            reserv = torch.cuda.memory_reserved() / 1024 ** 3
            return f"GPU: {alloc:.1f} GB usado / {reserv:.1f} GB reservado"
        return "Modo CPU"
    
    def get_device_info(self):
        """Obtiene información completa del dispositivo"""
        return {
            "device": self.device,
            "gpu_info": self.gpu_info,
            "model_loaded": self.model is not None,
            "memory_usage": self.obtener_uso_memoria()
        }
    
    def is_gpu_available(self):
        """Verifica si GPU está disponible y funcionando"""
        return self.gpu_info.get("available", False)
    
    def get_gpu_name(self):
        """Obtiene el nombre de la GPU"""
        if self.is_gpu_available():
            return self.gpu_info.get("name", "GPU Desconocida")
        return "CPU"
    
    def check_gpu_memory_sufficient(self, required_gb=4.0):
        """Verifica si hay suficiente memoria GPU para el modelo"""
        if not self.is_gpu_available():
            return False, "GPU no disponible"
        
        free_memory = self.gpu_info.get("free_gb", 0)
        if free_memory >= required_gb:
            return True, f"Memoria suficiente: {free_memory:.1f} GB disponible"
        else:
            return False, f"Memoria insuficiente: {free_memory:.1f} GB disponible, se requieren {required_gb:.1f} GB"

    def _detect_best_device(self):
        """Detecta el mejor dispositivo disponible con información detallada"""
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            if gpu_count > 0:
                # Seleccionar GPU con más memoria libre
                best_device = 0
                max_free_memory = 0
                
                for i in range(gpu_count):
                    props = torch.cuda.get_device_properties(i)
                    total_memory = props.total_memory
                    
                    torch.cuda.set_device(i)
                    allocated = torch.cuda.memory_allocated(i)
                    free_memory = total_memory - allocated
                    
                    if free_memory > max_free_memory:
                        max_free_memory = free_memory
                        best_device = i
                
                torch.cuda.set_device(best_device)
                return f"cuda:{best_device}"
        
        return "cpu"
    
    def _get_gpu_info(self):
        """Obtiene información detallada de la GPU"""
        if not torch.cuda.is_available():
            return {"available": False, "reason": "CUDA no disponible"}
        
        try:
            current_device = torch.cuda.current_device()
            props = torch.cuda.get_device_properties(current_device)
            
            total_memory = props.total_memory / 1024**3  # GB
            allocated = torch.cuda.memory_allocated(current_device) / 1024**3
            reserved = torch.cuda.memory_reserved(current_device) / 1024**3
            free = total_memory - reserved
            
            return {
                "available": True,
                "device_id": current_device,
                "name": props.name,
                "total_memory_gb": round(total_memory, 1),
                "allocated_gb": round(allocated, 1),
                "reserved_gb": round(reserved, 1),
                "free_gb": round(free, 1),
                "compute_capability": f"{props.major}.{props.minor}",
                "cuda_version": torch.version.cuda
            }
        except Exception as e:
            return {"available": False, "error": str(e)}
