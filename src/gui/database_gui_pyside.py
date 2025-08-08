"""
GUI de Gestión de Base de Datos - StockPrep Pro v2.0 (Versión PySide6)
"""
import sys
from pathlib import Path
from typing import Dict, List, Optional

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget,
        QMessageBox, QTableWidget, QTableWidgetItem, QPushButton,
        QHBoxLayout, QHeaderView, QScrollArea, QGridLayout, QLabel, QFrame,
        QGroupBox, QLineEdit, QComboBox, QDateEdit, QInputDialog, QAbstractItemView
    )
    from PySide6.QtCore import Qt, QThread, Signal, QDate
    from PySide6.QtGui import QIcon, QPixmap, QCursor
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False

# Añadir ruta para importar módulos locales
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

if PYSIDE6_AVAILABLE:
    from core.enhanced_database_manager import EnhancedDatabaseManager, limpiar_registros_huerfanos
    from gui.components.edit_dialog import EditRecordDialog
    # from output.output_handler_v2 import OutputHandlerV2

# Hilo para cargar las miniaturas
class ThumbnailLoaderThread(QThread):
    thumbnail_loaded = Signal(QPixmap, str, dict) # pixmap, path, record
    finished = Signal()

    def __init__(self, records):
        super().__init__()
        self.records = records
        self.is_running = True

    def run(self):
        for record in self.records:
            if not self.is_running:
                break
            
            # --- LÓGICA DE RUTA INTELIGENTE ---
            # Priorizar la ruta de salida, si no, usar la original
            path_str = record.get('ruta_salida') or record.get('file_path')
            display_name = record.get('nombre_renombrado') or record.get('nombre_original')

            if path_str and Path(path_str).exists():
                pixmap = QPixmap(path_str)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.thumbnail_loaded.emit(scaled_pixmap, display_name, record)
        self.finished.emit()
    
    def stop(self):
        self.is_running = False

