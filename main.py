"""
Archivo principal de StockPrep
Punto de entrada con soporte de argumentos:
  - --gui [pyside|tkinter]
  - --cli
"""
import sys
import os
from pathlib import Path
import argparse
import logging, os
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Añadir el directorio 'src' al path para poder importar módulos locales
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir / 'src'))

def setup_logging():
    level_name = os.getenv("STOCKPREP_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    logs_dir = Path(__file__).resolve().parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    log_file = logs_dir / "stockprep.log"

    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    handlers = [
        logging.StreamHandler(),
        RotatingFileHandler(log_file, maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    ]

    logging.basicConfig(level=level, format=fmt, datefmt=datefmt, handlers=handlers)

setup_logging()

def run_gui_pyside():
    # Import diferido para no fallar si PySide6 no está instalado
    try:
        from gui.main_control_pyside import start_pyside_app
    except Exception as exc:
        print(f"❌ No se pudo iniciar PySide6: {exc}")
        return False
    start_pyside_app()
    return True

def run_gui_tkinter():
    # Import diferido para no fallar si Tkinter no está disponible
    try:
        from gui.inicio_gui import main as start_tk
    except Exception as exc:
        print(f"❌ No se pudo iniciar la GUI Tkinter: {exc}")
        return False
    start_tk()
    return True

def run_cli():
    """Modo CLI mínimo: procesa una imagen de ejemplo si se pasa --image."""
    from core.model_manager import Florence2Manager
    from core.image_processor import ImageProcessor
    parser = argparse.ArgumentParser(description="StockPrep Pro - CLI")
    parser.add_argument("--image", help="Ruta a la imagen a procesar")
    parser.add_argument("--detail", default="largo", choices=["minimo", "medio", "largo"], help="Nivel de detalle")
    args_cli, _ = parser.parse_known_args()

    if not args_cli.image:
        print("Uso: python main.py --cli --image ruta/imagen.jpg [--detail minimo|medio|largo]")
        return

    manager = Florence2Manager()
    ok = manager.cargar_modelo(callback=print)
    if not ok:
        print("❌ No se pudo cargar el modelo")
        return

    processor = ImageProcessor(manager)
    result = processor.process_image(args_cli.image, args_cli.detail)
    if result.get("error"):
        print(f"❌ Error: {result['error']}")
        return
    print("📝 Descripción:", result.get("caption") or result.get("descripcion"))
    print("🏷️ Keywords:", ", ".join(result.get("keywords", [])))
    print("🔍 Objetos:", result.get("objects"))

def main():
    """
    Punto de entrada principal para la aplicación StockPrep Pro v2.0.
    Soporta GUI PySide6/Tkinter y modo CLI.
    """
    parser = argparse.ArgumentParser(description="StockPrep Pro v2.0")
    parser.add_argument("--gui", choices=["pyside", "tkinter"], help="Seleccionar interfaz gráfica")
    parser.add_argument("--cli", action="store_true", help="Ejecutar en modo línea de comandos")
    args, unknown = parser.parse_known_args()

    if args.cli:
        run_cli()
        return

    gui_choice = args.gui or "pyside"
    print(f"🚀 Iniciando StockPrep Pro v2.0 - GUI {gui_choice}...")

    if gui_choice == "pyside":
        started = run_gui_pyside()
        if not started:
            print("↩️ Haciendo fallback automático a Tkinter...")
            if not run_gui_tkinter():
                print("❌ No se pudo iniciar ninguna interfaz gráfica.")
    else:
        if not run_gui_tkinter():
            print("❌ No se pudo iniciar la interfaz Tkinter.")

if __name__ == "__main__":
    main()
