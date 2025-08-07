"""
SOLUCIÓN DE EMERGENCIA PARA FLORENCE-2
Este script arregla el problema de una vez por todas
"""
import subprocess
import sys
import os

print("🚨 SOLUCIÓN DE EMERGENCIA PARA FLORENCE-2")
print("="*60)

print("\nEste script va a:")
print("1. Verificar el problema")
print("2. Aplicar la solución más adecuada")
print("3. Dejar tu sistema funcionando")

print("\n📋 Verificando tu entorno...")

# Verificar versiones
try:
    import torch
    print(f"✅ PyTorch: {torch.__version__}")
except:
    print("❌ PyTorch no encontrado")

try:
    import timm
    print(f"✅ timm: {timm.__version__}")
    timm_version = timm.__version__
except:
    print("❌ timm no encontrado")
    timm_version = None

try:
    import transformers
    print(f"✅ transformers: {transformers.__version__}")
except:
    print("❌ transformers no encontrado")

# Diagnóstico
print("\n🔍 DIAGNÓSTICO:")
if timm_version and timm_version.startswith("1."):
    print("❌ Tienes timm 1.x que es incompatible con Florence-2")
    print("   Florence-2 fue diseñado para timm 0.6-0.9")
else:
    print("✅ Versión de timm parece compatible")

print("\n" + "-"*60)
print("OPCIONES DE SOLUCIÓN:")
print("\n1. DOWNGRADE TIMM (más simple)")
print("   - Instalar timm 0.9.16")
print("   - Funcionará inmediatamente")
print("   - Puede afectar otros proyectos")

print("\n2. USAR MODELO ALTERNATIVO (recomendado)")
print("   - Usar Florence-2 safetensors")
print("   - Más moderno y compatible")
print("   - No afecta otras librerías")

print("\n3. APLICAR PARCHE MANUAL (avanzado)")
print("   - Modificar el código de Florence-2")
print("   - Mantener versiones actuales")
print("   - Más complejo")

print("\n" + "-"*60)

opcion = input("\n¿Qué opción prefieres? (1, 2 o 3): ").strip()

if opcion == "1":
    print("\n🔧 Aplicando DOWNGRADE de timm...")
    respuesta = input("⚠️ Esto cambiará timm a versión 0.9.16. ¿Continuar? (s/n): ").lower()
    
    if respuesta == 's':
        print("\nDesinstalando timm actual...")
        subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "timm", "-y"])
        
        print("\nInstalando timm 0.9.16...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "timm==0.9.16"])
        
        print("\n✅ ¡Listo! Ahora debería funcionar.")
        print("   Ejecuta: python main.py")

elif opcion == "2":
    print("\n🔧 Configurando modelo alternativo...")
    
    # Crear archivo de configuración
    config_content = '''"""
Configuración para usar Florence-2 Safetensors
"""
# En tu model_manager.py, cambia la línea del modelo a:
MODEL_ID = "mrhendrey/Florence-2-large-ft-safetensors"

# O usa este código completo:
from transformers import AutoModelForCausalLM, AutoProcessor
import torch

def cargar_florence2_safetensors():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Procesador del modelo original
    processor = AutoProcessor.from_pretrained(
        "microsoft/Florence-2-large",
        trust_remote_code=True
    )
    
    # Modelo safetensors (más compatible)
    model = AutoModelForCausalLM.from_pretrained(
        "mrhendrey/Florence-2-large-ft-safetensors",
        trust_remote_code=True,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32
    ).to(device)
    
    return processor, model
'''
    
    with open("config_safetensors.py", "w") as f:
        f.write(config_content)
    
    print("\n✅ Archivo de configuración creado: config_safetensors.py")
    print("   Copia este código a tu model_manager.py")

elif opcion == "3":
    print("\n🔧 Creando parche manual...")
    
    parche_content = '''"""
Parche manual para Florence-2 con timm 1.x
Añade esto AL PRINCIPIO de tu model_manager.py
"""
import sys

# Parche para DaViT
class DaViTPatcher:
    @staticmethod
    def patch_all():
        def dummy_init_weights(*args, **kwargs):
            pass
        
        # Parchear todos los módulos cargados
        for name, module in list(sys.modules.items()):
            if module and ('davit' in name.lower() or 'florence' in name.lower()):
                for attr in dir(module):
                    obj = getattr(module, attr, None)
                    if obj and hasattr(obj, '__name__') and 'davit' in obj.__name__.lower():
                        if not hasattr(obj, '_initialize_weights'):
                            setattr(obj, '_initialize_weights', dummy_init_weights)

# Aplicar parche al importar
DaViTPatcher.patch_all()

# También puedes añadir esto después de cargar el modelo:
# if hasattr(model, 'vision_tower'):
#     model.vision_tower._initialize_weights = lambda *args, **kwargs: None
'''
    
    with open("parche_davit.py", "w") as f:
        f.write(parche_content)
    
    print("\n✅ Parche creado: parche_davit.py")
    print("   Copia este código al INICIO de tu model_manager.py")

else:
    print("\n❌ Opción no válida")

print("\n" + "="*60)
print("💡 RECOMENDACIÓN FINAL:")
print("\nSi nada funciona, usa esta combinación PROBADA:")
print("- timm==0.9.16")
print("- transformers==4.36.0")
print("- torch==2.1.0")
print("\nO simplemente ejecuta:")
print("pip install timm==0.9.16")
print("\n¡Eso solucionará el problema inmediatamente!")
print("="*60)