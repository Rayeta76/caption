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
    print("🚀 Iniciando StockPrep Pro...")
    
    # Verificar qué GUI usar
    use_pyside6 = False
    try:
        import PySide6
        use_pyside6 = True
        print("✅ PySide6 detectado - Usando interfaz Windows 11")
    except ImportError:
        print("ℹ️ PySide6 no instalado - Usando interfaz Tkinter")
    
    try:
        if use_pyside6:
            # Usar nueva interfaz moderna Windows 11
            try:
                from gui.modern_gui_win11 import StockPrepWin11App
                app = StockPrepWin11App()
                app.run()
            except ImportError:
                print("⚠️ Error importando interfaz PySide6, usando Tkinter...")
                use_pyside6 = False
        
        if not use_pyside6:
            # Usar interfaz Tkinter existente
            try:
                from gui.modern_gui_stockprep import StockPrepApp
                app = StockPrepApp()
                app.run()
            except ImportError:
                # Fallback a la interfaz original
                from gui.main_window import MainWindow
                app = MainWindow()
                app.run()
        
    except ImportError as e:
        print(f"❌ Error al importar módulos: {e}")
        print("\nPor favor, verifica que todas las dependencias estén instaladas:")
        print("pip install -r requirements.txt")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
