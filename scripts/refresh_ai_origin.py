#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.ai_origin import detect_ai_origin


def _json_load(value):
    if not value:
        return {}
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return {}


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh AI origin metadata in stockprep_images.db")
    parser.add_argument("--db", default=str(ROOT / "stockprep_images.db"), help="Ruta a la base SQLite")
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.is_absolute():
        db_path = (ROOT / db_path).resolve()

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, nombre_original, ruta_completa, ruta_salida, metadatos_exif FROM imagenes"
        ).fetchall()

        updated = 0
        for row in rows:
            image_path = row["ruta_salida"] or row["ruta_completa"]
            metadata = _json_load(row["metadatos_exif"])
            metadata["ai_origin"] = detect_ai_origin(
                image_path=image_path,
                metadata=metadata,
                original_name=row["nombre_original"],
            )
            conn.execute(
                "UPDATE imagenes SET metadatos_exif = ? WHERE id = ?",
                (json.dumps(metadata, ensure_ascii=False), row["id"]),
            )
            updated += 1

        conn.commit()

    print(f"BD: {db_path}")
    print(f"Registros actualizados: {updated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
