"""
Archivo principal de StockPrep
Este archivo inicia toda la aplicación
"""
import sys
from pathlib import Path

# Añadir la carpeta src al path de Python
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def main():
    """
    Función principal que inicia la aplicación StockPrep.
    Ahora inicia con la GUI de inicio basada en PySide6.
    """
    print("🚀 Iniciando StockPrep Pro v2.0 - Centro de Control...")

    try:
        from PySide6.QtWidgets import QApplication
        from gui.pyside_startup_gui import StockPrepStartupWindow
    except ImportError as e:
        print(f"❌ PySide6 no está disponible: {e}")
        print("Instala las dependencias con: pip install -r requirements.txt")
        return

    qt_app = QApplication.instance() or QApplication(sys.argv)
    window = StockPrepStartupWindow()
    window.show()
    qt_app.exec()


if __name__ == "__main__":
    main()
