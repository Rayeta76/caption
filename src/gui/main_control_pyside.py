"""
Centro de Control Principal de StockPrep Pro v2.0 - Versión PySide6
"""
import sys
from pathlib import Path

try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
    from PySide6.QtCore import Qt, QSize
    from PySide6.QtGui import QFont, QIcon
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    
# Añadir ruta para importar módulos locales
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Importar las ventanas secundarias
if PYSIDE6_AVAILABLE:
    from gui.modern_gui_win11 import StockPrepWin11App
    from gui.database_gui_pyside import DatabaseManagerAppPyside

class MainControlPyside(QMainWindow):
    """Ventana principal que actúa como centro de control."""
    def __init__(self):
        super().__init__()
        self.image_processor_window = None
        self.db_manager_window = None
        
        self.setWindowTitle("StockPrep Pro v2.0 - Centro de Control")
        self.setMinimumSize(400, 250)
        
        # Icono de la aplicación
        try:
            self.setWindowIcon(QIcon("stockprep_icon.png"))
        except:
            pass

        # Widget central y layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignCenter)
        
        # Título
        title_label = QLabel("StockPrep Pro v2.0")
        title_font = QFont("Segoe UI", 24, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        
        # Subtítulo
        subtitle_label = QLabel("Seleccione un módulo para iniciar")
        subtitle_font = QFont("Segoe UI", 12)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        # Layout de botones
        button_layout = QHBoxLayout()
        
        # Botones
        self.btn_processor = QPushButton("🖼️ Procesador de Imágenes")
        self.btn_db_manager = QPushButton("🗄️ Gestor de Base de Datos")
        
        for btn in [self.btn_processor, self.btn_db_manager]:
            btn.setMinimumHeight(60)
            btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        
        button_layout.addWidget(self.btn_processor)
        button_layout.addWidget(self.btn_db_manager)
        
        # Añadir widgets al layout principal
        main_layout.addWidget(title_label)
        main_layout.addWidget(subtitle_label)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)
        main_layout.addStretch()
        
        # Conectar señales
        self.btn_processor.clicked.connect(self.launch_image_processor)
        self.btn_db_manager.clicked.connect(self.launch_db_manager)

    def launch_image_processor(self):
        """Lanza la ventana del procesador de imágenes."""
        if not self.image_processor_window:
            self.image_processor_window = StockPrepWin11App()
            # Cuando se cierre, eliminamos la referencia
            self.image_processor_window.setAttribute(Qt.WA_DeleteOnClose)
            self.image_processor_window.destroyed.connect(lambda: setattr(self, 'image_processor_window', None))
        
        self.image_processor_window.show()
        self.image_processor_window.activateWindow()

    def launch_db_manager(self):
        """Lanza la ventana del gestor de base de datos."""
        if not self.db_manager_window:
            self.db_manager_window = DatabaseManagerAppPyside()
            self.db_manager_window.setAttribute(Qt.WA_DeleteOnClose)
            self.db_manager_window.destroyed.connect(lambda: setattr(self, 'db_manager_window', None))
        
        self.db_manager_window.show()
        self.db_manager_window.activateWindow()


def start_pyside_app():
    if not PYSIDE6_AVAILABLE:
        print("ERROR: PySide6 no está instalado. No se puede ejecutar la aplicación.")
        return

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
        
    main_control = MainControlPyside()
    main_control.show()
    
    # No llamar a sys.exit(app.exec()) aquí para permitir que las ventanas secundarias funcionen
    app.exec()

if __name__ == '__main__':
    start_pyside_app() 