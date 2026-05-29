#!/usr/bin/env python3
"""
Local web gallery for StockPrep.

Serves the SQLite catalog, WebP thumbnails stored in BLOBs, and original images
from disk through a small standard-library HTTP server.
"""
from __future__ import annotations

import argparse
import json
import mimetypes
import re
import sys
import sqlite3
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = ROOT / "web" / "gallery"
DEFAULT_DB = ROOT / "stockprep_images.db"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tif", ".tiff"}

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.utils.ai_origin import detect_ai_origin


def _json_load(value, fallback):
    if value in (None, ""):
        return fallback
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        if isinstance(fallback, list):
            return [item.strip() for item in str(value).split(",") if item.strip()]
        return fallback


def _image_path(record: sqlite3.Row) -> Path | None:
    for key in ("ruta_salida", "ruta_completa"):
        value = record[key] if key in record.keys() else None
        if not value:
            continue
        path = Path(value)
        if not path.is_absolute():
            path = ROOT / path
        if path.exists() and path.suffix.lower() in IMAGE_EXTENSIONS:
            return path
    return None


def _clean_fts_query(query: str) -> str:
    tokens = re.findall(r"[\wáéíóúüñÁÉÍÓÚÜÑ-]+", query, flags=re.UNICODE)
    return " ".join(f"{token}*" for token in tokens[:8])


