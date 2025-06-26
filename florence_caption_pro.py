"""Entrypoint para la interfaz moderna Florence-2 Image Captioning Pro"""
import sys
from pathlib import Path

# Añadir src al PYTHONPATH
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from gui.florence_caption_pro import CaptionProApp

if __name__ == "__main__":
    app = CaptionProApp()
    app.run()
