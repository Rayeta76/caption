"""Helpers to normalize bilingual stock metadata.

The legacy pipeline stored a single caption and keyword list. Newer records can
carry English and Spanish variants while keeping the old fields populated for
compatibility with existing UI and export code.
"""

from __future__ import annotations

import json
import re
from typing import Any


def coerce_keyword_list(value: Any) -> list[str]:
    """Return a clean list of keywords from JSON, comma text, or a Python list."""
    if value in (None, ""):
        return []
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        try:
            parsed = json.loads(text)
            return coerce_keyword_list(parsed)
        except (TypeError, json.JSONDecodeError):
            parts = re.split(r"[,;\n]", text)
            return _dedupe([part.strip() for part in parts if part.strip()])
    if isinstance(value, (tuple, set)):
        value = list(value)
    if isinstance(value, list):
        return _dedupe([str(item).strip() for item in value if str(item).strip()])
    return [str(value).strip()] if str(value).strip() else []


def normalize_bilingual_results(results: dict[str, Any] | None) -> dict[str, Any]:
    """Build normalized bilingual metadata from a result dictionary."""
    data = results or {}

    caption_en = _first_text(
        data.get("caption_en"),
        data.get("description_en"),
        data.get("descripcion_en"),
        data.get("caption"),
        data.get("descripcion"),
    )
    caption_es = _first_text(
        data.get("caption_es"),
        data.get("description_es"),
        data.get("descripcion_es"),
    )

    keywords_en = coerce_keyword_list(
        data.get("keywords_en") or data.get("keywords") or data.get("tags_en")
    )
    keywords_es = coerce_keyword_list(data.get("keywords_es") or data.get("tags_es"))

    return {
        "caption": caption_en,
        "descripcion": caption_en,
        "caption_en": caption_en,
        "caption_es": caption_es,
        "keywords": keywords_en,
        "keywords_en": keywords_en,
        "keywords_es": keywords_es,
    }


def merge_bilingual_results(results: dict[str, Any] | None) -> dict[str, Any]:
    """Return a copy of results with legacy and bilingual keys aligned."""
    merged = dict(results or {})
    normalized = normalize_bilingual_results(merged)
    for key, value in normalized.items():
        if value not in ("", [], None):
            merged[key] = value
    merged.setdefault("caption", normalized["caption"])
    merged.setdefault("descripcion", normalized["descripcion"])
    merged.setdefault("keywords", normalized["keywords"])
    return merged


def legacy_title_from_caption(caption: str, max_chars: int = 80) -> str:
    """Create a short title from the first sentence of a caption."""
    caption = (caption or "").strip()
    if not caption:
        return ""
    first = re.split(r"[.!?]\s", caption, maxsplit=1)[0].strip()
    return first[:max_chars].strip()


def _first_text(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    clean: list[str] = []
    for item in items:
        key = item.casefold()
        if key in seen:
            continue
        seen.add(key)
        clean.append(item)
    return clean
