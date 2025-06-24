"""
Script para descargar Florence-2 localmente
Esto evita problemas de red y versiones
"""
import os
from huggingface_hub import snapshot_download

# Configurar la ruta donde quieres guardar el modelo
RUTA_MODELOS = r"E:\Modelos\Florence2-large"

print("🚀 Iniciando descarga de Florence-2-large...")
print(f"📁 Se guardará en: {RUTA_MODELOS}")
print("⏳ Esto puede tardar 10-20 minutos dependiendo de tu conexión")
print("-" * 50)

try:
    # Crear la carpeta si no existe
    os.makedirs(RUTA_MODELOS, exist_ok=True)
    
    # Descargar el modelo completo
    snapshot_download(
        repo_id="microsoft/Florence-2-large",
        local_dir=RUTA_MODELOS,
        local_dir_use_symlinks=False,
        resume_download=True
    )
    
    print("\n✅ ¡Descarga completada!")
    print(f"📁 Modelo guardado en: {RUTA_MODELOS}")
    print("\n📝 Ahora actualiza tu model_manager.py:")
    print(f'   self.model_id = r"{RUTA_MODELOS}"')
    
except Exception as e:
    print(f"\n❌ Error durante la descarga: {e}")
    print("\n💡 Alternativa: Descarga manualmente desde:")
    print("   https://huggingface.co/microsoft/Florence-2-large/tree/main")
    print("   Descarga TODOS los archivos a la carpeta:", RUTA_MODELOS)