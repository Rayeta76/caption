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
=======
import sqlite3
import json
from pathlib import Path

class ImageDatabase:
    """Gestor muy simple de registros de imágenes en SQLite."""
    def __init__(self, db_path: str | Path = "stockprep.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self._create_table()

    def _create_table(self):
        cur = self.conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS imagenes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_original TEXT,
                nombre_nuevo TEXT,
                descripcion TEXT,
                keywords TEXT,
                ruta_original TEXT,
                ruta_nueva TEXT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        self.conn.commit()

    def guardar_imagen(self, nombre_original: str, nombre_nuevo: str,
                       descripcion: str, keywords: list[str],
                       ruta_original: str, ruta_nueva: str) -> int:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO imagenes (nombre_original, nombre_nuevo, descripcion, keywords, ruta_original, ruta_nueva)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (
                nombre_original,
                nombre_nuevo,
                descripcion,
                json.dumps(keywords, ensure_ascii=False),
                ruta_original,
                ruta_nueva,
            ),
        )
        self.conn.commit()
        return cur.lastrowid

