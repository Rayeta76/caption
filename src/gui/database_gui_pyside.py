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
        QGroupBox, QLineEdit, QComboBox, QDateEdit, QInputDialog, QAbstractItemView,
        QCompleter
    )
    from PySide6.QtCore import Qt, QDate
    from PySide6.QtGui import QIcon
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False

# Añadir ruta para importar módulos locales
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

if PYSIDE6_AVAILABLE:
    from core.enhanced_database_manager import EnhancedDatabaseManager, limpiar_registros_huerfanos
    from core.enhanced_database_manager_v2 import EnhancedDatabaseManagerV2
    from gui.components.edit_dialog import EditRecordDialog
    from gui.gallery_pyside import (
        open_image_viewer,
        populate_thumbnail_grid,
    )


if PYSIDE6_AVAILABLE:
    class DatabaseManagerAppPyside(QMainWindow):
        """Aplicación de gestión de base de datos con PySide6."""
        
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle("StockPrep Pro v2.0 - Gestión de Base de Datos")
            self.setMinimumSize(1200, 700)
            self.thumbnail_loader_thread = None
            self.search_loader_holder = {}
            self._gallery_thread_holder = {}
            self.gallery_records: List[Dict] = []
            self.search_gallery_records: List[Dict] = []
            self.search_filters = {}
            self.db_path = str(Path(__file__).resolve().parents[2] / "stockprep_images.db")
    
            # Icono de la aplicación
            try:
                self.setWindowIcon(QIcon("stockprep_icon.png"))
            except Exception:
                pass
            
            # Gestor de Base de Datos + esquema galería (FTS5 / thumbnails WebP) unificado
            try:
                self.db_manager = EnhancedDatabaseManagerV2(self.db_path)
            except Exception:
                self.db_manager = EnhancedDatabaseManager(self.db_path)
            self.db_v2 = self.db_manager
    
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
    
            # Doble clic: abrir visor de imagen
            try:
                self.records_table.cellDoubleClicked.connect(self.open_selected_record)
            except Exception:
                pass
    
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
                    
                    # Mostrar la ruta correcta (priorizar ruta_salida sobre file_path)
                    display_path = record.get('ruta_salida') or record.get('file_path', '')
                    self.records_table.setItem(row, 1, QTableWidgetItem(display_path))
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
                
                # Sincronizar autocompletado con palabras clave actuales
                self.actualizar_autocompletado_keywords()
    
            except Exception as e:
                QMessageBox.critical(self, "Error de Base de Datos", f"No se pudieron cargar los registros: {e}")
    
        def create_gallery_tab(self):
            """Crea la pestaña de la galería de imágenes."""
            gallery_widget = QWidget()
            layout = QVBoxLayout(gallery_widget)
    
            top = QHBoxLayout()
            btn_refresh_gallery = QPushButton("Actualizar galeria")
            btn_refresh_gallery.clicked.connect(self.load_gallery_images)
            self.gallery_status_label = QLabel("")
            top.addWidget(btn_refresh_gallery)
            top.addWidget(self.gallery_status_label, stretch=1)
            layout.addLayout(top)
    
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            layout.addWidget(scroll_area)
    
            self.gallery_container = QWidget()
            self.gallery_layout = QGridLayout(self.gallery_container)
            scroll_area.setWidget(self.gallery_container)
    
            self.notebook.addTab(gallery_widget, "Galeria de Imagenes")
            self.load_gallery_images()
    
        def load_gallery_images(self):
            """Carga la galería con thumbnails desde BLOB o disco."""
            self.gallery_records = self.db_manager.buscar_imagenes(limite=200)
            self.gallery_status_label.setText(
                f"Cargando {len(self.gallery_records)} imagenes..."
            )
            populate_thumbnail_grid(
                self.gallery_layout,
                self.gallery_records,
                self.db_path,
                self.open_record_in_viewer,
                col_count=5,
                thread_holder=self._gallery_thread_holder,
            )
            self.gallery_status_label.setText(
                f"{len(self.gallery_records)} registros en galeria (clic para ampliar)"
            )
    
        def open_record_in_viewer(self, record: Dict):
            """Abre visor ampliado con navegación entre el conjunto activo."""
            if self.notebook.currentIndex() == getattr(self, "search_tab_index", -1):
                records = self.search_gallery_records
            else:
                records = self.gallery_records
            if not records:
                records = [record]
            open_image_viewer(self, records, record, self.db_path)
    
        def closeEvent(self, event):
            """Detener hilos de carga al cerrar."""
            for holder in (self._gallery_thread_holder, self.search_loader_holder):
                thread = holder.get("thread")
                if thread and thread.isRunning():
                    thread.stop()
                    thread.wait(2000)
            super().closeEvent(event)
    
        def create_search_tab(self):
            """Búsqueda con resultados visuales (grid de miniaturas)."""
            search_widget = QWidget()
            layout = QVBoxLayout(search_widget)
    
            form = QGridLayout()
            self.search_inputs = {}
    
            form.addWidget(QLabel("Palabra clave:"), 0, 0)
            self.search_inputs['keyword'] = QLineEdit()
            self.search_inputs['keyword'].returnPressed.connect(self.perform_search)
            
            # Configurar QCompleter para el autocompletado
            self.keyword_completer = QCompleter(self)
            self.keyword_completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.keyword_completer.setFilterMode(Qt.MatchContains)
            self.search_inputs['keyword'].setCompleter(self.keyword_completer)
            
            form.addWidget(self.search_inputs['keyword'], 0, 1)
    
            form.addWidget(QLabel("Estado:"), 1, 0)
            self.search_inputs['estado'] = QComboBox()
            self.search_inputs['estado'].addItems(["Todos", "completed", "pending", "error"])
            form.addWidget(self.search_inputs['estado'], 1, 1)
    
            form.addWidget(QLabel("Formato (jpg, png):"), 2, 0)
            self.search_inputs['formato'] = QLineEdit()
            form.addWidget(self.search_inputs['formato'], 2, 1)
    
            btn_search = QPushButton("Buscar con vista de imagenes")
            btn_search.clicked.connect(self.perform_search)
            form.addWidget(btn_search, 3, 0, 1, 2)
            layout.addLayout(form)
    
            self.search_status_label = QLabel("Escribe un criterio y pulsa Buscar.")
            layout.addWidget(self.search_status_label)
    
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            self.search_gallery_container = QWidget()
            self.search_gallery_layout = QGridLayout(self.search_gallery_container)
            scroll.setWidget(self.search_gallery_container)
            layout.addWidget(scroll, stretch=1)
    
            self.search_tab_index = self.notebook.addTab(search_widget, "Busqueda Visual")
    
        def _search_records(self, filters: Dict, limite: int = 200) -> List[Dict]:
            """Busca registros: FTS5 si hay keyword y db_v2, si no filtros clásicos."""
            keyword = (filters.get("keyword") or "").strip()
            other = {k: v for k, v in filters.items() if k != "keyword"}
    
            records: List[Dict] = []
            if keyword and self.db_v2:
                try:
                    fts_query = " ".join(f"{word}*" for word in keyword.split() if word)
                    records = self.db_v2.buscar_imagenes_fts5(fts_query, limite=limite)
                except Exception:
                    records = self.db_manager.buscar_imagenes(
                        filtros={"keyword": keyword, **other},
                        limite=limite,
                    )
            else:
                records = self.db_manager.buscar_imagenes(filtros=filters or None, limite=limite)
    
            if other:
                filtered = []
                for rec in records:
                    if "estado" in other and rec.get("estado") != other["estado"]:
                        continue
                    if "formato" in other:
                        fmt = (rec.get("formato") or "").lower().replace(".", "")
                        if fmt != other["formato"]:
                            continue
                    filtered.append(rec)
                records = filtered
            return records
    
        def perform_search(self):
            """Búsqueda visual + tabla explorador."""
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
    
            self.search_gallery_records = self._search_records(self.search_filters, limite=200)
            self.search_status_label.setText(
                f"{len(self.search_gallery_records)} resultados (clic en miniatura para ampliar)"
            )
    
            populate_thumbnail_grid(
                self.search_gallery_layout,
                self.search_gallery_records,
                self.db_path,
                self.open_record_in_viewer,
                col_count=5,
                thread_holder=self.search_loader_holder,
            )
    
            self.refresh_browser_data()
            self.notebook.setCurrentIndex(self.search_tab_index)
            
        def actualizar_autocompletado_keywords(self):
            """Carga las palabras clave únicas desde la base de datos y actualiza el QCompleter."""
            if not hasattr(self, 'keyword_completer'):
                return
            try:
                from PySide6.QtCore import QStringListModel
                keywords = self.db_manager.obtener_todas_las_keywords()
                if keywords:
                    model = QStringListModel(keywords, self.keyword_completer)
                    self.keyword_completer.setModel(model)
            except Exception as e:
                print(f"Error al actualizar autocompletado: {e}")
    
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
    
        def open_selected_record(self, row: int, column: int):
            """Doble clic en explorador: abre visor ampliado."""
            try:
                id_item = self.records_table.item(row, 0)
                if not id_item:
                    return
                record_id = int(id_item.text().strip())
                records = self.db_manager.buscar_imagenes(
                    filtros=self.search_filters or None,
                    limite=500,
                )
                record_data = next((r for r in records if r.get("id") == record_id), None)
                if not record_data:
                    QMessageBox.warning(
                        self,
                        "Registro no encontrado",
                        f"No se encontro el registro con ID {record_id}.",
                    )
                    return
                self.open_record_in_viewer(record_data)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo abrir la imagen: {e}")
    
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
else:
    DatabaseManagerAppPyside = None  # type: ignore[misc, assignment]

    def start_db_gui():
        print("PySide6 no disponible. Instala con: pip install PySide6")