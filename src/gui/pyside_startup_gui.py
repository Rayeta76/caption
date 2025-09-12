"""PySide6-based startup window for StockPrep Pro."""

from __future__ import annotations

import sys
import threading
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QMessageBox,
    QStatusBar,
)
from PySide6.QtCore import Qt

from gui.components.styles import get_win11_style
from gui.components.stats_widget import ModernStatsWidget
from gui.components.threads import ModelLoadingThread

from core.enhanced_database_manager import EnhancedDatabaseManager
from core.model_manager import Florence2Manager


class StockPrepStartupWindow(QMainWindow):
    """Main startup window using PySide6."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("StockPrep Pro v2.0 - Inicio")
        self.setGeometry(100, 100, 600, 400)

        # Core managers
        self.db_manager = EnhancedDatabaseManager("stockprep_images.db")
        self.model_manager = Florence2Manager()
        self.model_thread: ModelLoadingThread | None = None
        self.recognition_window = None

        self.init_ui()
        self.apply_style()
        self.update_stats()

    # ------------------------------------------------------------------
    # UI setup
    # ------------------------------------------------------------------
    def init_ui(self) -> None:
        central = QWidget()
        layout = QVBoxLayout()
        central.setLayout(layout)
        self.setCentralWidget(central)

        title = QLabel("StockPrep Pro v2.0")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:24px;font-weight:bold;")
        layout.addWidget(title)

        self.stats_widget = ModernStatsWidget()
        layout.addWidget(self.stats_widget)

        self.recognition_btn = QPushButton("Abrir Reconocimiento de Imágenes")
        self.recognition_btn.clicked.connect(self.open_recognition_module)
        layout.addWidget(self.recognition_btn)

        db_btn = QPushButton("Gestión de Base de Datos")
        db_btn.clicked.connect(self.open_database_module)
        layout.addWidget(db_btn)

        stats_btn = QPushButton("Estadísticas Rápidas")
        stats_btn.clicked.connect(self.show_quick_stats)
        layout.addWidget(stats_btn)

        exit_btn = QPushButton("Salir")
        exit_btn.clicked.connect(self.close)
        layout.addWidget(exit_btn)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

    def apply_style(self) -> None:
        """Applies Win11 style from components."""
        self.setStyleSheet(get_win11_style())

    # ------------------------------------------------------------------
    # Stats handling
    # ------------------------------------------------------------------
    def update_stats(self) -> None:
        try:
            stats = self.db_manager.obtener_estadisticas()
            mapped = {
                "total_images": stats.get("imagenes_procesadas", 0),
                "db_records": stats.get("total_imagenes", 0),
                "db_size": stats.get("tamano", {}).get("total_bytes", 0) // 1024,
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            self.stats_widget.update_stats(mapped)
        except Exception as e:  # pragma: no cover - avoid failing on stats
            self.status.showMessage(f"Error estadísticas: {e}")

    def show_quick_stats(self) -> None:
        try:
            stats = self.db_manager.obtener_estadisticas()
            msg = (
                "📊 Estadísticas del Sistema\n\n"
                f"🖼️ Imágenes totales: {stats.get('total_imagenes', 0)}\n"
                f"✅ Procesadas: {stats.get('imagenes_procesadas', 0)}\n"
                f"⏳ Pendientes: {stats.get('imagenes_pendientes', 0)}\n"
                f"❌ Errores: {stats.get('imagenes_error', 0)}\n\n"
                f"💾 Base de datos: {Path(self.db_manager.db_path).name}\n"
                f"📅 Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            QMessageBox.information(self, "Estadísticas Rápidas", msg)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error obteniendo estadísticas: {e}")

    # ------------------------------------------------------------------
    # Module launchers
    # ------------------------------------------------------------------
    def open_recognition_module(self) -> None:
        """Loads model in a separate thread and opens recognition window."""
        self.status.showMessage("Cargando modelo...")
        self.recognition_btn.setEnabled(False)

        self.model_thread = ModelLoadingThread(self.model_manager)
        self.model_thread.progress.connect(self.status.showMessage)
        self.model_thread.error.connect(self.on_model_error)
        self.model_thread.finished.connect(self.on_model_loaded)
        self.model_thread.start()

    def on_model_error(self, message: str) -> None:
        QMessageBox.critical(self, "Error", message)
        self.recognition_btn.setEnabled(True)
        self.status.clearMessage()

    def on_model_loaded(self, success: bool) -> None:
        if not success:
            QMessageBox.critical(self, "Error", "No se pudo cargar el modelo")
            self.recognition_btn.setEnabled(True)
            self.status.clearMessage()
            return

        from gui.modern_gui_win11 import StockPrepWin11App

        self.recognition_window = StockPrepWin11App(
            model_manager=self.model_manager,
            db_manager=self.db_manager,
        )
        self.recognition_window.destroyed.connect(self.on_recognition_closed)
        self.recognition_window.show()
        self.hide()
        self.status.clearMessage()
        self.recognition_btn.setEnabled(True)

    def on_recognition_closed(self) -> None:
        self.show()
        self.update_stats()
        self.status.showMessage("Módulo de reconocimiento cerrado", 5000)

    def open_database_module(self) -> None:
        """Opens the Tkinter-based database manager."""
        self.status.showMessage("Iniciando módulo de base de datos...")
        self.hide()

        def run_db():
            from gui.database_gui import DatabaseManagerApp

            app = DatabaseManagerApp(self.db_manager)
            app.run()

            # When database window closes, restore startup window
            self.update_stats()
            self.status.showMessage("Módulo de base de datos cerrado", 5000)
            self.show()

        threading.Thread(target=run_db, daemon=True).start()


def main() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    window = StockPrepStartupWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
