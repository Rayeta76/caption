"""
Diagnóstico del problema Florence-2 / timm
"""
import sys
print("🔍 DIAGNÓSTICO DE FLORENCE-2\n")

# 1. Verificar versión de Python
print(f"1. Python: {sys.version}")

# 2. Verificar librerías clave
try:
    import torch
    print(f"\n2. PyTorch: {torch.__version__}")
    print(f"   CUDA: {torch.cuda.is_available()} - {torch.version.cuda if torch.cuda.is_available() else 'N/A'}")
except ImportError:
    print("❌ PyTorch no instalado")

try:
    import timm
    print(f"\n3. timm: {timm.__version__}")
    
    # Verificar si timm tiene los métodos esperados
    print("   Verificando métodos de timm:")
    
    # Intentar crear un modelo DaViT si existe
    try:
        if hasattr(timm, 'create_model'):
            # Ver qué modelos DaViT están disponibles
            import timm.models
            davit_models = [m for m in timm.list_models() if 'davit' in m.lower()]
            print(f"   Modelos DaViT disponibles: {len(davit_models)}")
            if davit_models:
                print(f"   Ejemplo: {davit_models[0]}")
    except Exception as e:
        print(f"   ⚠️ Error verificando modelos: {e}")
        
except ImportError:
    print("❌ timm no instalado")

try:
    import transformers
    print(f"\n4. Transformers: {transformers.__version__}")
except ImportError:
    print("❌ Transformers no instalado")

# 5. Probar carga básica del procesador
print("\n5. Probando carga del procesador Florence-2...")
try:
    from transformers import AutoProcessor
    processor = AutoProcessor.from_pretrained(
        "microsoft/Florence-2-large",
        trust_remote_code=True
    )
    print("   ✅ Procesador cargado correctamente")
except Exception as e:
    print(f"   ❌ Error al cargar procesador: {e}")

# 6. Verificar el problema específico
print("\n6. Información sobre el problema:")
print("   El error 'DaViT object has no attribute _initialize_weights' ocurre porque:")
print("   - Florence-2 usa una versión interna modificada de DaViT")
print("   - Esta versión espera métodos de timm < 1.0.0")
print("   - Tu timm 1.0.15 tiene una API diferente")
print("\n   SOLUCIONES:")
print("   1. Usar el model_manager.py parcheado (recomendado)")
print("   2. Descargar el modelo localmente (más estable)")
print("   3. Downgrade timm a 0.9.16 (NO recomendado - puede romper otras cosas)")

print("\n" + "="*50)
print("✨ Usa el model_manager.py corregido que te proporcioné")
print("   Si falla, usa el script descargar_modelo.py")
print("="*50)