class GalleryRequestHandler(BaseHTTPRequestHandler):
    server: "GalleryHTTPServer"

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} - {fmt % args}")

    def do_HEAD(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)
        if path in ("/", "/index.html"):
            return self._serve_static(WEB_ROOT / "index.html", "text/html; charset=utf-8", head_only=True)
        if path.startswith("/static/"):
            rel = path.removeprefix("/static/").strip("/")
            return self._serve_static(WEB_ROOT / rel, head_only=True)
        if path.startswith("/thumb/"):
            return self._serve_thumbnail(path, head_only=True)
        if path.startswith("/media/"):
            return self._serve_media(path, head_only=True)
        self.send_error(HTTPStatus.NOT_FOUND, "Ruta no encontrada")

    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        try:
            if path in ("/", "/index.html"):
                return self._serve_static(WEB_ROOT / "index.html", "text/html; charset=utf-8")
            if path.startswith("/static/"):
                rel = path.removeprefix("/static/").strip("/")
                return self._serve_static(WEB_ROOT / rel)
            if path == "/api/stats":
                return self._send_json(self._api_stats())
            if path == "/api/images":
                return self._send_json(self._api_images(parse_qs(parsed.query)))
            if path.startswith("/api/images/"):
                return self._send_json(self._api_image_detail(path))
            if path.startswith("/thumb/"):
                return self._serve_thumbnail(path)
            if path.startswith("/media/"):
                return self._serve_media(path)
            self.send_error(HTTPStatus.NOT_FOUND, "Ruta no encontrada")
        except Exception as exc:
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, str(exc))

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.server.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _serve_static(self, file_path: Path, content_type: str | None = None, head_only: bool = False):
        try:
            resolved = file_path.resolve()
            resolved.relative_to(WEB_ROOT.resolve())
        except ValueError:
            self.send_error(HTTPStatus.FORBIDDEN, "Archivo fuera de la web")
            return

        if not resolved.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "Archivo no encontrado")
            return

        if content_type is None:
            content_type = mimetypes.guess_type(str(resolved))[0] or "application/octet-stream"
            if resolved.suffix in {".css", ".js"}:
                content_type += "; charset=utf-8"

        data = resolved.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if not head_only:
            self.wfile.write(data)

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK):
        data = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _row_to_card(self, row: sqlite3.Row) -> dict:
        keywords = _json_load(row["keywords"], [])
        caption = row["caption"] or row["descripcion"] or row["titulo"] or ""
        return {
            "id": row["id"],
            "name": row["nombre_renombrado"] or row["nombre_original"] or f"Imagen {row['id']}",
            "caption": caption,
            "keywords": keywords,
            "format": row["formato"],
            "width": row["ancho"],
            "height": row["alto"],
            "state": row["estado"],
            "model": row["modelo_ia_usado"],
            "processedAt": row["fecha_procesamiento"],
            "hasThumbnail": bool(row["thumbnail_webp"]),
            "thumbnailSize": row["thumbnail_size"] or 0,
        }

    def _row_to_detail(self, row: sqlite3.Row) -> dict:
        detail = self._row_to_card(row)
        metadata = _json_load(row["metadatos_exif"], {})
        file_path = _image_path(row)
        ai_origin = metadata.get("ai_origin") if isinstance(metadata, dict) else None
        if not ai_origin:
            ai_origin = detect_ai_origin(
                image_path=file_path,
                metadata=metadata,
                original_name=row["nombre_original"],
            )
        detail.update(
            {
                "originalPath": row["ruta_completa"],
                "outputPath": row["ruta_salida"],
                "originalName": row["nombre_original"],
                "title": row["titulo"],
                "description": row["descripcion"],
                "objects": _json_load(row["objetos_detectados"], []),
                "tags": _json_load(row["etiquetas"], []),
                "aiOrigin": ai_origin,
                "notes": row["notas"],
                "sizeBytes": row["tamano_bytes"],
                "hash": row["hash_md5"],
                "createdAt": row["fecha_creacion"],
                "updatedAt": row["fecha_actualizacion"],
            }
        )
        return detail

    def _api_stats(self) -> dict:
        with self._connect() as conn:
            total = conn.execute("SELECT COUNT(*) FROM imagenes").fetchone()[0]
            processed = conn.execute("SELECT COUNT(*) FROM imagenes WHERE estado = 'completed'").fetchone()[0]
            thumbs = conn.execute("SELECT COUNT(*) FROM imagenes WHERE thumbnail_webp IS NOT NULL").fetchone()[0]
            formats = [
                {"format": row["formato"] or "sin formato", "count": row["count"]}
                for row in conn.execute(
                    """
                    SELECT formato, COUNT(*) AS count
                    FROM imagenes
                    GROUP BY formato
                    ORDER BY count DESC, formato
                    """
                )
            ]
        return {"total": total, "processed": processed, "withThumbnails": thumbs, "formats": formats}

    def _api_images(self, params: dict[str, list[str]]) -> dict:
        page = max(int(params.get("page", ["1"])[0] or 1), 1)
        limit = min(max(int(params.get("limit", ["36"])[0] or 36), 1), 120)
        offset = (page - 1) * limit
        query = (params.get("q", [""])[0] or "").strip()
        image_format = (params.get("format", [""])[0] or "").strip().lower()
        state = (params.get("state", [""])[0] or "").strip()

        where = []
        values: list[object] = []
        if image_format:
            where.append("LOWER(i.formato) = ?")
            values.append(image_format)
        if state:
            where.append("i.estado = ?")
            values.append(state)

        if query:
            rows, total = self._search_images(query, where, values, limit, offset)
        else:
            rows, total = self._list_images(where, values, limit, offset)

        return {
            "items": [self._row_to_card(row) for row in rows],
            "page": page,
            "limit": limit,
            "total": total,
            "pages": max((total + limit - 1) // limit, 1),
        }

    def _list_images(self, where: list[str], values: list[object], limit: int, offset: int):
        where_sql = f"WHERE {' AND '.join(where)}" if where else ""
        with self._connect() as conn:
            total = conn.execute(f"SELECT COUNT(*) FROM imagenes i {where_sql}", values).fetchone()[0]
            rows = conn.execute(
                f"""
                SELECT i.*
                FROM imagenes i
                {where_sql}
                ORDER BY COALESCE(i.fecha_procesamiento, i.fecha_creacion) DESC, i.id DESC
                LIMIT ? OFFSET ?
                """,
                [*values, limit, offset],
            ).fetchall()
        return rows, total

    def _search_images(self, query: str, where: list[str], values: list[object], limit: int, offset: int):
        fts_query = _clean_fts_query(query)
        where_sql = f"AND {' AND '.join(where)}" if where else ""
        with self._connect() as conn:
            try:
                total = conn.execute(
                    f"""
                    SELECT COUNT(*)
                    FROM imagenes i
                    JOIN imagenes_fts f ON f.rowid = i.id
                    WHERE f MATCH ? {where_sql}
                    """,
                    [fts_query, *values],
                ).fetchone()[0]
                rows = conn.execute(
                    f"""
                    SELECT i.*
                    FROM imagenes i
                    JOIN imagenes_fts f ON f.rowid = i.id
                    WHERE f MATCH ? {where_sql}
                    ORDER BY rank
                    LIMIT ? OFFSET ?
                    """,
                    [fts_query, *values, limit, offset],
                ).fetchall()
                return rows, total
            except sqlite3.DatabaseError:
                like = f"%{query}%"
                like_where = [
                    "(i.nombre_original LIKE ? OR i.nombre_renombrado LIKE ? OR i.caption LIKE ? OR i.descripcion LIKE ? OR i.keywords LIKE ?)"
                ]
                like_values = [like, like, like, like, like, *values]
                if where:
                    like_where.extend(where)
                return self._list_images(like_where, like_values, limit, offset)

    def _api_image_detail(self, path: str) -> dict:
        image_id = self._path_id(path)
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM imagenes WHERE id = ?", (image_id,)).fetchone()
        if not row:
            return {"error": "Imagen no encontrada", "id": image_id}
        return {"item": self._row_to_detail(row)}

    def _serve_thumbnail(self, path: str, head_only: bool = False):
        image_id = self._path_id(path)
        with self._connect() as conn:
            row = conn.execute("SELECT thumbnail_webp FROM imagenes WHERE id = ?", (image_id,)).fetchone()
        if not row or not row["thumbnail_webp"]:
            self.send_error(HTTPStatus.NOT_FOUND, "Miniatura no disponible")
            return
        data = row["thumbnail_webp"]
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "image/webp")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "public, max-age=3600")
        self.end_headers()
        if not head_only:
            self.wfile.write(data)

    def _serve_media(self, path: str, head_only: bool = False):
        image_id = self._path_id(path)
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM imagenes WHERE id = ?", (image_id,)).fetchone()
        if not row:
            self.send_error(HTTPStatus.NOT_FOUND, "Imagen no encontrada")
            return
        file_path = _image_path(row)
        if not file_path:
            self.send_error(HTTPStatus.NOT_FOUND, "Archivo no disponible en disco")
            return
        data = file_path.read_bytes()
        content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "public, max-age=3600")
        self.end_headers()
        if not head_only:
            self.wfile.write(data)

    @staticmethod
    def _path_id(path: str) -> int:
        match = re.search(r"/(\d+)(?:/)?$", path)
        if not match:
            raise ValueError("ID no valido")
        return int(match.group(1))


class GalleryHTTPServer(ThreadingHTTPServer):
    def __init__(self, address, handler, db_path: Path):
        self.db_path = db_path
        super().__init__(address, handler)


def main() -> int:
    parser = argparse.ArgumentParser(description="StockPrep local web gallery")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Ruta a stockprep_images.db")
    parser.add_argument("--host", default="127.0.0.1", help="Host local")
    parser.add_argument("--port", default=8000, type=int, help="Puerto local")
    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.is_absolute():
        db_path = ROOT / db_path
    if not db_path.is_file():
        raise SystemExit(f"No existe la base de datos: {db_path}")

    server = GalleryHTTPServer((args.host, args.port), GalleryRequestHandler, db_path)
    url = f"http://{args.host}:{args.port}"
    print(f"StockPrep Web Gallery")
    print(f"BD: {db_path}")
    print(f"URL: {url}")
    print("Pulsa Ctrl+C para detener el servidor.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
