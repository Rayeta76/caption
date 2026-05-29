#!/usr/bin/env python3
"""Smoke test for bilingual metadata parsing and database persistence."""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TMP_DIR = ROOT / "temp" / "bilingual_smoke"
TMP_DB = TMP_DIR / "smoke_stockprep.db"
TMP_IMAGE = TMP_DIR / "smoke_image.jpg"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    if TMP_DB.exists():
        TMP_DB.unlink()
    if TMP_IMAGE.exists():
        TMP_IMAGE.unlink()

    Image.new("RGB", (64, 64), (24, 120, 96)).save(TMP_IMAGE, "JPEG", quality=90)

    from src.core.enhanced_database_manager_v2 import EnhancedDatabaseManagerV2
    from src.core.model_registry import get_model_profiles, get_processing_modes
    from src.utils.bilingual_metadata import parse_bilingual_model_output

    raw_model_output = json.dumps(
        {
            "caption_en": "A minimal studio test image with a green square on a neutral background.",
            "caption_es": "Una imagen de prueba de estudio con un cuadrado verde sobre un fondo neutro.",
            "keywords_en": ["studio", "green", "square", "test image"],
            "keywords_es": ["estudio", "verde", "cuadrado", "imagen de prueba"],
        },
        ensure_ascii=False,
    )

    parsed = parse_bilingual_model_output(raw_model_output)
    db = EnhancedDatabaseManagerV2(str(TMP_DB))
    image_id = db.obtener_o_crear_registro_id(str(TMP_IMAGE))
    if image_id is None:
        raise RuntimeError("Could not create smoke test image record")

    ok = db.actualizar_procesamiento_completo(
        image_id,
        {
            **parsed,
            "objetos_detectados": [],
        },
        "smoke_image_output.jpg",
        str(TMP_IMAGE),
    )
    if not ok:
        raise RuntimeError("Could not persist bilingual smoke test metadata")

    with sqlite3.connect(TMP_DB) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            """
            SELECT caption_en, caption_es, keywords_en, keywords_es, caption, keywords
            FROM imagenes
            WHERE id = ?
            """,
            (image_id,),
        ).fetchone()

    payload = dict(row)
    checks = {
        "caption_en": bool(payload["caption_en"]),
        "caption_es": bool(payload["caption_es"]),
        "keywords_en": bool(json.loads(payload["keywords_en"] or "[]")),
        "keywords_es": bool(json.loads(payload["keywords_es"] or "[]")),
        "legacy_caption_matches_en": payload["caption"] == payload["caption_en"],
        "legacy_keywords_match_en": payload["keywords"] == payload["keywords_en"],
        "model_profiles_available": len(get_model_profiles()) >= 3,
        "processing_modes_available": len(get_processing_modes()) >= 3,
    }

    print(json.dumps({"ok": all(checks.values()), "checks": checks}, ensure_ascii=False, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
