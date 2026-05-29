#!/usr/bin/env python3
"""Backfill bilingual metadata columns in an existing StockPrep database."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "stockprep_images.db"

BILINGUAL_COLUMNS = {
    "caption_en": "TEXT",
    "caption_es": "TEXT",
    "keywords_en": "TEXT",
    "keywords_es": "TEXT",
}


def refresh(db_path: Path) -> tuple[int, int]:
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(imagenes)")
        existing = {column[1] for column in cursor.fetchall()}

        added = 0
        for column, column_type in BILINGUAL_COLUMNS.items():
            if column not in existing:
                cursor.execute(f"ALTER TABLE imagenes ADD COLUMN {column} {column_type}")
                added += 1

        cursor.execute(
            """
            UPDATE imagenes
            SET
                caption_en = COALESCE(NULLIF(caption_en, ''), caption),
                keywords_en = COALESCE(NULLIF(keywords_en, ''), keywords)
            WHERE (caption_en IS NULL OR caption_en = '' OR keywords_en IS NULL OR keywords_en = '')
            """
        )
        updated = cursor.rowcount
        conn.commit()

    return added, updated


def main() -> int:
    parser = argparse.ArgumentParser(description="Backfill bilingual metadata columns")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to stockprep_images.db")
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.is_absolute():
        db_path = ROOT / db_path
    if not db_path.exists():
        raise SystemExit(f"Database not found: {db_path}")

    added, updated = refresh(db_path)
    print(f"Database: {db_path}")
    print(f"Columns added: {added}")
    print(f"Rows backfilled: {updated}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
