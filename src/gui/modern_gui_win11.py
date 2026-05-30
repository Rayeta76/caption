"""
Interfaz gráfica moderna estilo Windows 11 para StockPrep Pro
Usa PySide6 para una experiencia nativa y moderna
"""
import sys
import os
from pathlib import Path
from typing import Optional, Dict, List
import logging
import threading
from datetime import datetime

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QTextEdit, QFileDialog, QProgressBar,
        QTabWidget, QGroupBox, QGridLayout, QScrollArea, QFrame,
        QMessageBox, QStatusBar, QMenuBar, QMenu, QSplitter,
        QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem,
        QCheckBox, QButtonGroup, QRadioButton, QComboBox
    )
    from PySide6.QtCore import Qt, QThread, Signal, QTimer, QSize
    from PySide6.QtGui import (
        QPixmap, QFont, QIcon, QPalette, QColor, QAction,
        QPainter, QBrush, QLinearGradient
    )
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False

if PYSIDE6_AVAILABLE:
    # Importar módulos del core
    # Agregar el directorio padre al path para importaciones
    current_dir = Path(__file__).parent.parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    from core.qwen_manager import Qwen2VLManager
    from core.image_processor import ImageProcessor
    from core.model_registry import (
        find_model_profile,
        find_processing_mode,
        get_default_model_id,
        get_default_mode_id,
        get_model_profiles,
        get_processing_modes,
    )
    try:
        from core.enhanced_database_manager_v2 import EnhancedDatabaseManagerV2 as EnhancedDatabaseManager
    except ImportError:
        from core.enhanced_database_manager import EnhancedDatabaseManager
    from output.output_handler_v2 import OutputHandlerV2
    from utils.keyword_extractor import KeywordExtractor

    logger = logging.getLogger(__name__)

    class ModelLoadingThread(QThread):
        """Hilo para cargar el modelo sin bloquear la UI"""
        finished = Signal(bool)
        error = Signal(str)
        progress = Signal(str)
        
        def __init__(self, model_manager):
            super().__init__()
            self.model_manager = model_manager
        
        def run(self):
            """Ejecuta la carga del modelo"""
            try:
                def callback(mensaje):
                    self.progress.emit(mensaje)
                
                model_name = getattr(self.model_manager, "display_name", "modelo IA")
                self.progress.emit(f"🚀 Iniciando carga de {model_name}...")
                success = self.model_manager.cargar_modelo(callback)
                self.finished.emit(success)
                
            except Exception as e:
                logger.error(f"Error cargando modelo: {e}")
                self.error.emit(str(e))

    class ProcessingThread(QThread):
        """Hilo para procesar imágenes sin bloquear la UI"""
        finished = Signal(dict)
        error = Signal(str)
        progress = Signal(int)
        
        def __init__(
            self,
            image_path: str,
            processor,
            detail_level: str = "largo",
            custom_prompt: str = None,
            model_profile_id: str = None,
            processing_mode_id: str = None,
            verify_attributes: bool = True,
        ):
            super().__init__()
            self.image_path = image_path
            self.processor = processor
            self.detail_level = detail_level
            self.custom_prompt = custom_prompt
            self.model_profile_id = model_profile_id
            self.processing_mode_id = processing_mode_id
            self.verify_attributes = verify_attributes
        
        def run(self):
            """Ejecuta el procesamiento de imagen"""
            try:
                self.progress.emit(10)
                
                # Procesar imagen con nivel de detalle específico y prompt personalizado
                results = self.processor.process_image(
                    self.image_path,
                    self.detail_level,
                    self.custom_prompt,
                    verify_attributes=self.verify_attributes,
                )
                if isinstance(results, dict):
                    results["model_profile_id"] = self.model_profile_id
                    results["processing_mode_id"] = self.processing_mode_id
                
                self.progress.emit(100)
                self.finished.emit(results)
                
            except Exception as e:
                logger.error(f"Error procesando imagen: {e}")
                self.error.emit(str(e))

    class ModernStatsWidget(QWidget):
        """Widget moderno para mostrar estadísticas"""
        
        def __init__(self):
            super().__init__()
            self.init_ui()
        
        def init_ui(self):
            layout = QGridLayout()
            
            # Estilo moderno
            self.setStyleSheet("""
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #E0E0E0;
                    border-radius: 8px;
                    margin-top: 1ex;
                    padding: 10px;
                    background-color: #FAFAFA;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: #2B579A;
                }
                QLabel {
                    color: #333333;
                    font-size: 14px;
                }
            """)
            
            # Estadísticas de procesamiento
            processing_group = QGroupBox("📊 Estadísticas de Procesamiento")
            processing_layout = QVBoxLayout()
            
            self.total_images_label = QLabel("Imágenes procesadas: 0")
            self.success_rate_label = QLabel("Tasa de éxito: 100%")
            self.avg_time_label = QLabel("Tiempo promedio: 0s")
            
            processing_layout.addWidget(self.total_images_label)
            processing_layout.addWidget(self.success_rate_label)
            processing_layout.addWidget(self.avg_time_label)
            processing_group.setLayout(processing_layout)
            
            # Estadísticas de base de datos
            db_group = QGroupBox("🗄️ Base de Datos")
            db_layout = QVBoxLayout()
            
            self.db_records_label = QLabel("Registros: 0")
            self.db_size_label = QLabel("Tamaño: 0 KB")
            self.last_update_label = QLabel("Última actualización: Nunca")
            
            db_layout.addWidget(self.db_records_label)
            db_layout.addWidget(self.db_size_label)
            db_layout.addWidget(self.last_update_label)
            db_group.setLayout(db_layout)
            
            layout.addWidget(processing_group, 0, 0)
            layout.addWidget(db_group, 0, 1)
            
            self.setLayout(layout)
        
        def update_stats(self, stats: Dict):
            """Actualiza las estadísticas mostradas"""
            if 'total_imagenes' in stats:
                self.total_images_label.setText(f"Imágenes procesadas: {stats['total_imagenes']}")
            if 'total_imagenes' in stats:
                self.db_records_label.setText(f"Registros: {stats['total_imagenes']}")
            if 'tamano' in stats:
                size_kb = stats['tamano'].get('total_bytes', 0) / 1024
                self.db_size_label.setText(f"Tamaño: {size_kb:.0f} KB")
            if 'last_update' in stats:
                self.last_update_label.setText(f"Última actualización: {stats['last_update']}")

    class StockPrepWin11App(QMainWindow):
        """Aplicación principal con interfaz Windows 11"""
        
        def __init__(self):
            super().__init__()
            self.current_image_path = None
            self.processing_thread = None
            self.model_loading_thread = None
            self.model_loaded = False
            
            # Variables para procesamiento en lote
            self.current_folder_path = None
            self.batch_images = []
            self.batch_processing = False
            self.batch_current_index = 0
            
            # Variables para carpeta de salida
            self.output_directory = None
            self.copy_and_rename = True
            self.embed_metadata = True
            
            # Variable para nivel de detalle de descripción
            self.detail_level = "largo"
            self.model_profiles = get_model_profiles()
            self.processing_modes = get_processing_modes()
            self.selected_model_profile_id = get_default_model_id()
            self.selected_processing_mode_id = get_default_mode_id()
            self.selected_model_profile = find_model_profile(self.selected_model_profile_id)
            self.selected_processing_mode = find_processing_mode(self.selected_processing_mode_id)
            self.detail_level = self.selected_processing_mode.detail_level
            
            # Inicializar componentes del core
            self.init_core_components()
            
            # Configurar interfaz
            self.init_ui()
            self.apply_win11_style()
            
            # Timer para actualizar estadísticas
            self.stats_timer = QTimer()
            self.stats_timer.timeout.connect(self.update_statistics)
            self.stats_timer.start(5000)  # Actualizar cada 5 segundos
        
        def init_core_components(self):
            """Inicializa los componentes del core"""
            try:
                self.model_manager = Qwen2VLManager()
                self.configure_model_manager()
                self.db_manager = EnhancedDatabaseManager("stockprep_images.db")
                self.output_handler = OutputHandlerV2(output_directory=self.output_directory or "output", db_path="stockprep_images.db")
                self.keyword_extractor = KeywordExtractor()
                self.image_processor = ImageProcessor(
                    model_manager=self.model_manager,
                    keyword_extractor=self.keyword_extractor
                )
                logger.info("Componentes del core inicializados correctamente")
            except Exception as e:
                logger.error(f"Error inicializando componentes: {e}")
                QMessageBox.critical(self, "Error", f"Error inicializando componentes: {e}")

        def configure_model_manager(self):
            """Aplica el perfil de modelo seleccionado al gestor compatible."""
            profile = self.selected_model_profile
            if profile.manager != "qwen2_vl":
                raise ValueError(f"El gestor '{profile.manager}' todavia no esta integrado")

            self.model_manager.configure_model(
                model_id=profile.model_id,
                display_name=profile.label,
            )
        
        def init_ui(self):
            """Inicializa la interfaz de usuario"""
            self.setWindowTitle("StockPrep Pro v2.0 - Interfaz Windows 11")
            self.setGeometry(100, 100, 1200, 800)
            self.setMinimumSize(1000, 600)
            
            # Configurar icono
            try:
                self.setWindowIcon(QIcon("stockprep_icon.png"))
            except:
                pass # Sin icono si no se puede cargar
            
            # Widget central
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Layout principal
            main_layout = QVBoxLayout()
            central_widget.setLayout(main_layout)
            
            # Crear menú
            self.create_menu_bar()
            
            # Crear tabs
            self.tab_widget = QTabWidget()
            main_layout.addWidget(self.tab_widget)
            
            # Tab 1: Procesamiento principal
            self.create_main_tab()
            
            # Tab 2: Historial y base de datos
            self.create_history_tab()
            
            # Tab 3: Estadísticas
            self.create_stats_tab()
            
            # Barra de estado
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)
            self.status_bar.showMessage("Listo para procesar imágenes")
        
        def create_menu_bar(self):
            """Crea la barra de menú"""
            menubar = self.menuBar()
            
            # Menú Archivo
            file_menu = menubar.addMenu("Archivo")
            
            open_action = QAction("Abrir Imagen", self)
            open_action.setShortcut("Ctrl+O")
            open_action.triggered.connect(self.select_image)
            file_menu.addAction(open_action)
            
            file_menu.addSeparator()
            
            exit_action = QAction("Salir", self)
            exit_action.setShortcut("Ctrl+Q")
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)
            
            # Menú Herramientas
            tools_menu = menubar.addMenu("Herramientas")
            
            export_action = QAction("Exportar Base de Datos", self)
            export_action.triggered.connect(self.export_database)
            tools_menu.addAction(export_action)
            
            # Menú Ayuda
            help_menu = menubar.addMenu("Ayuda")
            
            about_action = QAction("Acerca de", self)
            about_action.triggered.connect(self.show_about)
            help_menu.addAction(about_action)
        
        def create_main_tab(self):
            """Crea el tab principal de procesamiento"""
            main_tab = QWidget()
            layout = QHBoxLayout()
            
            # Panel izquierdo - Imagen y controles
            left_panel = QFrame()
            left_panel.setFrameStyle(QFrame.StyledPanel)
            left_layout = QVBoxLayout()

            # Sección IA: modelo y modo
            ai_group = QGroupBox("🧠 IA")
            ai_layout = QVBoxLayout()

            model_label = QLabel("Modelo:")
            model_label.setStyleSheet("font-weight: bold; color: #2B579A;")
            ai_layout.addWidget(model_label)

            self.model_profile_combo = QComboBox()
            for profile in self.model_profiles:
                self.model_profile_combo.addItem(profile.ui_label, profile.id)
                index = self.model_profile_combo.count() - 1
                self.model_profile_combo.setItemData(index, profile.description, Qt.ToolTipRole)
            self.model_profile_combo.setCurrentIndex(
                max(0, self.model_profile_combo.findData(self.selected_model_profile_id))
            )
            self.model_profile_combo.currentIndexChanged.connect(self.on_model_profile_changed)
            ai_layout.addWidget(self.model_profile_combo)

            self.model_info_label = QLabel(self.selected_model_profile.description)
            self.model_info_label.setWordWrap(True)
            self.model_info_label.setStyleSheet("color: #666666; font-size: 11px;")
            ai_layout.addWidget(self.model_info_label)

            mode_label = QLabel("Modo:")
            mode_label.setStyleSheet("font-weight: bold; color: #2B579A;")
            ai_layout.addWidget(mode_label)

            self.processing_mode_combo = QComboBox()
            for mode in self.processing_modes:
                self.processing_mode_combo.addItem(mode.label, mode.id)
                index = self.processing_mode_combo.count() - 1
                self.processing_mode_combo.setItemData(index, mode.description, Qt.ToolTipRole)
            self.processing_mode_combo.setCurrentIndex(
                max(0, self.processing_mode_combo.findData(self.selected_processing_mode_id))
            )
            self.processing_mode_combo.currentIndexChanged.connect(self.on_processing_mode_changed)
            ai_layout.addWidget(self.processing_mode_combo)

            self.processing_mode_info_label = QLabel(self.selected_processing_mode.description)
            self.processing_mode_info_label.setWordWrap(True)
            self.processing_mode_info_label.setStyleSheet("color: #666666; font-size: 11px;")
            ai_layout.addWidget(self.processing_mode_info_label)

            ai_group.setLayout(ai_layout)
            left_layout.addWidget(ai_group)
            
            # Botón cargar modelo
            self.load_model_btn = QPushButton(f"🧠 Cargar {self.selected_model_profile.label}")
            self.load_model_btn.setMinimumHeight(50)
            self.load_model_btn.setObjectName("loadModelBtn")
            self.load_model_btn.clicked.connect(self.load_model)
            left_layout.addWidget(self.load_model_btn)
            
            # Botón para seleccionar imagen
            self.select_btn = QPushButton("📁 Seleccionar Imagen")
            self.select_btn.setMinimumHeight(50)
            self.select_btn.clicked.connect(self.select_image)
            left_layout.addWidget(self.select_btn)
            
            # Botón para seleccionar carpeta
            self.select_folder_btn = QPushButton("📂 Seleccionar Carpeta de Imágenes")
            self.select_folder_btn.setMinimumHeight(50)
            self.select_folder_btn.clicked.connect(self.select_folder)
            left_layout.addWidget(self.select_folder_btn)
            
            # Separador
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setFrameShadow(QFrame.Sunken)
            left_layout.addWidget(separator)
            
            # Sección de configuración de salida
            output_group = QGroupBox("📁 Configuración de Salida")
            output_layout = QVBoxLayout()
            
            # Botón para seleccionar carpeta de salida
            self.select_output_btn = QPushButton("📤 Seleccionar Carpeta de Salida")
            self.select_output_btn.setMinimumHeight(40)
            self.select_output_btn.clicked.connect(self.select_output_directory)
            output_layout.addWidget(self.select_output_btn)
            
            # Etiqueta de carpeta actual
            self.output_label = QLabel("📍 Salida: output/ (predeterminada)")
            self.output_label.setWordWrap(True)
            self.output_label.setStyleSheet("color: #666666; font-size: 11px;")
            output_layout.addWidget(self.output_label)
            
            # Checkbox para copiar y renombrar
            self.copy_rename_checkbox = QCheckBox("✨ Copiar y renombrar imágenes con descripción")
            self.copy_rename_checkbox.setChecked(True)
            self.copy_rename_checkbox.stateChanged.connect(self.on_copy_rename_changed)
            output_layout.addWidget(self.copy_rename_checkbox)
            
            # Checkbox para inyectar metadatos EXIF/IPTC (Fase 4)
            self.embed_metadata_checkbox = QCheckBox("💾 Inyectar metadatos (EXIF/IPTC) en el archivo original/copia")
            self.embed_metadata_checkbox.setChecked(True)
            self.embed_metadata_checkbox.stateChanged.connect(self.on_embed_metadata_changed)
            output_layout.addWidget(self.embed_metadata_checkbox)
            
            # Separador
            separator2 = QFrame()
            separator2.setFrameShape(QFrame.HLine)
            separator2.setFrameShadow(QFrame.Sunken)
            output_layout.addWidget(separator2)
            
            # Controles de nivel de detalle
            detail_label = QLabel("📝 Nivel de Detalle de Descripción:")
            detail_label.setStyleSheet("font-weight: bold; color: #2B579A;")
            output_layout.addWidget(detail_label)
            
            # Radio buttons para nivel de detalle
            self.detail_group = QButtonGroup()
            
            self.detail_minimo = QRadioButton("⚡ Mínimo (5-15 palabras)")
            self.detail_medio = QRadioButton("📖 Medio (20-50 palabras)")  
            self.detail_largo = QRadioButton("📚 Largo (50+ palabras)")
            
            # Establecer largo como predeterminado
            self.detail_largo.setChecked(True)
            
            # Agregar al grupo
            self.detail_group.addButton(self.detail_minimo, 0)
            self.detail_group.addButton(self.detail_medio, 1)
            self.detail_group.addButton(self.detail_largo, 2)
            
            # Conectar señales
            self.detail_group.buttonClicked.connect(self.on_detail_level_changed)
            
            output_layout.addWidget(self.detail_minimo)
            output_layout.addWidget(self.detail_medio)
            output_layout.addWidget(self.detail_largo)
            
            # Separador
            separator3 = QFrame()
            separator3.setFrameShape(QFrame.HLine)
            separator3.setFrameShadow(QFrame.Sunken)
            output_layout.addWidget(separator3)
            
            # Caja de Prompt Personalizado (Fase 3)
            prompt_label = QLabel("✨ Instrucciones IA (Prompt Opcional):")
            prompt_label.setStyleSheet("font-weight: bold; color: #2B579A;")
            output_layout.addWidget(prompt_label)
            
            self.custom_prompt_edit = QTextEdit()
            self.custom_prompt_edit.setPlaceholderText("Ej: Asegúrate de etiquetar el vestido como 'traje de fallera' y menciona la iluminación...")
            self.custom_prompt_edit.setMinimumHeight(45)
            self.custom_prompt_edit.setMaximumHeight(65)
            self.custom_prompt_edit.setStyleSheet("font-size: 11px;")
            output_layout.addWidget(self.custom_prompt_edit)
            
            output_group.setLayout(output_layout)
            left_layout.addWidget(output_group)
            
            # Label para mostrar imagen
            self.image_label = QLabel("Selecciona una imagen para comenzar")
            self.image_label.setAlignment(Qt.AlignCenter)
            self.image_label.setMinimumHeight(150)
            self.image_label.setStyleSheet("""
                QLabel {
                    border: 2px dashed #CCCCCC;
                    border-radius: 8px;
                    background-color: #F8F8F8;
                    color: #666666;
                    font-size: 16px;
                }
            """)
            left_layout.addWidget(self.image_label)
            
            # Botón procesar
            self.process_btn = QPushButton("🚀 Procesar Imagen")
            self.process_btn.setMinimumHeight(50)
            self.process_btn.setEnabled(False)
            self.process_btn.clicked.connect(self.process_image)
            left_layout.addWidget(self.process_btn)
            
            # Barra de progreso
            self.progress_bar = QProgressBar()
            self.progress_bar.setVisible(False)
            left_layout.addWidget(self.progress_bar)
            
            # Etiqueta de progreso para lotes
            self.batch_progress_label = QLabel("")
            self.batch_progress_label.setAlignment(Qt.AlignCenter)
            self.batch_progress_label.setVisible(False)
            left_layout.addWidget(self.batch_progress_label)
            
            left_panel.setLayout(left_layout)
            layout.addWidget(left_panel, 1)
            
            # Panel derecho - Resultados
            right_panel = QFrame()
            right_panel.setFrameStyle(QFrame.StyledPanel)
            right_layout = QVBoxLayout()
            
            # Área de resultados
            results_label = QLabel("📝 Resultados del Procesamiento")
            results_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
            right_layout.addWidget(results_label)
            
            # Caption
            caption_group = QGroupBox("📖 Descripción (Caption)")
            caption_layout = QVBoxLayout()
            self.caption_text = QTextEdit()
            self.caption_text.setMaximumHeight(120)
            self.caption_text.setPlaceholderText("La descripción aparecerá aquí...")
            caption_layout.addWidget(self.caption_text)
            caption_group.setLayout(caption_layout)
            right_layout.addWidget(caption_group)
            
            # Keywords
            keywords_group = QGroupBox("🏷️ Palabras Clave")
            keywords_layout = QVBoxLayout()
            self.keywords_text = QTextEdit()
            self.keywords_text.setMaximumHeight(100)
            self.keywords_text.setPlaceholderText("Las palabras clave aparecerán aquí...")
            keywords_layout.addWidget(self.keywords_text)
            keywords_group.setLayout(keywords_layout)
            right_layout.addWidget(keywords_group)
            
            # Objects
            objects_group = QGroupBox("🎯 Objetos Detectados")
            objects_layout = QVBoxLayout()
            self.objects_text = QTextEdit()
            self.objects_text.setMaximumHeight(150)
            self.objects_text.setPlaceholderText("Los objetos detectados aparecerán aquí...")
            objects_layout.addWidget(self.objects_text)
            objects_group.setLayout(objects_layout)
            right_layout.addWidget(objects_group)
            
            # Botón exportar
            self.export_btn = QPushButton("💾 Exportar Resultados")
            self.export_btn.setMinimumHeight(40)
            self.export_btn.setEnabled(False)
            self.export_btn.clicked.connect(self.export_results)
            right_layout.addWidget(self.export_btn)
            
            right_panel.setLayout(right_layout)
            layout.addWidget(right_panel, 1)
            
            main_tab.setLayout(layout)
            self.tab_widget.addTab(main_tab, "🖼️ Procesamiento")
        
        def create_history_tab(self):
            """Crea el tab de historial"""
            history_tab = QWidget()
            layout = QVBoxLayout()
            
            # Tabla de historial
            self.history_table = QTableWidget()
            self.history_table.setColumnCount(5)
            self.history_table.setHorizontalHeaderLabels([
                "Archivo", "Fecha", "Caption", "Keywords", "Objetos"
            ])
            layout.addWidget(self.history_table)
            
            # Botones de control
            buttons_layout = QHBoxLayout()
            
            refresh_btn = QPushButton("🔄 Actualizar")
            refresh_btn.clicked.connect(self.refresh_history)
            buttons_layout.addWidget(refresh_btn)
            
            clear_btn = QPushButton("🗑️ Limpiar Historial")
            clear_btn.clicked.connect(self.clear_history)
            buttons_layout.addWidget(clear_btn)
            
            buttons_layout.addStretch()
            layout.addLayout(buttons_layout)
            
            history_tab.setLayout(layout)
            self.tab_widget.addTab(history_tab, "📋 Historial")
        
        def create_stats_tab(self):
            """Crea el tab de estadísticas"""
            stats_tab = QWidget()
            layout = QVBoxLayout()
            
            # Widget de estadísticas
            self.stats_widget = ModernStatsWidget()
            layout.addWidget(self.stats_widget)
            
            layout.addStretch()
            stats_tab.setLayout(layout)
            self.tab_widget.addTab(stats_tab, "📊 Estadísticas")
        
        def apply_win11_style(self):
            """Aplica el estilo Windows 11 con color verde mar para éxito"""
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #F3F3F3;
                }
                
                QTabWidget::pane {
                    border: 1px solid #E0E0E0;
                    border-radius: 8px;
                    background-color: white;
                }
                
                QTabBar::tab {
                    background-color: #F8F8F8;
                    border: 1px solid #E0E0E0;
                    padding: 8px 16px;
                    margin-right: 2px;
                    border-top-left-radius: 6px;
                    border-top-right-radius: 6px;
                }
                
                QTabBar::tab:selected {
                    background-color: white;
                    border-bottom: 1px solid white;
                }
                
                QPushButton {
                    background-color: #0078D4;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 14px;
                }
                
                QPushButton:hover {
                    background-color: #106EBE;
                }
                
                QPushButton:pressed {
                    background-color: #005A9E;
                }
                
                QPushButton:disabled {
                    background-color: #CCCCCC;
                    color: #666666;
                }
                
                QTextEdit {
                    border: 1px solid #E0E0E0;
                    border-radius: 6px;
                    padding: 8px;
                    background-color: white;
                    font-family: 'Segoe UI';
                    font-size: 12px;
                }
                
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #E0E0E0;
                    border-radius: 8px;
                    margin-top: 1ex;
                    padding: 10px;
                    background-color: #FAFAFA;
                }
                
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: #2B579A;
                }
                
                QProgressBar {
                    border: 1px solid #E0E0E0;
                    border-radius: 6px;
                    text-align: center;
                    background-color: #F0F0F0;
                }
                
                QProgressBar::chunk {
                    background-color: #0078D4;
                    border-radius: 5px;
                }
                
                /* Estilo para botones con contenido cargado (verde) */
                QPushButton[loaded="true"] {
                    background-color: #3CB371;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 14px;
                }
                
                QPushButton[loaded="true"]:hover {
                    background-color: #2E8B57;
                }
                
                QPushButton[loaded="true"]:pressed {
                    background-color: #228B22;
                }
            """)
        
        def load_model(self):
            """Carga el modelo Qwen2-VL"""
            if self.model_loaded:
                QMessageBox.information(self, "Información", "El modelo ya está cargado")
                return
            
            # Verificar memoria GPU disponible antes de cargar
            if hasattr(self.model_manager, 'check_gpu_memory_sufficient'):
                sufficient, message = self.model_manager.check_gpu_memory_sufficient(4.0)
                if not sufficient:
                    reply = QMessageBox.question(
                        self, "Advertencia de Memoria",
                        f"{message}\n\n¿Deseas continuar de todos modos?\n"
                        "El modelo podría cargarse en CPU o fallar por falta de memoria.",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if reply == QMessageBox.No:
                        return
            
            # Cambiar botón a estado de carga
            self.load_model_btn.setEnabled(False)
            self.load_model_btn.setText("🔄 Cargando Modelo...")
            
            # Crear y iniciar hilo de carga
            self.model_loading_thread = ModelLoadingThread(self.model_manager)
            self.model_loading_thread.finished.connect(self.on_model_loaded)
            self.model_loading_thread.error.connect(self.on_model_error)
            self.model_loading_thread.progress.connect(self.on_model_progress)
            self.model_loading_thread.start()
        
        def on_model_progress(self, message: str):
            """Maneja el progreso de carga del modelo"""
            self.status_bar.showMessage(message)
        
        def on_model_loaded(self, success: bool):
            """Maneja el resultado de la carga del modelo"""
            if success:
                self.model_loaded = True
                
                # Cambiar botón a verde mar (#3CB371)
                self.load_model_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3CB371;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 6px;
                        font-weight: bold;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #2E8B57;
                    }
                    QPushButton:pressed {
                        background-color: #228B22;
                    }
                """)
                self.load_model_btn.setText("✅ Modelo Cargado")
                self.load_model_btn.setEnabled(False)
                
                # Mostrar información del dispositivo usado
                device_info = self.model_manager.get_device_info()
                device = device_info["device"]
                if device.startswith("cuda"):
                    gpu_name = self.model_manager.get_gpu_name()
                    self.status_bar.showMessage(f"✅ Modelo ejecutándose en GPU: {gpu_name}")
                    QMessageBox.information(
                        self, "Modelo Cargado", 
                        f"{self.selected_model_profile.label} cargado exitosamente en GPU: {gpu_name}"
                    )
                else:
                    self.status_bar.showMessage("⚠️ Modelo ejecutándose en CPU (rendimiento limitado)")
                    QMessageBox.information(
                        self, "Modelo Cargado", 
                        f"{self.selected_model_profile.label} cargado en CPU"
                    )
            else:
                # Restaurar botón al estado original
                self.reset_load_model_button()
                
                self.status_bar.showMessage("❌ Error al cargar el modelo")
                QMessageBox.critical(self, "Error", f"No se pudo cargar {self.selected_model_profile.label}")
            
            self.model_loading_thread = None
        
        def on_model_error(self, error_msg: str):
            """Maneja errores de carga del modelo"""
            # Restaurar botón al estado original
            self.reset_load_model_button()
            
            self.status_bar.showMessage(f"❌ Error inesperado: {error_msg}")
            QMessageBox.critical(self, "Error", f"Error inesperado: {error_msg}")
            self.model_loading_thread = None
        
        def select_image(self):
            """Selecciona una imagen para procesar"""
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Seleccionar Imagen",
                "",
                "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif *.tiff)"
            )
            
            if file_path:
                self.current_image_path = file_path
                self.current_folder_path = None  # Limpiar selección de carpeta
                self.batch_images = []
                self.load_image_preview(file_path)
                self.process_btn.setEnabled(True)
                self.process_btn.setText("🚀 Procesar Imagen")
                
                # Cambiar botón de selección a verde
                self.select_btn.setProperty("loaded", True)
                self.select_btn.setText("✅ Imagen Seleccionada")
                self.select_btn.style().unpolish(self.select_btn)
                self.select_btn.style().polish(self.select_btn)
                
                # Restaurar botón de carpeta al estilo normal
                self.select_folder_btn.setProperty("loaded", False)
                self.select_folder_btn.setText("📂 Seleccionar Carpeta de Imágenes")
                self.select_folder_btn.style().unpolish(self.select_folder_btn)
                self.select_folder_btn.style().polish(self.select_folder_btn)
                
                self.status_bar.showMessage(f"Imagen seleccionada: {Path(file_path).name}")
        
        def select_folder(self):
            """Selecciona una carpeta para procesamiento en lote"""
            folder_path = QFileDialog.getExistingDirectory(
                self,
                "Seleccionar Carpeta de Imágenes"
            )
            
            if folder_path:
                self.current_folder_path = folder_path
                self.current_image_path = None  # Limpiar selección de imagen individual
                
                # Buscar todas las imágenes en la carpeta
                self.batch_images = self.find_images_in_folder(folder_path)
                
                if self.batch_images:
                    # Mostrar primera imagen como preview
                    self.load_image_preview(self.batch_images[0])
                    self.process_btn.setEnabled(True)
                    self.process_btn.setText(f"🚀 Procesar {len(self.batch_images)} Imágenes")
                    
                    # Cambiar botón de carpeta a verde
                    self.select_folder_btn.setProperty("loaded", True)
                    self.select_folder_btn.setText(f"✅ {len(self.batch_images)} Imágenes Cargadas")
                    self.select_folder_btn.style().unpolish(self.select_folder_btn)
                    self.select_folder_btn.style().polish(self.select_folder_btn)
                    
                    # Restaurar botón de imagen al estilo normal
                    self.select_btn.setProperty("loaded", False)
                    self.select_btn.setText("📁 Seleccionar Imagen")
                    self.select_btn.style().unpolish(self.select_btn)
                    self.select_btn.style().polish(self.select_btn)
                    
                    self.status_bar.showMessage(f"Carpeta seleccionada: {len(self.batch_images)} imágenes encontradas en {Path(folder_path).name}")
                else:
                    QMessageBox.warning(self, "Sin imágenes", "No se encontraron imágenes en la carpeta seleccionada")
                    self.status_bar.showMessage("No se encontraron imágenes en la carpeta")
        
        def find_images_in_folder(self, folder_path: str):
            """Encuentra todas las imágenes en una carpeta"""
            extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp'}
            images_by_path = {}
            
            try:
                folder = Path(folder_path)
                for img in folder.iterdir():
                    if img.is_file() and img.suffix.lower() in extensions:
                        images_by_path[str(img.resolve()).lower()] = img
                
                # Ordenar por nombre
                images = sorted(images_by_path.values(), key=lambda path: path.name.lower())
                return [str(img) for img in images]
                
            except Exception as e:
                logger.error(f"Error buscando imágenes: {e}")
                return []
        
        def select_output_directory(self):
            """Selecciona la carpeta de salida"""
            folder_path = QFileDialog.getExistingDirectory(
                self,
                "Seleccionar Carpeta de Salida"
            )
            
            if folder_path:
                self.output_directory = folder_path
                self.output_handler.set_output_directory(folder_path)
                
                # Actualizar etiqueta
                folder_name = Path(folder_path).name
                self.output_label.setText(f"📍 Salida: {folder_name}/ (personalizada)")
                
                self.status_bar.showMessage(f"Carpeta de salida establecida: {folder_path}")
        
        def on_copy_rename_changed(self, state):
            """Maneja el cambio en el checkbox de copiar y renombrar"""
            self.copy_and_rename = state == 2  # Qt.Checked = 2

        def on_embed_metadata_changed(self, state):
            """Maneja el cambio en el checkbox de inyección de metadatos"""
            self.embed_metadata = state == 2

        def reset_load_model_button(self):
            """Devuelve el botón de carga al estado del modelo seleccionado."""
            self.load_model_btn.setEnabled(True)
            self.load_model_btn.setText(f"🧠 Cargar {self.selected_model_profile.label}")
            self.load_model_btn.setStyleSheet("")

        def on_model_profile_changed(self, index):
            """Cambia el perfil de modelo activo."""
            profile_id = self.model_profile_combo.itemData(index)
            profile = find_model_profile(profile_id)

            if not profile.selectable:
                QMessageBox.information(
                    self,
                    "Modelo no integrado",
                    f"{profile.label} esta registrado, pero todavia no tiene cargador integrado.\n\n"
                    "Lo dejamos como segunda opinion futura para no romper el flujo actual."
                )
                self.model_profile_combo.blockSignals(True)
                self.model_profile_combo.setCurrentIndex(
                    max(0, self.model_profile_combo.findData(self.selected_model_profile_id))
                )
                self.model_profile_combo.blockSignals(False)
                return

            if profile.id == self.selected_model_profile_id:
                return

            if self.model_loaded:
                reply = QMessageBox.question(
                    self,
                    "Cambiar modelo",
                    "Cambiar de modelo descargara el modelo actual de memoria.\n\n¿Continuar?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    self.model_profile_combo.blockSignals(True)
                    self.model_profile_combo.setCurrentIndex(
                        max(0, self.model_profile_combo.findData(self.selected_model_profile_id))
                    )
                    self.model_profile_combo.blockSignals(False)
                    return
                self.model_manager.descargar_modelo()
                self.model_loaded = False

            self.selected_model_profile_id = profile.id
            self.selected_model_profile = profile
            self.configure_model_manager()
            self.model_info_label.setText(profile.description)
            self.reset_load_model_button()
            self.status_bar.showMessage(f"Modelo seleccionado: {profile.label}")

        def on_processing_mode_changed(self, index):
            """Cambia el modo de procesamiento."""
            mode_id = self.processing_mode_combo.itemData(index)
            self.selected_processing_mode_id = mode_id
            self.selected_processing_mode = find_processing_mode(mode_id)
            self.processing_mode_info_label.setText(self.selected_processing_mode.description)
            self.detail_level = self.selected_processing_mode.detail_level

            radio_by_level = {
                "minimo": self.detail_minimo,
                "medio": self.detail_medio,
                "largo": self.detail_largo,
            }
            radio = radio_by_level.get(self.detail_level)
            if radio:
                radio.setChecked(True)

            self.status_bar.showMessage(f"Modo seleccionado: {self.selected_processing_mode.label}")
        
        def on_detail_level_changed(self, button):
            """Maneja el cambio en el nivel de detalle"""
            button_id = self.detail_group.id(button)
            self.detail_level = {0: 'minimo', 1: 'medio', 2: 'largo'}[button_id]
            
            # Actualizar status bar con el nivel seleccionado
            level_names = {'minimo': 'Mínimo', 'medio': 'Medio', 'largo': 'Largo'}
            self.status_bar.showMessage(f"Nivel de detalle cambiado a: {level_names[self.detail_level]}")

        def get_effective_custom_prompt(self) -> str:
            """Combina prompt manual y modo de procesamiento."""
            pieces = []
            user_prompt = self.custom_prompt_edit.toPlainText().strip()
            if user_prompt:
                pieces.append(user_prompt)
            if self.selected_processing_mode.prompt_suffix:
                pieces.append(
                    f"Processing mode: {self.selected_processing_mode.label}. "
                    f"{self.selected_processing_mode.prompt_suffix}"
                )
            return "\n\n".join(pieces)
        
        def load_image_preview(self, image_path: str):
            """Carga la vista previa de la imagen"""
            try:
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    # Escalar imagen manteniendo proporción
                    scaled_pixmap = pixmap.scaled(
                        400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled_pixmap)
                else:
                    self.image_label.setText("Error cargando imagen")
            except Exception as e:
                logger.error(f"Error cargando vista previa: {e}")
                self.image_label.setText("Error cargando imagen")
        
        def process_image(self):
            """Procesa la imagen seleccionada o lote de imágenes"""
            # Verificar que el modelo esté cargado
            if not self.model_loaded:
                reply = QMessageBox.question(
                    self, "Modelo no cargado",
                    f"{self.selected_model_profile.label} no está cargado.\n¿Deseas cargarlo ahora?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.load_model()
                return
            
            # Verificar qué procesar
            if self.batch_images:
                # Procesamiento en lote
                self.start_batch_processing()
            elif self.current_image_path:
                # Procesamiento de imagen individual
                self.process_single_image()
            else:
                QMessageBox.warning(self, "Advertencia", "Selecciona una imagen o carpeta primero")
        
        def process_single_image(self):
            """Procesa una imagen individual"""
            # Deshabilitar botones
            self.process_btn.setEnabled(False)
            self.export_btn.setEnabled(False)
            
            # Mostrar barra de progreso
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            
            custom_prompt = self.get_effective_custom_prompt()
            
            # Crear y iniciar hilo de procesamiento con nivel de detalle y prompt opcional
            self.processing_thread = ProcessingThread(
                self.current_image_path,
                self.image_processor,
                self.detail_level,
                custom_prompt,
                self.selected_model_profile_id,
                self.selected_processing_mode_id,
                self.selected_processing_mode.verify_attributes,
            )
            self.processing_thread.finished.connect(self.on_processing_finished)
            self.processing_thread.error.connect(self.on_processing_error)
            self.processing_thread.progress.connect(self.progress_bar.setValue)
            self.processing_thread.start()
            
            level_names = {'minimo': 'Mínimo', 'medio': 'Medio', 'largo': 'Largo'}
            self.status_bar.showMessage(
                f"Procesando imagen con {self.selected_model_profile.label} / {self.selected_processing_mode.label} / {level_names[self.detail_level]}..."
            )
        
        def start_batch_processing(self):
            """Inicia el procesamiento en lote"""
            if not self.batch_images:
                return
            
            # Confirmar procesamiento en lote
            reply = QMessageBox.question(
                self, "Confirmar Procesamiento en Lote",
                f"¿Procesar {len(self.batch_images)} imágenes?\n\n"
                "Esto puede tomar varios minutos dependiendo del número de imágenes.",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply != QMessageBox.Yes:
                return
            
            # Inicializar variables de lote
            self.batch_processing = True
            self.batch_current_index = 0
            
            # Deshabilitar botones
            self.process_btn.setEnabled(False)
            self.export_btn.setEnabled(False)
            
            # Mostrar barras de progreso
            self.progress_bar.setVisible(True)
            self.batch_progress_label.setVisible(True)
            
            # Procesar primera imagen
            self.process_next_batch_image()
        
        def process_next_batch_image(self):
            """Procesa la siguiente imagen en el lote"""
            if self.batch_current_index >= len(self.batch_images):
                self.finish_batch_processing()
                return
            
            current_image = self.batch_images[self.batch_current_index]
            
            # Actualizar etiquetas de progreso
            progress_text = f"Procesando imagen {self.batch_current_index + 1} de {len(self.batch_images)}"
            self.batch_progress_label.setText(progress_text)
            
            overall_progress = int((self.batch_current_index / len(self.batch_images)) * 100)
            self.progress_bar.setValue(overall_progress)
            
            # Actualizar preview con imagen actual
            self.load_image_preview(current_image)
            
            custom_prompt = self.get_effective_custom_prompt()
            
            # Crear y iniciar hilo de procesamiento con nivel de detalle y prompt opcional
            self.processing_thread = ProcessingThread(
                current_image,
                self.image_processor,
                self.detail_level,
                custom_prompt,
                self.selected_model_profile_id,
                self.selected_processing_mode_id,
                self.selected_processing_mode.verify_attributes,
            )
            self.processing_thread.finished.connect(self.on_batch_image_finished)
            self.processing_thread.error.connect(self.on_batch_image_error)
            self.processing_thread.progress.connect(self.progress_bar.setValue)
            self.processing_thread.start()
            
            self.status_bar.showMessage(f"Procesando lote: {Path(current_image).name}")
        
        def on_batch_image_finished(self, results: Dict):
            """Maneja el resultado de una imagen del lote"""
            try:
                current_image = self.batch_images[self.batch_current_index]
                
                # Guardar resultados
                self.output_handler.save_results(current_image, results, self.copy_and_rename, self.embed_metadata)
                
                # Mostrar resultados de la imagen actual
                self.update_results_display(results)
                
                # Avanzar al siguiente
                self.batch_current_index += 1
                self.processing_thread = None
                
                # Procesar siguiente imagen
                QApplication.processEvents()  # Permitir que la UI se actualice
                QTimer.singleShot(100, self.process_next_batch_image)  # Pequeña pausa
                
            except Exception as e:
                logger.error(f"Error procesando imagen del lote: {e}")
                self.on_batch_image_error(str(e))
        
        def on_batch_image_error(self, error_msg: str):
            """Maneja errores en el procesamiento de lote"""
            current_image = self.batch_images[self.batch_current_index]
            logger.error(f"Error procesando {current_image}: {error_msg}")
            
            # Avanzar al siguiente (saltar imagen con error)
            self.batch_current_index += 1
            self.processing_thread = None
            
            # Continuar con la siguiente imagen
            QTimer.singleShot(100, self.process_next_batch_image)
        
        def finish_batch_processing(self):
            """Finaliza el procesamiento en lote"""
            self.batch_processing = False
            
            # Ocultar barras de progreso
            self.progress_bar.setVisible(False)
            self.batch_progress_label.setVisible(False)
            
            # Rehabilitar botones
            self.process_btn.setEnabled(True)
            self.export_btn.setEnabled(True)
            
            # Mostrar resumen
            processed_count = self.batch_current_index
            total_count = len(self.batch_images)
            
            QMessageBox.information(
                self, "Procesamiento Completado",
                f"Procesamiento en lote completado.\n\n"
                f"Imágenes procesadas: {processed_count} de {total_count}\n"
                f"Los resultados se han guardado en la base de datos."
            )
            
            self.status_bar.showMessage(f"Lote completado: {processed_count}/{total_count} imágenes procesadas")
            
            # Actualizar historial
            self.refresh_history()
        
        def update_results_display(self, results: Dict):
            """Actualiza la visualización de resultados"""
            # Mostrar resultados en la interfaz
            self.caption_text.setText(results.get('caption', ''))
            
            keywords = results.get('keywords', [])
            if isinstance(keywords, list):
                self.keywords_text.setText('\n'.join(keywords))
            else:
                self.keywords_text.setText(str(keywords))
            
            objects = results.get('objects', [])
            if isinstance(objects, list) and objects:
                objects_text = []
                for i, obj in enumerate(objects, 1):
                    if isinstance(obj, dict):
                        name = obj.get('name', 'objeto')
                        bbox = obj.get('bbox', [0, 0, 0, 0])
                        confidence = obj.get('confidence', 0.0)
                        
                        # Formatear coordenadas de manera más legible
                        x1, y1, x2, y2 = [int(coord) for coord in bbox]
                        objects_text.append(f"{i}. {name}")
                        objects_text.append(f"   Posición: [{x1}, {y1}, {x2}, {y2}]")
                        objects_text.append(f"   Confianza: {confidence:.2f}")
                        objects_text.append("")  # Línea en blanco
                    else:
                        objects_text.append(f"{i}. {str(obj)}")
                
                # Remover última línea en blanco si existe
                if objects_text and objects_text[-1] == "":
                    objects_text.pop()
                    
                self.objects_text.setText('\n'.join(objects_text))
            elif isinstance(objects, list):
                self.objects_text.setText("No se detectaron objetos en la imagen")
            else:
                self.objects_text.setText(str(objects))
        
        def on_processing_finished(self, results: Dict):
            """Maneja el resultado del procesamiento de imagen individual"""
            try:
                # Mostrar resultados en la interfaz
                self.update_results_display(results)
                
                # Guardar resultados
                if self.output_handler.save_results(self.current_image_path, results, self.copy_and_rename, self.embed_metadata):
                    if self.copy_and_rename and results.get('renamed_file'):
                        self.status_bar.showMessage(f"Imagen procesada y renombrada: {results['renamed_file']}")
                    else:
                        self.status_bar.showMessage("Imagen procesada y guardada exitosamente")
                    self.export_btn.setEnabled(True)
                else:
                    self.status_bar.showMessage("Imagen procesada, pero error al guardar")
                
            except Exception as e:
                logger.error(f"Error mostrando resultados: {e}")
                QMessageBox.critical(self, "Error", f"Error mostrando resultados: {e}")
            
            finally:
                # Rehabilitar botones y ocultar progreso
                self.process_btn.setEnabled(True)
                self.progress_bar.setVisible(False)
                self.processing_thread = None
        
        def on_processing_error(self, error_msg: str):
            """Maneja errores de procesamiento"""
            QMessageBox.critical(self, "Error de Procesamiento", error_msg)
            self.process_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
            self.status_bar.showMessage("Error en el procesamiento")
            self.processing_thread = None
        
        def export_results(self):
            """Exporta los resultados actuales"""
            if not self.current_image_path and not self.batch_images:
                QMessageBox.warning(self, "Sin datos", "No hay resultados para exportar")
                return
            
            # Seleccionar formato de exportación
            reply = QMessageBox.question(
                self, "Formato de Exportación",
                "¿Deseas exportar en formato JSON?\n\n"
                "JSON es más completo y recomendado.\n"
                "CSV es más simple para análisis en hojas de cálculo.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            # Determinar extensión y filtros
            if reply == QMessageBox.Yes:
                extension = ".json"
                filter_str = "JSON (*.json);;Todos los archivos (*.*)"
                default_name = f"stockprep_resultados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            else:
                extension = ".csv"
                filter_str = "CSV (*.csv);;Todos los archivos (*.*)"
                default_name = f"stockprep_resultados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            # Abrir diálogo para seleccionar archivo de destino
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Exportar Resultados",
                default_name,
                filter_str
            )
            
            if not file_path:
                return
            
            try:
                # Obtener datos de la base de datos
                if self.db_manager:
                    data = self.db_manager.buscar_imagenes(limite=10000)
                    
                    if reply == QMessageBox.Yes:  # JSON
                        success = self.output_handler.export_to_json(file_path, data)
                    else:  # CSV
                        success = self.output_handler.export_to_csv(file_path, data)
                    
                    if success:
                        # Mostrar resumen de archivos individuales también
                        if self.current_image_path:
                            summary = self.output_handler.get_export_summary(self.current_image_path)
                            
                            msg = f"✅ Datos exportados a: {Path(file_path).name}\n\n"
                            msg += "Archivos individuales creados:\n"
                            for file_type, info in summary.get('files_created', {}).items():
                                status = "✅" if info['exists'] else "❌"
                                msg += f"{status} {file_type}: {Path(info['path']).name}\n"
                        else:
                            msg = f"✅ Datos exportados exitosamente a:\n{Path(file_path).name}\n\n"
                            msg += f"Total de registros: {len(data)}"
                        
                        QMessageBox.information(self, "Exportación Completada", msg)
                    else:
                        QMessageBox.critical(self, "Error", "Error durante la exportación")
                else:
                    QMessageBox.critical(self, "Error", "Base de datos no disponible")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error en exportación: {e}")
        
        def refresh_history(self):
            """Actualiza el historial de la base de datos"""
            try:
                if not self.db_manager:
                    return
                
                records = self.db_manager.buscar_imagenes()
                
                self.history_table.setRowCount(len(records))
                
                for row, record in enumerate(records):
                    # --- FIX: Asegurar que los valores no sean None antes de usarlos ---
                    file_path = record.get('file_path', '') or ''
                    created_at = record.get('created_at', '') or ''
                    caption = record.get('caption', '') or ''
                    keywords = record.get('keywords', []) or []
                    keywords_str = ', '.join(keywords) if isinstance(keywords, list) else str(keywords)
                    
                    objects = record.get('objects', []) or []
                    objects_str = f"{len(objects)} objetos detectados" if isinstance(objects, list) else ''

                    self.history_table.setItem(row, 0, QTableWidgetItem(file_path))
                    self.history_table.setItem(row, 1, QTableWidgetItem(created_at))
                    self.history_table.setItem(row, 2, QTableWidgetItem(caption[:100] + '...'))
                    self.history_table.setItem(row, 3, QTableWidgetItem(keywords_str[:50] + '...'))
                    self.history_table.setItem(row, 4, QTableWidgetItem(objects_str))
                
                self.status_bar.showMessage(f"Historial actualizado: {len(records)} registros")
                
            except Exception as e:
                logger.error(f"Error actualizando historial: {e}")
        
        def clear_history(self):
            """Limpia el historial de la base de datos"""
            reply = QMessageBox.question(
                self, "Confirmar", "¿Estás seguro de que quieres limpiar todo el historial?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    if self.db_manager:
                        # Aquí implementarías el método clear_all en db_manager
                        self.refresh_history()
                        self.status_bar.showMessage("Historial limpiado")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error limpiando historial: {e}")
        
        def update_statistics(self):
            """Actualiza las estadísticas"""
            try:
                stats = {}
                
                if self.db_manager:
                    db_stats = self.db_manager.obtener_estadisticas()
                    stats.update(db_stats)
                
                # Agregar estadísticas adicionales
                stats['last_update'] = datetime.now().strftime("%H:%M:%S")
                
                self.stats_widget.update_stats(stats)
                
            except Exception as e:
                logger.error(f"Error actualizando estadísticas: {e}")
        
        def export_database(self):
            """Exporta la base de datos"""
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Exportar Base de Datos", "", "JSON (*.json);;CSV (*.csv)"
            )
            
            if file_path:
                try:
                    if self.db_manager:
                        data = self.db_manager.buscar_imagenes()
                        
                        if file_path.endswith('.json'):
                            self.output_handler.export_to_json(file_path, {'images': data})
                        elif file_path.endswith('.csv'):
                            self.output_handler.export_to_csv(file_path, data)
                        
                        QMessageBox.information(self, "Éxito", f"Base de datos exportada a {file_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error exportando: {e}")
        
        def show_about(self):
            """Muestra información sobre la aplicación"""
            QMessageBox.about(
                self, "Acerca de StockPrep Pro",
                "StockPrep Pro v2.0\n\n"
                "Sistema todo-en-uno para procesamiento de imágenes\n"
                "con Microsoft Qwen2-VL y extracción de keywords.\n\n"
                "Características:\n"
                "• Generación automática de captions\n"
                "• Detección de objetos\n"
                "• Extracción de keywords con YAKE\n"
                "• Base de datos SQLite embebida\n"
                "• Interfaz moderna Windows 11\n\n"
                "Desarrollado con PySide6 y PyTorch"
            )
        
        def closeEvent(self, event):
            """Asegura que hilos y timers se detengan antes de cerrar solo esta ventana."""
            try:
                # Detener timer de stats
                if hasattr(self, 'stats_timer'):
                    self.stats_timer.stop()

                # Detener hilos en ejecución
                if self.model_loading_thread and self.model_loading_thread.isRunning():
                    self.model_loading_thread.quit()
                    self.model_loading_thread.wait(1000) # Esperar max 1 seg

                if self.processing_thread and self.processing_thread.isRunning():
                    self.processing_thread.quit()
                    self.processing_thread.wait(1000) # Esperar max 1 seg
                
                # Aceptar el evento de cierre para cerrar solo esta ventana
                event.accept() 
                
            except Exception as e:
                import logging
                logging.error(f"Error al cerrar la ventana del procesador: {e}")
                event.accept() # Intentar cerrar de todos modos
        
        def run(self):
            """Ejecuta la aplicación"""
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            
            self.show()
            return app.exec()

# Función de entrada para compatibilidad
def main():
    if not PYSIDE6_AVAILABLE:
        print("❌ PySide6 no está disponible. Usa la interfaz Tkinter en su lugar.")
        return
    
    app = StockPrepWin11App()
    app.run()

if __name__ == "__main__":
    main() 
