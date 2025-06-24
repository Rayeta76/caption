"""
Script para probar las diferentes opciones de Florence-2
Ejecuta: python probar_opciones.py
"""
import os
import sys

print("🧪 PROBADOR DE OPCIONES FLORENCE-2")
print("="*50)

# Verificar entorno
print("\n📋 Verificando entorno...")
import torch
print(f"✅ PyTorch: {torch.__version__}")
print(f"✅ CUDA: {torch.cuda.is_available()}")

# Añadir src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("\n🔍 Opciones disponibles:")
print("\n1. MODELO LOCAL (tu descarga)")
print("   Ruta: E:\\Proyectos\\Caption\\models\\Florence2-large")
print("   Pros: No necesita internet, carga más rápida")
print("   Contras: Puede tener problemas con timm 1.0.15")

print("\n2. MODELO SAFETENSORS (recomendado)")
print("   Modelo: mrhendrey/Florence-2-large-ft-safetensors")
print("   Pros: Más compatible, formato moderno, fine-tuned")
print("   Contras: Necesita descargar ~1.5GB la primera vez")

print("\n" + "-"*50)

# Opción 1: Probar modelo local
print("\n🧪 PRUEBA 1: Modelo Local")
try:
    # Verificar si existe
    ruta_local = r"E:\Proyectos\Caption\models\Florence2-large"
    if os.path.exists(ruta_local):
        print("✅ Carpeta del modelo encontrada")
        
        # Verificar archivos clave
        archivos_necesarios = ["config.json", "pytorch_model.bin", "model.safetensors"]
        archivos_encontrados = os.listdir(ruta_local)
        
        tiene_pytorch = "pytorch_model.bin" in archivos_encontrados
        tiene_safetensors = any(".safetensors" in f for f in archivos_encontrados)
        
        print(f"   - Formato PyTorch (.bin): {'✅' if tiene_pytorch else '❌'}")
        print(f"   - Formato Safetensors: {'✅' if tiene_safetensors else '❌'}")
        
    else:
        print("❌ No se encontró la carpeta del modelo local")
except Exception as e:
    print(f"❌ Error verificando modelo local: {e}")

# Opción 2: Verificar conectividad para Safetensors
print("\n🧪 PRUEBA 2: Verificar acceso a HuggingFace")
try:
    import requests
    response = requests.get("https://huggingface.co/api/models/mrhendrey/Florence-2-large-ft-safetensors", timeout=5)
    if response.status_code == 200:
        print("✅ Modelo Safetensors accesible en HuggingFace")
    else:
        print(f"⚠️ Código de respuesta: {response.status_code}")
except Exception as e:
    print(f"⚠️ No se pudo verificar: {e}")

# Recomendación
print("\n" + "="*50)
print("💡 RECOMENDACIÓN:")
print("\n1. Primero intenta con el modelo SAFETENSORS")
print("   Es más moderno y compatible con tu versión de timm")
print("\n2. Si no tienes internet o es muy lento, usa el LOCAL")
print("   Pero puede necesitar los parches del model_manager.py")

print("\n📝 Para usar en tu código:")
print("\n# Para modelo Safetensors (recomendado):")
print('manager = Florence2Manager(usar_local=False)')
print("\n# Para modelo local:")
print('manager = Florence2Manager(usar_local=True)')

# Prueba rápida opcional
print("\n" + "-"*50)
respuesta = input("\n¿Quieres hacer una prueba rápida ahora? (s/n): ").lower()

if respuesta == 's':
    print("\n¿Qué modelo quieres probar?")
    print("1. Local")
    print("2. Safetensors")
    
    opcion = input("Opción (1 o 2): ").strip()
    
    try:
        from core.model_manager import Florence2Manager
        
        usar_local = opcion == "1"
        print(f"\nProbando {'modelo local' if usar_local else 'modelo Safetensors'}...")
        
        manager = Florence2Manager(usar_local=usar_local)
        exito = manager.cargar_modelo(callback=print)
        
        if exito:
            print("\n🎉 ¡ÉXITO! El modelo se cargó correctamente")
            manager.descargar_modelo()
        else:
            print("\n❌ No se pudo cargar el modelo")
            print("Intenta con la otra opción")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nAsegúrate de:")
        print("1. Haber guardado el nuevo model_manager.py")
        print("2. Estar en la carpeta correcta del proyecto")

print("\n✨ ¡Listo!")