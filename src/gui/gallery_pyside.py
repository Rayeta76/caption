"""
Utilidades de galería PySide6: thumbnails, visor ampliado, navegación y zoom interactivo.
"""
from __future__ import annotations

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional

try:
    from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QMessageBox, QScrollArea, QWidget, QGridLayout, QFrame,
        QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    )
    from PySide6.QtCore import Qt, QThread, Signal
    from PySide6.QtGui import QPixmap, QImage, QCursor, QDesktopServices, QGuiApplication, QPainter, QColor
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
            self.records = records or []
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

    class ZoomableGraphicsView(QGraphicsView):
        """Vista interactiva con soporte para zoom por rueda del ratón y paneo arrastrando."""

        def __init__(self, parent=None):
            super().__init__(parent)
            self.scene = QGraphicsScene(self)
            self.setScene(self.scene)
            self.pixmap_item = QGraphicsPixmapItem()
            self.scene.addItem(self.pixmap_item)

            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
            self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.setBackgroundBrush(Qt.transparent)
            self.setFrameShape(QGraphicsView.NoFrame)
            self.setRenderHints(QPainter.SmoothPixmapTransform | QPainter.Antialiasing)

        def setPixmap(self, pixmap: QPixmap):
            self.pixmap_item.setPixmap(pixmap)
            self.scene.setSceneRect(self.pixmap_item.boundingRect())
            self.resetView()

        def wheelEvent(self, event):
            if not self.pixmap_item.pixmap().isNull():
                zoom_factor = 1.15 if event.angleDelta().y() > 0 else 0.85
                self.scale(zoom_factor, zoom_factor)
                event.accept()
            else:
                super().wheelEvent(event)

        def resetView(self):
            if not self.pixmap_item.pixmap().isNull():
                self.resetTransform()
                self.fitInView(self.pixmap_item, Qt.KeepAspectRatio)

        def mouseDoubleClickEvent(self, event):
            self.resetView()
            super().mouseDoubleClickEvent(event)

    class ImageViewerDialog(QDialog):
        """Visor de imagen a pantalla grande con navegación prev/next, zoom interactivo y copiado rápido."""

        def __init__(self, parent, records: List[Dict], start_index: int, db_path: str):
            super().__init__(parent)
            self.records = records or []
            self.db_path = db_path
            self.current_index = max(0, min(start_index, len(self.records) - 1))

            self.setWindowTitle("Visor de imagen")
            self.setMinimumSize(1100, 750)
            
            # Aplicar hoja de estilos estilo Windows 11 Fluent
            self.setStyleSheet("""
                QDialog {
                    background-color: #f3f3f3;
                    font-family: 'Segoe UI', sans-serif;
                }
                QFrame#infoPanel {
                    background-color: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 12px;
                }
                QFrame#cardFrame {
                    background-color: #fafafa;
                    border: 1px solid #e5e5e5;
                    border-radius: 8px;
                }
                QPushButton.fluent-action-btn {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 13px;
                }
                QPushButton.fluent-action-btn:hover {
                    background-color: #106ebe;
                }
                QPushButton.fluent-action-btn:pressed {
                    background-color: #005a9e;
                }
                QPushButton.fluent-secondary-btn {
                    background-color: #fdfdfd;
                    color: #333333;
                    border: 1px solid #d2d2d2;
                    padding: 6px 12px;
                    border-radius: 6px;
                    font-size: 12px;
                }
                QPushButton.fluent-secondary-btn:hover {
                    background-color: #f5f5f5;
                    border-color: #a6a6a6;
                }
                QPushButton.fluent-secondary-btn:pressed {
                    background-color: #e5e5e5;
                }
                QPushButton.fluent-copy-btn {
                    background-color: #f5f5f5;
                    color: #0078d4;
                    border: 1px solid #d2d2d2;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-weight: 600;
                    font-size: 11px;
                }
                QPushButton.fluent-copy-btn:hover {
                    background-color: #e0e9f5;
                    border-color: #0078d4;
                }
                QPushButton.fluent-copy-btn:pressed {
                    background-color: #c7def5;
                }
            """)

            # Layout horizontal principal para dividir Visor (izquierda) y Panel de Metadatos (derecha)
            main_layout = QHBoxLayout(self)
            main_layout.setContentsMargins(15, 15, 15, 15)
            main_layout.setSpacing(15)

            # Panel Izquierdo: Visor & Navegación
            left_layout = QVBoxLayout()
            left_layout.setSpacing(10)

            # Visor interactivo con soporte de Zoom & Drag
            self.zoomable_view = ZoomableGraphicsView(self)
            self.zoomable_view.setStyleSheet("border: 1px solid #cccccc; border-radius: 8px; background-color: #e8e8e8;")
            left_layout.addWidget(self.zoomable_view, stretch=1)

            # Controles de navegación
            nav = QHBoxLayout()
            self.btn_prev = QPushButton("◀ Anterior")
            self.btn_prev.setObjectName("btnPrev")
            self.btn_prev.setMinimumHeight(35)
            
            self.btn_reset_zoom = QPushButton("🔍 Reset Zoom")
            self.btn_reset_zoom.setMinimumHeight(35)
            self.btn_reset_zoom.clicked.connect(self.zoomable_view.resetView)
            
            self.btn_next = QPushButton("Siguiente ▶")
            self.btn_next.setObjectName("btnNext")
            self.btn_next.setMinimumHeight(35)
            
            self.counter_label = QLabel()
            self.counter_label.setStyleSheet("font-weight: bold; color: #555555;")
            
            self.btn_prev.clicked.connect(self.show_previous)
            self.btn_next.clicked.connect(self.show_next)
            
            nav.addWidget(self.btn_prev)
            nav.addWidget(self.btn_reset_zoom)
            nav.addWidget(self.counter_label, stretch=1, alignment=Qt.AlignCenter)
            nav.addWidget(self.btn_next)
            left_layout.addLayout(nav)
            
            main_layout.addLayout(left_layout, stretch=2)

            # Panel Derecho: Metadatos e Información (Contenedor QFrame con estilo)
            self.info_panel = QFrame()
            self.info_panel.setObjectName("infoPanel")
            self.info_panel.setFixedWidth(380)
            
            info_layout = QVBoxLayout(self.info_panel)
            info_layout.setContentsMargins(15, 15, 15, 15)
            info_layout.setSpacing(12)

            # Cabecera de información
            self.title_label = QLabel()
            self.title_label.setWordWrap(True)
            self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #1a1a1a; margin-bottom: 5px;")
            info_layout.addWidget(self.title_label)

            # 1. Card para Descripción (Caption)
            caption_card = QFrame()
            caption_card.setObjectName("cardFrame")
            caption_card_layout = QVBoxLayout(caption_card)
            caption_card_layout.setContentsMargins(10, 10, 10, 10)
            
            caption_header_layout = QHBoxLayout()
            caption_title = QLabel("📝 Descripción / Caption")
            caption_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #0078d4;")
            btn_copy_caption = QPushButton("Copiar")
            btn_copy_caption.setCursor(Qt.PointingHandCursor)
            btn_copy_caption.setProperty("class", "fluent-copy-btn")
            btn_copy_caption.setStyleSheet("max-width: 60px;")
            btn_copy_caption.clicked.connect(self.copy_caption)
            
            caption_header_layout.addWidget(caption_title)
            caption_header_layout.addStretch()
            caption_header_layout.addWidget(btn_copy_caption)
            caption_card_layout.addLayout(caption_header_layout)

            self.caption_content = QLabel()
            self.caption_content.setWordWrap(True)
            self.caption_content.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.caption_content.setStyleSheet("font-size: 12px; color: #333333; margin-top: 5px;")
            caption_card_layout.addWidget(self.caption_content)
            
            info_layout.addWidget(caption_card)

            # 2. Card para Palabras clave (Keywords)
            keywords_card = QFrame()
            keywords_card.setObjectName("cardFrame")
            keywords_card_layout = QVBoxLayout(keywords_card)
            keywords_card_layout.setContentsMargins(10, 10, 10, 10)

            keywords_header_layout = QHBoxLayout()
            keywords_title = QLabel("🏷️ Palabras Clave")
            keywords_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #0078d4;")
            btn_copy_keywords = QPushButton("Copiar")
            btn_copy_keywords.setCursor(Qt.PointingHandCursor)
            btn_copy_keywords.setProperty("class", "fluent-copy-btn")
            btn_copy_keywords.setStyleSheet("max-width: 60px;")
            btn_copy_keywords.clicked.connect(self.copy_keywords)

            keywords_header_layout.addWidget(keywords_title)
            keywords_header_layout.addStretch()
            keywords_header_layout.addWidget(btn_copy_keywords)
            keywords_card_layout.addLayout(keywords_header_layout)

            self.keywords_content = QLabel()
            self.keywords_content.setWordWrap(True)
            self.keywords_content.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.keywords_content.setStyleSheet("font-size: 12px; color: #333333; margin-top: 5px;")
            keywords_card_layout.addWidget(self.keywords_content)
            
            info_layout.addWidget(keywords_card)

            # 3. Card para Detalles y Ruta
            details_card = QFrame()
            details_card.setObjectName("cardFrame")
            details_card_layout = QVBoxLayout(details_card)
            details_card_layout.setContentsMargins(10, 10, 10, 10)
            
            details_title = QLabel("📂 Detalles de Archivo")
            details_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #0078d4; margin-bottom: 5px;")
            details_card_layout.addWidget(details_title)
            
            self.details_path = QLabel()
            self.details_path.setWordWrap(True)
            self.details_path.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.details_path.setStyleSheet("font-size: 11px; color: #555555;")
            details_card_layout.addWidget(self.details_path)
            
            info_layout.addWidget(details_card)

            # Relleno elástico
            info_layout.addStretch()

            # 4. Acciones rápidas premium
            btn_copy_all = QPushButton("📋 Copiar Todos los Metadatos")
            btn_copy_all.setCursor(Qt.PointingHandCursor)
            btn_copy_all.setProperty("class", "fluent-action-btn")
            btn_copy_all.setMinimumHeight(40)
            btn_copy_all.clicked.connect(self.copy_all_metadata)
            info_layout.addWidget(btn_copy_all)

            btn_open = QPushButton("💻 Abrir en el Sistema")
            btn_open.setCursor(Qt.PointingHandCursor)
            btn_open.setProperty("class", "fluent-secondary-btn")
            btn_open.clicked.connect(self.open_with_system)
            info_layout.addWidget(btn_open)

            btn_folder = QPushButton("📁 Abrir Carpeta Contenedora")
            btn_folder.setCursor(Qt.PointingHandCursor)
            btn_folder.setProperty("class", "fluent-secondary-btn")
            btn_folder.clicked.connect(self.open_folder)
            info_layout.addWidget(btn_folder)

            btn_copy_path = QPushButton("🔗 Copiar Ruta de Archivo")
            btn_copy_path.setCursor(Qt.PointingHandCursor)
            btn_copy_path.setProperty("class", "fluent-secondary-btn")
            btn_copy_path.clicked.connect(self.copy_path)
            info_layout.addWidget(btn_copy_path)

            btn_close = QPushButton("Cerrar")
            btn_close.setCursor(Qt.PointingHandCursor)
            btn_close.clicked.connect(self.close)
            btn_close.setMinimumHeight(35)
            btn_close.setStyleSheet("background-color: #e1dfdd; color: #323130; border: none; border-radius: 6px; font-weight: bold;")
            info_layout.addWidget(btn_close)

            main_layout.addWidget(self.info_panel)

            if self.records:
                self.refresh_view()
            else:
                self.title_label.setText("Sin datos de imágenes.")

        def refresh_view(self):
            record = self.records[self.current_index]
            record_id = record.get("id", "?")
            self.setWindowTitle(f"Visor de imagen - ID {record_id}")

            pixmap = load_full_pixmap_for_record(self.db_path, record, max_size=1200)
            if pixmap and not pixmap.isNull():
                self.zoomable_view.setPixmap(pixmap)
            else:
                # Mostrar un marcador de posición si falla la carga
                placeholder = QPixmap(800, 600)
                placeholder.fill(QColor("#e8e8e8"))
                self.zoomable_view.setPixmap(placeholder)

            self.title_label.setText(record_display_name(record))

            caption = record.get("caption") or record.get("descripcion") or "Sin caption"
            self.caption_content.setText(caption)

            keywords = record.get("keywords", [])
            kw_str = ", ".join(keywords) if isinstance(keywords, list) else str(keywords)
            self.keywords_content.setText(kw_str or "—")

            path = record_image_path(record) or "N/A"
            self.details_path.setText(path)

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
                QMessageBox.warning(self, "Archivo no encontrado", "La ruta no existe en el disco.")

        def open_folder(self):
            p = self._current_path()
            if p and p.parent.exists():
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(p.parent.resolve())))
            else:
                QMessageBox.warning(self, "Carpeta no encontrada", "El directorio no existe en el disco.")

        def copy_path(self):
            p = self._current_path()
            if p:
                QGuiApplication.clipboard().setText(str(p.resolve()))
                QMessageBox.information(self, "Copiado", "Ruta de archivo copiada al portapapeles.")

        def copy_caption(self):
            record = self.records[self.current_index]
            caption = record.get("caption") or record.get("descripcion") or ""
            if caption:
                QGuiApplication.clipboard().setText(caption)
                QMessageBox.information(self, "Copiado", "Descripción (caption) copiada al portapapeles.")
            else:
                QMessageBox.warning(self, "Error", "No hay descripción disponible para copiar.")

        def copy_keywords(self):
            record = self.records[self.current_index]
            keywords = record.get("keywords", [])
            kw_str = ", ".join(keywords) if isinstance(keywords, list) else str(keywords)
            if kw_str and kw_str != "[]" and kw_str != "None":
                QGuiApplication.clipboard().setText(kw_str)
                QMessageBox.information(self, "Copiado", "Palabras clave copiadas al portapapeles.")
            else:
                QMessageBox.warning(self, "Error", "No hay palabras clave disponibles para copiar.")

        def copy_all_metadata(self):
            record = self.records[self.current_index]
            caption = record.get("caption") or record.get("descripcion") or ""
            keywords = record.get("keywords", [])
            kw_str = ", ".join(keywords) if isinstance(keywords, list) else str(keywords)
            
            metadata_text = f"Descripción: {caption}\nPalabras clave: {kw_str}"
            QGuiApplication.clipboard().setText(metadata_text)
            QMessageBox.information(self, "Copiado", "Todos los metadatos copiados al portapapeles.")

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
