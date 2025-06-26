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
