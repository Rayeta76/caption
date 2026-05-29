#!/usr/bin/env python3
"""
Import images into the StockPrep gallery database.

This is useful to test the local web gallery with many images before running
the full AI captioning workflow.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.core.enhanced_database_manager_v2 import EnhancedDatabaseManagerV2


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tif", ".tiff"}


def iter_images(folder: Path, recursive: bool):
    pattern = "**/*" if recursive else "*"
    for path in folder.glob(pattern):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            yield path


def main() -> int:
    parser = argparse.ArgumentParser(description="Import images into stockprep_images.db")
    parser.add_argument("folder", help="Carpeta con imagenes")
    parser.add_argument("--db", default=str(ROOT / "stockprep_images.db"), help="Ruta a la base SQLite")
    parser.add_argument("--recursive", action="store_true", help="Buscar tambien en subcarpetas")
    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.is_absolute():
        folder = (Path.cwd() / folder).resolve()
    if not folder.is_dir():
        raise SystemExit(f"No existe la carpeta: {folder}")

    db_path = Path(args.db)
    if not db_path.is_absolute():
        db_path = (ROOT / db_path).resolve()

    manager = EnhancedDatabaseManagerV2(str(db_path))
    imported = 0
    skipped = 0

    for image_path in iter_images(folder, args.recursive):
        if manager.insertar_imagen_automatica(str(image_path.resolve())):
            imported += 1
            print(f"OK  {image_path.name}")
        else:
            skipped += 1
            print(f"SKIP {image_path.name}")

    print()
    print(f"BD: {db_path}")
    print(f"Importadas: {imported}")
    print(f"Omitidas o existentes: {skipped}")
    print("Abre o recarga: http://127.0.0.1:8000/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
