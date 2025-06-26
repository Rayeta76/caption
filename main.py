"""
Archivo principal de StockPrep
Este archivo inicia toda la aplicación
"""
import sys
import os
from pathlib import Path

# Añadir la carpeta src al path de Python
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """
    Función principal que inicia la aplicación StockPrep.
    Crea la instancia de la aplicación y ejecuta el bucle principal.
    """
    print("🚀 Iniciando StockPrep...")
    
    try:
        # Importar y ejecutar la interfaz gráfica moderna
        from gui.modern_gui_stockprep import StockPrepApp
        app = StockPrepApp()
        app.run()
        
    except ImportError as e:
        print(f"❌ Error al importar módulos: {e}")
        print("\nPor favor, verifica que todas las dependencias estén instaladas:")
        print("conda activate florence2")
        print("pip install transformers torch pillow")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
