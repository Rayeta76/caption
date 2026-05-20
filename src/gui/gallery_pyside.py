"""
Utilidades de galería PySide6: thumbnails, visor ampliado y navegación.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

try:
    from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QMessageBox, QScrollArea, QWidget, QGridLayout, QFrame,
    )
    from PySide6.QtCore import Qt, QThread, Signal
    from PySide6.QtGui import QPixmap, QImage, QCursor, QDesktopServices, QGuiApplication
    from PySide6.QtCore import QUrl
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False


def record_display_name(record: Dict) -> str:
    name = record.get("nombre_renombrado") or record.get("nombre_original")
    if name:
        return str(name)
    path = record_image_path(record)
    return Path(path).name if path else f"ID {record.get('id', '?')}"


def record_image_path(record: Dict) -> Optional[str]:
    for key in ("ruta_salida", "file_path", "ruta_completa"):
        value = record.get(key)
        if value:
            return str(value)
    return None


def fetch_thumbnail_webp_bytes(db_path: str, imagen_id: int) -> Optional[bytes]:
    if not db_path or not imagen_id:
        return None
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT thumbnail_webp FROM imagenes WHERE id = ?",
                (imagen_id,),
            )
            row = cursor.fetchone()
            return row[0] if row and row[0] else None
    except sqlite3.OperationalError:
        return None


def pixmap_from_webp_bytes(data: bytes) -> Optional["QPixmap"]:
    if not PYSIDE6_AVAILABLE or not data:
        return None
    image = QImage.fromData(data)
    if image.isNull():
        return None
    return QPixmap.fromImage(image)


def load_pixmap_for_record(
    db_path: str,
    record: Dict,
    max_size: int = 200,
) -> Optional["QPixmap"]:
    if not PYSIDE6_AVAILABLE:
        return None

    imagen_id = record.get("id")
    if imagen_id:
        webp = fetch_thumbnail_webp_bytes(db_path, imagen_id)
        if webp:
            pixmap = pixmap_from_webp_bytes(webp)
            if pixmap and not pixmap.isNull():
                return pixmap.scaled(
                    max_size,
                    max_size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )

    path_str = record_image_path(record)
    if path_str and Path(path_str).exists():
        pixmap = QPixmap(path_str)
        if not pixmap.isNull():
            return pixmap.scaled(
                max_size,
                max_size,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
    return None


def load_full_pixmap_for_record(db_path: str, record: Dict, max_size: int = 1200) -> Optional["QPixmap"]:
    path_str = record_image_path(record)
    if path_str and Path(path_str).exists():
        pixmap = QPixmap(path_str)
        if not pixmap.isNull():
            if max(pixmap.width(), pixmap.height()) > max_size:
                return pixmap.scaled(
                    max_size,
                    max_size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            return pixmap

    imagen_id = record.get("id")
    if imagen_id:
        webp = fetch_thumbnail_webp_bytes(db_path, imagen_id)
        if webp:
            pixmap = pixmap_from_webp_bytes(webp)
            if pixmap and not pixmap.isNull():
                return pixmap.scaled(
                    max_size,
                    max_size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
    return None


if PYSIDE6_AVAILABLE:

    class ThumbnailLoaderThread(QThread):
        thumbnail_loaded = Signal(object, str, dict)  # QPixmap, display_name, record
        finished = Signal()

        def __init__(self, records: List[Dict], db_path: str):
            super().__init__()
            self.records = records
            self.db_path = db_path
            self.is_running = True

        def run(self):
            for record in self.records:
                if not self.is_running:
                    break
                pixmap = load_pixmap_for_record(self.db_path, record, max_size=200)
                if pixmap and not pixmap.isNull():
                    self.thumbnail_loaded.emit(
                        pixmap,
                        record_display_name(record),
                        record,
                    )
            self.finished.emit()

        def stop(self):
            self.is_running = False

    class ThumbnailWidget(QFrame):
        clicked = Signal(dict)

        def __init__(self, pixmap, display_name: str, record: Dict, parent=None):
            super().__init__(parent)
            self.record = record
            self.setFrameShape(QFrame.Box)
            self.setLineWidth(1)
            self.setCursor(QCursor(Qt.PointingHandCursor))
            self.setFixedWidth(220)

            layout = QVBoxLayout(self)
            img_label = QLabel()
            img_label.setPixmap(pixmap)
            img_label.setAlignment(Qt.AlignCenter)
            img_label.setMinimumHeight(180)

            name_label = QLabel(display_name)
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setWordWrap(True)
            name_label.setMaximumWidth(210)

            layout.addWidget(img_label)
            layout.addWidget(name_label)

        def mousePressEvent(self, event):
            if event.button() == Qt.LeftButton:
                self.clicked.emit(self.record)
            super().mousePressEvent(event)

    class ImageViewerDialog(QDialog):
        """Visor de imagen a pantalla grande con navegación prev/next."""

        def __init__(self, parent, records: List[Dict], start_index: int, db_path: str):
            super().__init__(parent)
            self.records = records or []
            self.db_path = db_path
            self.current_index = max(0, min(start_index, len(self.records) - 1))

            self.setWindowTitle("Visor de imagen")
            self.setMinimumSize(900, 750)
            try:
                from PySide6.QtGui import QIcon
                self.setWindowIcon(QIcon("stockprep_icon.png"))
            except Exception:
                pass

            layout = QVBoxLayout(self)

            self.image_label = QLabel()
            self.image_label.setAlignment(Qt.AlignCenter)
            self.image_label.setMinimumHeight(500)
            layout.addWidget(self.image_label, stretch=1)

            self.info_label = QLabel()
            self.info_label.setWordWrap(True)
            self.info_label.setStyleSheet(
                "QLabel { background-color: #f0f0f0; padding: 10px; border-radius: 5px; }"
            )
            layout.addWidget(self.info_label)

            nav = QHBoxLayout()
            self.btn_prev = QPushButton("◀ Anterior")
            self.btn_next = QPushButton("Siguiente ▶")
            self.counter_label = QLabel()
            self.btn_prev.clicked.connect(self.show_previous)
            self.btn_next.clicked.connect(self.show_next)
            nav.addWidget(self.btn_prev)
            nav.addWidget(self.counter_label, stretch=1, alignment=Qt.AlignCenter)
            nav.addWidget(self.btn_next)
            layout.addLayout(nav)

            actions = QHBoxLayout()
            btn_open = QPushButton("Abrir con visor del sistema")
            btn_folder = QPushButton("Abrir carpeta")
            btn_copy = QPushButton("Copiar ruta")
            btn_close = QPushButton("Cerrar")
            btn_open.clicked.connect(self.open_with_system)
            btn_folder.clicked.connect(self.open_folder)
            btn_copy.clicked.connect(self.copy_path)
            btn_close.clicked.connect(self.close)
            actions.addWidget(btn_open)
            actions.addWidget(btn_folder)
            actions.addWidget(btn_copy)
            actions.addStretch()
            actions.addWidget(btn_close)
            layout.addLayout(actions)

            if self.records:
                self.refresh_view()
            else:
                self.image_label.setText("No hay imágenes para mostrar.")

        def refresh_view(self):
            record = self.records[self.current_index]
            record_id = record.get("id", "?")
            self.setWindowTitle(f"Visor de imagen - ID {record_id}")

            pixmap = load_full_pixmap_for_record(self.db_path, record, max_size=1100)
            if pixmap and not pixmap.isNull():
                self.image_label.setPixmap(pixmap)
                self.image_label.setText("")
            else:
                self.image_label.setPixmap(QPixmap())
                self.image_label.setText(
                    "No se pudo cargar la imagen.\n"
                    "Comprueba que el archivo existe o ejecuta la migración de thumbnails."
                )

            caption = record.get("caption") or record.get("descripcion") or "Sin caption"
            keywords = record.get("keywords", [])
            kw_str = ", ".join(keywords) if isinstance(keywords, list) else str(keywords)
            path = record_image_path(record) or "N/A"
            self.info_label.setText(
                f"<b>Archivo:</b> {record_display_name(record)}<br>"
                f"<b>Caption:</b> {caption}<br>"
                f"<b>Keywords:</b> {kw_str or '—'}<br>"
                f"<b>Ruta:</b> {path}"
            )
            self.counter_label.setText(
                f"{self.current_index + 1} / {len(self.records)}"
            )
            self.btn_prev.setEnabled(self.current_index > 0)
            self.btn_next.setEnabled(self.current_index < len(self.records) - 1)

        def show_previous(self):
            if self.current_index > 0:
                self.current_index -= 1
                self.refresh_view()

        def show_next(self):
            if self.current_index < len(self.records) - 1:
                self.current_index += 1
                self.refresh_view()

        def _current_path(self) -> Optional[Path]:
            path = record_image_path(self.records[self.current_index])
            return Path(path) if path else None

        def open_with_system(self):
            p = self._current_path()
            if p and p.exists():
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(p.resolve())))
            else:
                QMessageBox.warning(self, "Archivo no encontrado", "La ruta no existe en disco.")

        def open_folder(self):
            p = self._current_path()
            if p and p.parent.exists():
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(p.parent.resolve())))

        def copy_path(self):
            p = self._current_path()
            if p:
                QGuiApplication.clipboard().setText(str(p.resolve()))
                QMessageBox.information(self, "Copiado", "Ruta copiada al portapapeles.")

    def open_image_viewer(parent, records: List[Dict], record: Dict, db_path: str):
        if not records:
            records = [record]
        try:
            index = next(i for i, r in enumerate(records) if r.get("id") == record.get("id"))
        except StopIteration:
            index = 0
            records = [record] + records
        dialog = ImageViewerDialog(parent, records, index, db_path)
        dialog.exec()

    def populate_thumbnail_grid(
        layout: QGridLayout,
        records: List[Dict],
        db_path: str,
        on_click,
        col_count: int = 5,
        thread_holder: Optional[dict] = None,
    ):
        """Llena un QGridLayout con thumbnails en segundo plano."""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not records:
            placeholder = QLabel("No hay resultados para mostrar.")
            placeholder.setAlignment(Qt.AlignCenter)
            layout.addWidget(placeholder, 0, 0, 1, col_count)
            return

        state = {"count": 0, "col_count": col_count}

        def on_loaded(pixmap, display_name, record):
            row = state["count"] // state["col_count"]
            col = state["count"] % state["col_count"]
            widget = ThumbnailWidget(pixmap, display_name, record)
            widget.clicked.connect(on_click)
            layout.addWidget(widget, row, col)
            state["count"] += 1

        thread = ThumbnailLoaderThread(records, db_path)
        thread.thumbnail_loaded.connect(on_loaded)
        if thread_holder is not None:
            old = thread_holder.get("thread")
            if old and old.isRunning():
                old.stop()
                old.wait(2000)
            thread_holder["thread"] = thread
        thread.start()
