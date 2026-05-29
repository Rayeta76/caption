#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.core.enhanced_database_manager_v2 import EnhancedDatabaseManagerV2


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh WebP thumbnails for the StockPrep gallery")
    parser.add_argument("--db", default=str(ROOT / "stockprep_images.db"), help="Ruta a la base SQLite")
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.is_absolute():
        db_path = (ROOT / db_path).resolve()

    # Instantiating V2 migrates missing thumbnails.
    EnhancedDatabaseManagerV2(str(db_path))

    with sqlite3.connect(db_path) as conn:
        total = conn.execute("SELECT COUNT(*) FROM imagenes").fetchone()[0]
        thumbs = conn.execute("SELECT COUNT(*) FROM imagenes WHERE thumbnail_webp IS NOT NULL").fetchone()[0]

    print(f"BD: {db_path}")
    print(f"Imagenes: {total}")
    print(f"Miniaturas WebP: {thumbs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
