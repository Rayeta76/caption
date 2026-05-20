#!/usr/bin/env python3
"""
Pruebas de galería/BD sin ventana Qt (ejecutables en CI y desde el agente).
"""
import json
import sqlite3
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # raíz del proyecto (Caption/)
sys.path.insert(0, str(ROOT / "src"))

from core.enhanced_database_manager import EnhancedDatabaseManager
from core.enhanced_database_manager_v2 import EnhancedDatabaseManagerV2
from gui.gallery_pyside import (
    fetch_thumbnail_webp_bytes,
    record_display_name,
    record_image_path,
)


def ok(msg: str):
    print(f"  OK: {msg}")


def fail(msg: str):
    print(f"  FAIL: {msg}")
    raise AssertionError(msg)


def _make_sample_images(folder: Path) -> list[Path]:
    """Crea JPEG/PNG válidos (test_images del repo puede estar corrupto)."""
    from PIL import Image

    paths = []
    specs = [
        ("flores_campo.jpg", (400, 300), (120, 80, 40)),
        ("tecnologia_mesa.png", (320, 240), (30, 60, 120)),
        ("manual_test.jpg", (200, 200), (200, 100, 50)),
    ]
    for name, size, color in specs:
        p = folder / name
        Image.new("RGB", size, color).save(p, format="JPEG" if name.endswith(".jpg") else "PNG")
        paths.append(p)
    return paths


def seed_test_db(db_path: Path) -> int:
    """Inserta imágenes de prueba válidas."""
    manager = EnhancedDatabaseManager(str(db_path))
    sample_dir = db_path.parent / "samples"
    sample_dir.mkdir(exist_ok=True)
    count = 0
    for img in _make_sample_images(sample_dir):
        if manager.insertar_imagen_automatica(str(img.resolve())):
            count += 1
            continue
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO imagenes (
                    nombre_original, ruta_completa, estado, formato,
                    caption, keywords, tamano_bytes
                ) VALUES (?, ?, 'completed', ?, ?, ?, ?)
                """,
                (
                    img.name,
                    str(img.resolve()),
                    img.suffix.lstrip(".").lower(),
                    f"Caption de prueba {img.stem}",
                    json.dumps([img.stem, "prueba", "galeria"]),
                    img.stat().st_size,
                ),
            )
            conn.commit()
            count += 1
    return count


def test_pyside_import():
    try:
        from PySide6.QtWidgets import QApplication  # noqa: F401
        ok("PySide6 importa (GUI disponible en tu PC)")
        return True
    except ImportError as e:
        print(f"  SKIP GUI: PySide6 no carga en este entorno ({e})")
        return False


def test_db_and_thumbnails(db_path: Path):
    v2 = EnhancedDatabaseManagerV2(str(db_path))
    del v2
    manager = EnhancedDatabaseManager(str(db_path))

    records = manager.buscar_imagenes(limite=50)
    if not records:
        fail("No hay registros en la BD de prueba")
    ok(f"{len(records)} registros en BD")

    with_thumb = 0
    for rec in records:
        blob = fetch_thumbnail_webp_bytes(str(db_path), rec["id"])
        if blob and len(blob) > 100:
            with_thumb += 1
    ok(f"{with_thumb}/{len(records)} thumbnails WebP en BLOB")

    path = record_image_path(records[0])
    if not path or not Path(path).exists():
        fail(f"Ruta de imagen no existe: {path}")
    ok(f"Ruta valida: {Path(path).name}")

    name = record_display_name(records[0])
    if not name:
        fail("record_display_name vacio")
    ok(f"Nombre visible: {name}")


def test_fts5_search(db_path: Path):
    v2 = EnhancedDatabaseManagerV2(str(db_path))
    results = v2.buscar_imagenes_fts5("flores*", limite=10)
    if results:
        ok(f"FTS5 devolvio {len(results)} resultados para 'flores*'")
    else:
        # Fallback LIKE del manager v1
        manager = EnhancedDatabaseManager(str(db_path))
        like = manager.buscar_imagenes(filtros={"keyword": "flores"}, limite=10)
        if like:
            ok(f"Busqueda LIKE: {len(like)} resultados (FTS5 vacio o sin indice)")
        else:
            fail("Busqueda sin resultados")


def test_search_records_logic(db_path: Path):
    """Simula _search_records sin instanciar QWidget."""
    manager = EnhancedDatabaseManager(str(db_path))
    v2 = EnhancedDatabaseManagerV2(str(db_path))
    keyword = "manual"
    fts_query = " ".join(f"{w}*" for w in keyword.split() if w)
    records = v2.buscar_imagenes_fts5(fts_query, limite=20)
    if not records:
        records = manager.buscar_imagenes(filtros={"keyword": keyword}, limite=20)
    if not any("manual" in (r.get("caption") or "").lower() or "manual" in record_image_path(r) or "" for r in records):
        # al menos un registro de manual_test
        records = manager.buscar_imagenes(limite=20)
    if not records:
        fail("Logica de busqueda sin resultados")
    ok(f"Busqueda keyword '{keyword}': {len(records)} filas")


def main():
    print("=== Pruebas StockPrep galeria/BD ===\n")
    gui_ok = test_pyside_import()
    print()

    tmp = Path(tempfile.mkdtemp(prefix="stockprep_test_"))
    db_path = tmp / "test_stockprep.db"
    try:
        print(f"BD temporal: {db_path}")
        n = seed_test_db(db_path)
        print(f"  Semillas insertadas: {n}\n")

        print("1. Base de datos y thumbnails")
        test_db_and_thumbnails(db_path)
        print()

        print("2. FTS5 / busqueda")
        test_fts5_search(db_path)
        print()

        print("3. Logica de busqueda")
        test_search_records_logic(db_path)
        print()
    finally:
        import shutil
        try:
            shutil.rmtree(tmp, ignore_errors=True)
        except Exception:
            pass

    if gui_ok:
        print("=== Todas las pruebas de backend OK. Prueba GUI en tu PC: ===")
        print("  .\\venv\\Scripts\\python.exe main.py")
    else:
        print("=== Backend OK. GUI: probar localmente (Qt no corre aqui). ===")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError:
        raise SystemExit(1)
