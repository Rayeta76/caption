"""Gestor sencillo de registros de imágenes.

Este módulo almacena en un archivo JSON la información
básica de las imágenes procesadas. Es una implementación
mínima para que la GUI pueda funcionar sin errores.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class ImageDatabase:
    """Base de datos muy simple basada en JSON."""

    def __init__(self, db_path: str | Path = "image_database.json") -> None:
        self.db_path = Path(db_path)
        self._registros: list[Dict[str, Any]] = []
        self._load()

    def _load(self) -> None:
        if self.db_path.is_file():
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    self._registros = json.load(f) or []
            except Exception:
                self._registros = []

    def _save(self) -> None:
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump(self._registros, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def guardar_imagen(self, **info: Any) -> int:
        """Guarda la información de una imagen y devuelve su ID."""
        registro_id = len(self._registros) + 1
        info["id"] = registro_id
        self._registros.append(info)
        self._save()
        return registro_id