# Widget para la miniatura 'clicable'
class ThumbnailWidget(QFrame):
    """Widget-frame personalizado para una miniatura que es 'clicable'."""
    clicked = Signal(dict)

    def __init__(self, pixmap, display_name, record, parent=None):
        super().__init__(parent)
        self.record = record
        
        # Estilo
        self.setFrameShape(QFrame.Box)
        self.setLineWidth(1)
        self.setCursor(QCursor(Qt.PointingHandCursor))

        # Layout
        layout = QVBoxLayout(self)
        
        img_label = QLabel()
        img_label.setPixmap(pixmap)
        img_label.setAlignment(Qt.AlignCenter)
        
        name_label = QLabel(display_name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        
        layout.addWidget(img_label)
        layout.addWidget(name_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.record)
        super().mousePressEvent(event)

class DatabaseManagerAppPyside(QMainWindow):
    """Aplicación de gestión de base de datos con PySide6."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("StockPrep Pro v2.0 - Gestión de Base de Datos")
        self.setMinimumSize(1200, 700)
        self.thumbnail_loader_thread = None
        self.search_filters = {} # Diccionario para guardar los filtros

        # Icono de la aplicación
        try:
            self.setWindowIcon(QIcon("stockprep_icon.png"))
        except:
            pass
        
        # Gestor de Base de Datos
        self.db_manager = EnhancedDatabaseManager("stockprep_images.db")

        # Configurar UI
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Crear Notebook (TabWidget)
        self.notebook = QTabWidget()
        main_layout.addWidget(self.notebook)
        
        # Crear pestañas
        self.create_browser_tab()
        self.create_gallery_tab()
        self.create_search_tab()
        self.create_stats_tab()
        self.create_maintenance_tab()

        # Cargar datos iniciales
        self.refresh_browser_data()

    def create_browser_tab(self):
        """Crea la pestaña del explorador de registros."""
        browser_widget = QWidget()
        layout = QVBoxLayout(browser_widget)

        # Controles
        controls_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("🔄 Actualizar / Mostrar Todos")
        self.btn_refresh.clicked.connect(self.clear_filters_and_refresh)
        
        # Botón para editar
        self.btn_edit = QPushButton("✏️ Editar Registro")
        self.btn_edit.clicked.connect(self.edit_selected_record)
        
        # Botón para eliminar
        self.btn_delete = QPushButton("🗑️ Eliminar Registros Seleccionados")
        self.btn_delete.clicked.connect(self.delete_selected_record)
        
        controls_layout.addWidget(self.btn_refresh)
        controls_layout.addWidget(self.btn_edit)
        controls_layout.addWidget(self.btn_delete)
        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Tabla de registros
        self.records_table = QTableWidget()
        self.records_table.setColumnCount(6)
        self.records_table.setHorizontalHeaderLabels([
            "ID", "Archivo", "Fecha", "Caption", "Keywords", "Objetos"
        ])
        self.records_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.records_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.records_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        # --- MEJORAS DE LA TABLA ---
        # 1. Habilitar ordenación
        self.records_table.setSortingEnabled(True)
        # 2. Permitir redimensionar columnas manualmente
        header = self.records_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive) # Permite arrastrar
        header.setStretchLastSection(True) # La última columna se estira

        layout.addWidget(self.records_table)
        self.notebook.addTab(browser_widget, "📂 Explorador de Registros")

    def clear_filters_and_refresh(self):
        """Limpia los filtros y refresca la tabla."""
        self.search_filters.clear()
        # Limpiar visualmente los campos de búsqueda
        if hasattr(self, 'search_inputs'):
            self.search_inputs['keyword'].setText("")
            self.search_inputs['estado'].setCurrentIndex(0)
            self.search_inputs['formato'].setText("")
        self.refresh_browser_data()

    def refresh_browser_data(self):
        """Carga o actualiza los datos en la tabla del explorador usando los filtros guardados."""
        try:
            records = self.db_manager.buscar_imagenes(filtros=self.search_filters, limite=500)
            self.records_table.setRowCount(len(records))

            for row, record in enumerate(records):
                # Usamos .get() para evitar errores si una clave no existe
                self.records_table.setItem(row, 0, QTableWidgetItem(str(record.get('id', ''))))
                self.records_table.setItem(row, 1, QTableWidgetItem(record.get('file_path', '')))
                self.records_table.setItem(row, 2, QTableWidgetItem(record.get('fecha_procesamiento', '')))
                self.records_table.setItem(row, 3, QTableWidgetItem(record.get('caption', '')))
                
                # Convertir lista de keywords a string
                keywords = record.get('keywords', [])
                keywords_str = ', '.join(keywords) if isinstance(keywords, list) else str(keywords)
                self.records_table.setItem(row, 4, QTableWidgetItem(keywords_str))

                # Contar objetos
                objects = record.get('objetos_detectados', [])
                objects_count = len(objects) if isinstance(objects, list) else 0
                self.records_table.setItem(row, 5, QTableWidgetItem(str(objects_count)))

        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"No se pudieron cargar los registros: {e}")

    def create_gallery_tab(self):
        """Crea la pestaña de la galería de imágenes."""
        gallery_widget = QWidget()
        layout = QVBoxLayout(gallery_widget)
        
        # Botón para refrescar la galería
        btn_refresh_gallery = QPushButton("🔄 Actualizar Galería")
        btn_refresh_gallery.clicked.connect(self.load_gallery_images)
        layout.addWidget(btn_refresh_gallery)

        # Área de scroll para la galería
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Widget contenedor para las miniaturas
        self.gallery_container = QWidget()
        self.gallery_layout = QGridLayout(self.gallery_container)
        scroll_area.setWidget(self.gallery_container)

        self.notebook.addTab(gallery_widget, "🖼️ Galería de Imágenes")
        
        # Carga inicial
        self.load_gallery_images()

    def load_gallery_images(self):
        """Inicia la carga de imágenes para la galería en un hilo."""
        # Limpiar galería anterior
        for i in reversed(range(self.gallery_layout.count())): 
            self.gallery_layout.itemAt(i).widget().setParent(None)

        # Detener hilo anterior si existe
        if self.thumbnail_loader_thread and self.thumbnail_loader_thread.isRunning():
            self.thumbnail_loader_thread.stop()
            self.thumbnail_loader_thread.wait()

        # Cargar registros y lanzar hilo
        records = self.db_manager.buscar_imagenes(limite=100) # Limitar a 100 para empezar
        self.thumbnail_loader_thread = ThumbnailLoaderThread(records)
        self.thumbnail_loader_thread.thumbnail_loaded.connect(self.add_thumbnail_to_gallery)
        self.thumbnail_loader_thread.start()

    def add_thumbnail_to_gallery(self, pixmap, display_name, record):
        """Añade una miniatura a la galería."""
        col_count = 5 # 5 imágenes por fila
        row = self.gallery_layout.count() // col_count
        col = self.gallery_layout.count() % col_count

        # Usar el nuevo widget personalizado
        thumbnail_widget = ThumbnailWidget(pixmap, display_name, record)
        thumbnail_widget.clicked.connect(self.show_record_details)

        self.gallery_layout.addWidget(thumbnail_widget, row, col)
        
    def show_record_details(self, record):
        """Muestra los detalles de un registro en un QMessageBox."""
        title = f"Detalles del Registro ID: {record.get('id', 'N/A')}"
        
        # Formatear el texto para que se vea bien en el QMessageBox
        details_parts = []
        details_parts.append(f"<b>Archivo:</b><br>{record.get('file_path', 'N/A')}")
        details_parts.append(f"<b>Fecha:</b><br>{record.get('fecha_procesamiento', 'N/A')}")
        details_parts.append(f"<hr><b>Caption:</b><br>{record.get('caption', 'Sin caption.')}")
        
        keywords = record.get('keywords', [])
        keywords_str = ', '.join(keywords) if keywords else "No hay keywords."
        details_parts.append(f"<hr><b>Keywords:</b><br>{keywords_str}")
        
        objects = record.get('objetos_detectados', [])
        if objects:
            # Mostramos solo los nombres de los objetos para simplicidad
            object_names = [obj.get('nombre', 'Objeto') for obj in objects]
            objects_str = '<br>'.join(f"- {name}" for name in object_names)
        else:
            objects_str = "No se detectaron objetos."
        details_parts.append(f"<hr><b>Objetos Detectados:</b><br>{objects_str}")

        QMessageBox.information(self, title, "<br>".join(details_parts))

    def closeEvent(self, event):
        """Asegurarse de que el hilo se detenga al cerrar."""
        if self.thumbnail_loader_thread and self.thumbnail_loader_thread.isRunning():
            self.thumbnail_loader_thread.stop()
            self.thumbnail_loader_thread.wait()
        super().closeEvent(event)

    def create_search_tab(self):
        """Crea la pestaña de búsqueda avanzada."""
        search_widget = QWidget()
        layout = QGridLayout(search_widget)
        
        self.search_inputs = {}

        # Fila 1: Keyword
        layout.addWidget(QLabel("Palabra Clave:"), 0, 0)
        self.search_inputs['keyword'] = QLineEdit()
        layout.addWidget(self.search_inputs['keyword'], 0, 1)

        # Fila 2: Estado
        layout.addWidget(QLabel("Estado:"), 1, 0)
        self.search_inputs['estado'] = QComboBox()
        self.search_inputs['estado'].addItems(["Todos", "completed", "pending", "error"])
        layout.addWidget(self.search_inputs['estado'], 1, 1)
        
        # Fila 3: Formato
        layout.addWidget(QLabel("Formato (ej: jpg, png):"), 2, 0)
        self.search_inputs['formato'] = QLineEdit()
        layout.addWidget(self.search_inputs['formato'], 2, 1)

        # Botones
        btn_search = QPushButton("🔍 Buscar")
        btn_search.clicked.connect(self.perform_search)
        layout.addWidget(btn_search, 3, 0, 1, 2) # Ocupa 2 columnas
        
        layout.setRowStretch(4, 1) # Empuja todo hacia arriba
        self.notebook.addTab(search_widget, "🔍 Búsqueda Avanzada")

    def perform_search(self):
        """Recoge los filtros del formulario y actualiza la tabla del explorador."""
        self.search_filters.clear()
        
        keyword = self.search_inputs['keyword'].text().strip()
        if keyword:
            self.search_filters['keyword'] = keyword
            
        estado = self.search_inputs['estado'].currentText()
        if estado != "Todos":
            self.search_filters['estado'] = estado
            
        formato = self.search_inputs['formato'].text().strip()
        if formato:
            self.search_filters['formato'] = formato.lower().replace('.', '')
        
        # Cambiar a la pestaña del explorador y refrescar
        self.notebook.setCurrentIndex(0) # 0 es el índice del explorador
        self.refresh_browser_data()

    def create_stats_tab(self):
        """Crea la pestaña de estadísticas."""
        stats_widget = QWidget()
        layout = QVBoxLayout(stats_widget)
        
        # Botón para refrescar
        btn_refresh_stats = QPushButton("🔄 Actualizar Estadísticas")
        btn_refresh_stats.clicked.connect(self.update_stats_display)
        layout.addWidget(btn_refresh_stats)
        
        # --- Grupo de Estadísticas Generales ---
        general_group = QGroupBox("📊 Estadísticas Generales")
        general_layout = QVBoxLayout(general_group)
        
        self.stats_labels = {
            'total_imagenes': QLabel("Total de imágenes: 0"),
            'imagenes_procesadas': QLabel("Imágenes procesadas: 0"),
            'imagenes_pendientes': QLabel("Imágenes pendientes: 0"),
            'imagenes_error': QLabel("Imágenes con error: 0"),
            'tamano_total': QLabel("Tamaño total en disco: 0 MB")
        }
        for label in self.stats_labels.values():
            general_layout.addWidget(label)
        
        layout.addWidget(general_group)

        # --- Grupo de Estadísticas por Formato ---
        format_group = QGroupBox("🖼️ Registros por Formato de Archivo")
        self.stats_format_layout = QVBoxLayout(format_group)
        layout.addWidget(format_group)

        layout.addStretch() # Empuja todo hacia arriba
        self.notebook.addTab(stats_widget, "📊 Estadísticas")
        
        # Carga inicial de datos
        self.update_stats_display()

    def update_stats_display(self):
        """Obtiene y muestra las estadísticas en la pestaña correspondiente."""
        try:
            stats = self.db_manager.obtener_estadisticas()
            if not stats:
                QMessageBox.warning(self, "Sin datos", "No se pudieron obtener estadísticas. La base de datos podría estar vacía.")
                return

            # Actualizar labels generales
            self.stats_labels['total_imagenes'].setText(f"Total de imágenes: {stats.get('total_imagenes', 0)}")
            self.stats_labels['imagenes_procesadas'].setText(f"Imágenes procesadas: {stats.get('imagenes_procesadas', 0)}")
            self.stats_labels['imagenes_pendientes'].setText(f"Imágenes pendientes: {stats.get('imagenes_pendientes', 0)}")
            self.stats_labels['imagenes_error'].setText(f"Imágenes con error: {stats.get('imagenes_error', 0)}")
            
            total_size_mb = stats.get('tamano', {}).get('total_bytes', 0) / (1024 * 1024)
            self.stats_labels['tamano_total'].setText(f"Tamaño total en disco: {total_size_mb:.2f} MB")

            # Actualizar stats por formato
            # Limpiar layout anterior
            for i in reversed(range(self.stats_format_layout.count())): 
                self.stats_format_layout.itemAt(i).widget().setParent(None)
            
            por_formato = stats.get('por_formato', {})
            if por_formato:
                for formato, cantidad in por_formato.items():
                    self.stats_format_layout.addWidget(QLabel(f"- {formato.upper()}: {cantidad}"))
            else:
                self.stats_format_layout.addWidget(QLabel("No hay datos de formatos."))

        except Exception as e:
            QMessageBox.critical(self, "Error de Estadísticas", f"No se pudieron cargar las estadísticas: {e}")
            
    def create_maintenance_tab(self):
        """Crea la pestaña de mantenimiento."""
        maintenance_widget = QWidget()
        layout = QVBoxLayout(maintenance_widget)
        
        # --- Grupo de Acciones de Mantenimiento ---
        maintenance_group = QGroupBox("⚙️ Acciones de Mantenimiento")
        maintenance_layout = QVBoxLayout(maintenance_group)

        btn_clean_orphans = QPushButton("🧹 Limpiar Registros Huérfanos")
        btn_clean_orphans.setToolTip("Busca y elimina registros de la BD cuyas imágenes ya no existen en el disco.")
        btn_clean_orphans.clicked.connect(self.clean_orphaned_records_action)
        
        btn_clean_history = QPushButton("🗑️ Limpiar Historial Antiguo")
        btn_clean_history.setToolTip("Elimina el historial de procesamiento (no las imágenes) más antiguo que un número de días.")
        btn_clean_history.clicked.connect(self.clean_old_history_action)

        maintenance_layout.addWidget(btn_clean_orphans)
        maintenance_layout.addWidget(btn_clean_history)
        
        layout.addWidget(maintenance_group)
        layout.addStretch()
        self.notebook.addTab(maintenance_widget, "🔧 Mantenimiento")

    def clean_orphaned_records_action(self):
        """Acción para limpiar registros de imágenes no encontradas."""
        reply = QMessageBox.question(
            self, 
            "Confirmar Limpieza",
            "¿Estás seguro de que quieres buscar y eliminar registros de imágenes que ya no existen en el disco?\n\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Nota: Esta función puede ser lenta si hay muchos registros.
                # En una app más grande, se haría en un hilo.
                deleted_count = limpiar_registros_huerfanos(self.db_manager)
                QMessageBox.information(
                    self, 
                    "Limpieza Completada", 
                    f"Se han eliminado {deleted_count} registros huérfanos."
                )
                self.refresh_browser_data() # Actualizar la vista
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Ocurrió un error durante la limpieza: {e}")

    def clean_old_history_action(self):
        """Acción para limpiar el historial de procesamiento antiguo."""
        days, ok = QInputDialog.getInt(
            self, 
            "Limpiar Historial Antiguo", 
            "Eliminar entradas del historial de procesamiento más antiguas de (días):",
            value=90, 
            min=7
        )
        
        if ok:
            reply = QMessageBox.question(
                self,
                "Confirmar Limpieza",
                f"¿Estás seguro de que quieres eliminar las entradas del historial de más de {days} días de antigüedad?\n\nEsto no elimina los registros de las imágenes, solo su historial de cambios.",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    deleted_count = self.db_manager.limpiar_registros_antiguos(days)
                    QMessageBox.information(
                        self, 
                        "Limpieza Completada", 
                        f"Se han eliminado {deleted_count} entradas del historial."
                    )
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Ocurrió un error durante la limpieza: {e}")

    def edit_selected_record(self):
        """Abre un diálogo para editar el registro seleccionado."""
        selected_items = self.records_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Sin Selección", "Por favor, selecciona un único registro para editar.")
            return
        if len(set(index.row() for index in selected_items)) > 1:
            QMessageBox.warning(self, "Selección Múltiple", "Por favor, selecciona solo un registro para editar.")
            return

        selected_row = selected_items[0].row()
        record_id = int(self.records_table.item(selected_row, 0).text())
        
        # Necesitamos todos los datos del registro para llenar el diálogo
        # Esta es una forma simple, para una app más grande se podría optimizar
        all_records = self.db_manager.buscar_imagenes(limite=99999)
        record_data = next((r for r in all_records if r['id'] == record_id), None)

        if not record_data:
            QMessageBox.critical(self, "Error", "No se pudieron encontrar los datos del registro seleccionado.")
            return
            
        dialog = EditRecordDialog(record_data, self)
        if dialog.exec(): # .exec() muestra el diálogo y espera
            new_data = dialog.get_data()
            try:
                success = self.db_manager.actualizar_campos_editables(record_id, new_data)
                if success:
                    QMessageBox.information(self, "Éxito", "Registro actualizado correctamente.")
                    self.refresh_browser_data()
                else:
                    QMessageBox.critical(self, "Error", "No se pudo actualizar el registro.")
            except Exception as e:
                QMessageBox.critical(self, "Error de Base de Datos", f"Ocurrió un error al actualizar: {e}")

    def delete_selected_record(self):
        """Elimina los registros seleccionados de la tabla y la base de datos."""
        selected_indexes = self.records_table.selectedIndexes()
        if not selected_indexes:
            QMessageBox.warning(self, "Sin Selección", "Por favor, selecciona uno o más registros para eliminar.")
            return

        # Obtener los IDs únicos de todas las filas seleccionadas
        selected_rows = sorted(list(set(index.row() for index in selected_indexes)))
        record_ids = [int(self.records_table.item(row, 0).text()) for row in selected_rows]

        reply = QMessageBox.question(
            self,
            "Confirmar Eliminación Múltiple",
            f"¿Estás seguro de que quieres eliminar permanentemente {len(record_ids)} registros?\n\nEsta acción no se puede deshacer.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                success = self.db_manager.eliminar_registros_por_ids(record_ids)
                if success:
                    QMessageBox.information(self, "Éxito", f"{len(record_ids)} registros eliminados correctamente.")
                    self.refresh_browser_data() # Actualizar la vista
                else:
                    QMessageBox.critical(self, "Error", "No se pudieron eliminar los registros seleccionados.")
            except Exception as e:
                QMessageBox.critical(self, "Error de Base de Datos", f"Ocurrió un error al eliminar: {e}")

def start_db_gui():
    if not PYSIDE6_AVAILABLE:
        QMessageBox.critical(None, "Error", "PySide6 no está instalado.")
        return

    app = QApplication.instance() or QApplication(sys.argv)
    
    db_window = DatabaseManagerAppPyside()
    db_window.show()
    
    # Solo ejecutar si no hay ya un bucle de eventos
    if not QApplication.instance():
        app.exec()

if __name__ == '__main__':
    start_db_gui() 