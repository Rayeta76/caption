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
    Ahora inicia con la GUI de inicio que permite acceder a los diferentes módulos.
    """
    print("🚀 Iniciando StockPrep Pro v2.0 - Centro de Control...")
    
    try:
        # Usar la nueva GUI de inicio como punto de entrada principal
        from gui.inicio_gui import StockPrepStartupApp
        app = StockPrepStartupApp()
        app.run()
        
    except ImportError as e:
        print(f"❌ Error al importar módulos: {e}")
        print("⚠️ Intentando cargar interfaz de reconocimiento directamente...")
        
        # Fallback al sistema anterior si la GUI de inicio falla
        try:
            # Verificar qué GUI usar para reconocimiento
            use_pyside6 = False
            try:
                import PySide6
                use_pyside6 = True
                print("✅ PySide6 detectado - Usando interfaz Windows 11")
            except ImportError:
                print("ℹ️ PySide6 no instalado - Usando interfaz Tkinter")
            
            if use_pyside6:
                # Usar interfaz moderna Windows 11
                try:
                    from PySide6.QtWidgets import QApplication
                    from gui.modern_gui_win11 import StockPrepWin11App
                    
                    # Crear QApplication primero
                    qt_app = QApplication.instance()
                    if qt_app is None:
                        qt_app = QApplication(sys.argv)
                    
                    # Crear y ejecutar la aplicación
                    app = StockPrepWin11App()
                    app.show()
                    qt_app.exec()
                    
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
                    print("❌ No se pudo cargar ninguna interfaz disponible")
                    print("Verifica que los archivos de GUI estén presentes")
        
        except Exception as fallback_error:
            print(f"❌ Error en fallback: {fallback_error}")
            print("\nPor favor, verifica que todas las dependencias estén instaladas:")
            print("pip install -r requirements.txt")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
