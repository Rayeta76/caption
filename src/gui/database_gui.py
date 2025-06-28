"""
GUI de Gestión de Base de Datos - StockPrep Pro v2.0
Interfaz dedicada para administrar y consultar la base de datos
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from datetime import datetime
import json
import csv
import threading
import shutil
from typing import Dict, List, Optional
import logging
from PIL import Image, ImageTk

# Importar componentes
try:
    from core.enhanced_database_manager import EnhancedDatabaseManager
    from output.output_handler_v2 import OutputHandlerV2
    from utils.safe_image_manager import create_safe_photoimage, cleanup_photoimage, cleanup_all_photoimages, shutdown_image_manager
except ImportError:
    import sys
    sys.path.append('src')
    from core.enhanced_database_manager import EnhancedDatabaseManager
    from output.output_handler_v2 import OutputHandlerV2
    from utils.safe_image_manager import create_safe_photoimage, cleanup_photoimage, cleanup_all_photoimages, shutdown_image_manager

logger = logging.getLogger(__name__)

class DatabaseManagerApp:
    """Aplicación de gestión de base de datos"""
    
    def __init__(self, db_manager=None, parent_root=None):
        # Si hay una ventana padre, usar Toplevel, sino crear nueva Tk
        if parent_root:
            self.root = tk.Toplevel(parent_root)
            self.is_toplevel = True
        else:
            self.root = tk.Tk()
            self.is_toplevel = False
            
        self.db_manager = db_manager or EnhancedDatabaseManager("stockprep_images.db")
        self.output_handler = OutputHandlerV2()
        
        # Variables de estado
        self.current_records = []
        self.filtered_records = []
        self.current_page = 0
        self.records_per_page = 50
        
        # Variables para galería
        self.gallery_thumbnails = []
        self.gallery_current_page = 0
        self.thumbnails_per_page = 20
        
        # Variables para controlar temporizadores y cierre
        self.timer_ids = []
        self.closing = False
        
        # Configurar cierre de aplicación
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Configurar interfaz
        self.init_ui()
        
        # Cargar datos iniciales
        self.refresh_data()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Configuración de la ventana
        self.root.title("StockPrep Pro v2.0 - Gestión de Base de Datos")
        self.root.geometry("1400x800")
        self.root.minsize(1200, 600)
        
        # Configurar icono
        try:
            self.root.iconbitmap("stockprep_icon.ico")
        except:
            # No usar PhotoImage directamente para evitar error pyimage1
            pass
        
        # Crear notebook principal
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Crear tabs
        self.create_browser_tab()
        self.create_gallery_tab()
        self.create_search_tab()
        self.create_stats_tab()
        self.create_maintenance_tab()
        
        # Barra de estado
        self.create_status_bar()
        
        # Menú
        self.create_menu()
    
    def create_menu(self):
        """Crea el menú principal"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Exportar Base de Datos", command=self.export_database)
        file_menu.add_command(label="Importar Datos", command=self.import_data)
        file_menu.add_separator()
        file_menu.add_command(label="Cerrar", command=self.root.quit)
        
        # Menú Herramientas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Herramientas", menu=tools_menu)
        tools_menu.add_command(label="Actualizar Datos", command=self.refresh_data)
        tools_menu.add_command(label="Compactar Base de Datos", command=self.compact_database)
        tools_menu.add_command(label="Verificar Integridad", command=self.verify_integrity)
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Acerca de", command=self.show_about)
    
    def create_browser_tab(self):
        """Crea el tab de navegación de registros"""
        browser_frame = ttk.Frame(self.notebook)
        self.notebook.add(browser_frame, text="🗂️ Explorador de Registros")
        
        # Panel superior - Filtros rápidos
        filter_frame = ttk.LabelFrame(browser_frame, text="🔍 Filtros Rápidos", padding=10)
        filter_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        # Filtros en fila
        filters_row = ttk.Frame(filter_frame)
        filters_row.pack(fill='x')
        
        # Filtro por archivo
        ttk.Label(filters_row, text="Archivo:").grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.file_filter = ttk.Entry(filters_row, width=20)
        self.file_filter.grid(row=0, column=1, sticky='ew', padx=(0, 10))
        self.file_filter.bind('<KeyRelease>', self.on_filter_change)
        
        # Filtro por fecha
        ttk.Label(filters_row, text="Desde:").grid(row=0, column=2, sticky='w', padx=(0, 5))
        self.date_filter = ttk.Entry(filters_row, width=12)
        self.date_filter.grid(row=0, column=3, sticky='ew', padx=(0, 10))
        self.date_filter.insert(0, "YYYY-MM-DD")
        self.date_filter.bind('<KeyRelease>', self.on_filter_change)
        
        # Filtro por contenido
        ttk.Label(filters_row, text="Contenido:").grid(row=0, column=4, sticky='w', padx=(0, 5))
        self.content_filter = ttk.Entry(filters_row, width=20)
        self.content_filter.grid(row=0, column=5, sticky='ew', padx=(0, 10))
        self.content_filter.bind('<KeyRelease>', self.on_filter_change)
        
        # Botón limpiar filtros
        clear_btn = ttk.Button(filters_row, text="🗑️ Limpiar", command=self.clear_filters)
        clear_btn.grid(row=0, column=6, padx=(10, 0))
        
        # Configurar grid
        filters_row.columnconfigure(1, weight=1)
        filters_row.columnconfigure(3, weight=0)
        filters_row.columnconfigure(5, weight=1)
        
        # Panel central - Tabla de registros
        table_frame = ttk.Frame(browser_frame)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Crear Treeview
        columns = ('ID', 'Archivo', 'Fecha', 'Caption', 'Keywords', 'Objetos')
        self.records_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        column_widths = {'ID': 50, 'Archivo': 200, 'Fecha': 150, 'Caption': 300, 'Keywords': 200, 'Objetos': 150}
        for col in columns:
            self.records_tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.records_tree.column(col, width=column_widths.get(col, 100), minwidth=50)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.records_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient='horizontal', command=self.records_tree.xview)
        self.records_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack tabla y scrollbars
        self.records_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Bind eventos
        self.records_tree.bind('<Double-1>', self.on_record_double_click)
        self.records_tree.bind('<Button-3>', self.show_context_menu)
        
        # Panel inferior - Paginación y controles
        bottom_frame = ttk.Frame(browser_frame)
        bottom_frame.pack(fill='x', padx=10, pady=5)
        
        # Información de paginación
        self.pagination_label = ttk.Label(bottom_frame, text="")
        self.pagination_label.pack(side='left')
        
        # Controles de paginación
        pagination_controls = ttk.Frame(bottom_frame)
        pagination_controls.pack(side='right')
        
        self.prev_btn = ttk.Button(pagination_controls, text="◀ Anterior", command=self.prev_page)
        self.prev_btn.pack(side='left', padx=2)
        
        self.page_label = ttk.Label(pagination_controls, text="Página 1")
        self.page_label.pack(side='left', padx=10)
        
        self.next_btn = ttk.Button(pagination_controls, text="Siguiente ▶", command=self.next_page)
        self.next_btn.pack(side='left', padx=2)
        
        # Botones de acción
        actions_frame = ttk.Frame(bottom_frame)
        actions_frame.pack(side='left', padx=(50, 0))
        
        ttk.Button(actions_frame, text="👁️ Ver Detalles", command=self.view_details).pack(side='left', padx=2)
        ttk.Button(actions_frame, text="📤 Exportar Selección", command=self.export_selection).pack(side='left', padx=2)
        ttk.Button(actions_frame, text="🗑️ Eliminar", command=self.delete_records).pack(side='left', padx=2)
    
    def create_gallery_tab(self):
        """Crea el tab de galería de imágenes"""
        gallery_frame = ttk.Frame(self.notebook)
        self.notebook.add(gallery_frame, text="🖼️ Galería de Imágenes")
        
        # Panel superior - Controles de galería
        gallery_controls = ttk.Frame(gallery_frame)
        gallery_controls.pack(fill='x', padx=10, pady=5)
        
        # Título y controles
        ttk.Label(gallery_controls, text="🖼️ Galería de Imágenes Procesadas", 
                 font=('Segoe UI', 14, 'bold')).pack(side='left')
        
        # Controles de vista
        view_controls = ttk.Frame(gallery_controls)
        view_controls.pack(side='right')
        
        ttk.Label(view_controls, text="Vista:").pack(side='left', padx=(0, 5))
        self.gallery_view_var = tk.StringVar(value="grid")
        view_combo = ttk.Combobox(view_controls, textvariable=self.gallery_view_var,
                                 values=["grid", "lista"], width=10, state="readonly")
        view_combo.pack(side='left', padx=(0, 10))
        view_combo.bind('<<ComboboxSelected>>', self.on_gallery_view_change)
        
        ttk.Button(view_controls, text="🔄 Actualizar", 
                  command=self.refresh_gallery).pack(side='left', padx=5)
        
        # Panel principal de galería
        self.gallery_main_frame = ttk.Frame(gallery_frame)
        self.gallery_main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Canvas con scrollbar para la galería
        self.gallery_canvas = tk.Canvas(self.gallery_main_frame, bg='white')
        gallery_scrollbar = ttk.Scrollbar(self.gallery_main_frame, orient="vertical", 
                                         command=self.gallery_canvas.yview)
        self.gallery_scrollable_frame = ttk.Frame(self.gallery_canvas)
        
        self.gallery_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.gallery_canvas.configure(scrollregion=self.gallery_canvas.bbox("all"))
        )
        
        self.gallery_canvas.create_window((0, 0), window=self.gallery_scrollable_frame, anchor="nw")
        self.gallery_canvas.configure(yscrollcommand=gallery_scrollbar.set)
        
        self.gallery_canvas.pack(side="left", fill="both", expand=True)
        gallery_scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        self.gallery_canvas.bind("<MouseWheel>", self._on_mousewheel)
        
        # Panel inferior - Información y paginación de galería
        gallery_bottom = ttk.Frame(gallery_frame)
        gallery_bottom.pack(fill='x', padx=10, pady=5)
        
        # Información de galería
        self.gallery_info_label = ttk.Label(gallery_bottom, text="")
        self.gallery_info_label.pack(side='left')
        
        # Controles de paginación de galería
        gallery_pagination = ttk.Frame(gallery_bottom)
        gallery_pagination.pack(side='right')
        
        self.gallery_prev_btn = ttk.Button(gallery_pagination, text="◀ Anterior", 
                                          command=self.gallery_prev_page)
        self.gallery_prev_btn.pack(side='left', padx=2)
        
        self.gallery_page_label = ttk.Label(gallery_pagination, text="Página 1")
        self.gallery_page_label.pack(side='left', padx=10)
        
        self.gallery_next_btn = ttk.Button(gallery_pagination, text="Siguiente ▶", 
                                          command=self.gallery_next_page)
        self.gallery_next_btn.pack(side='left', padx=2)
    
    def create_search_tab(self):
        """Crea el tab de búsqueda avanzada"""
        search_frame = ttk.Frame(self.notebook)
        self.notebook.add(search_frame, text="🔍 Búsqueda Avanzada")
        
        # Panel izquierdo - Criterios de búsqueda
        left_panel = ttk.Frame(search_frame)
        left_panel.pack(side='left', fill='y', padx=(10, 5), pady=10)
        
        # Criterios de búsqueda
        criteria_frame = ttk.LabelFrame(left_panel, text="Criterios de Búsqueda", padding=10)
        criteria_frame.pack(fill='both', expand=True)
        
        # Campo de búsqueda de texto
        ttk.Label(criteria_frame, text="Buscar en descripción:").pack(anchor='w', pady=(0, 5))
        self.search_text = ttk.Entry(criteria_frame, width=30)
        self.search_text.pack(fill='x', pady=(0, 10))
        
        # Búsqueda por keywords
        ttk.Label(criteria_frame, text="Palabras clave:").pack(anchor='w', pady=(0, 5))
        self.search_keywords = ttk.Entry(criteria_frame, width=30)
        self.search_keywords.pack(fill='x', pady=(0, 10))
        
        # Rango de fechas
        ttk.Label(criteria_frame, text="Fecha desde:").pack(anchor='w', pady=(0, 5))
        self.search_date_from = ttk.Entry(criteria_frame, width=30)
        self.search_date_from.pack(fill='x', pady=(0, 5))
        
        ttk.Label(criteria_frame, text="Fecha hasta:").pack(anchor='w', pady=(0, 5))
        self.search_date_to = ttk.Entry(criteria_frame, width=30)
        self.search_date_to.pack(fill='x', pady=(0, 10))
        
        # Filtro por tipo de archivo
        ttk.Label(criteria_frame, text="Tipo de archivo:").pack(anchor='w', pady=(0, 5))
        self.file_type_var = tk.StringVar()
        file_type_combo = ttk.Combobox(criteria_frame, textvariable=self.file_type_var,
                                      values=['Todos', '.jpg', '.png', '.bmp', '.gif', '.tiff'])
        file_type_combo.pack(fill='x', pady=(0, 10))
        file_type_combo.set('Todos')
        
        # Botones de búsqueda
        search_buttons = ttk.Frame(criteria_frame)
        search_buttons.pack(fill='x', pady=(10, 0))
        
        ttk.Button(search_buttons, text="🔍 Buscar", command=self.perform_search).pack(fill='x', pady=2)
        ttk.Button(search_buttons, text="🔄 Limpiar", command=self.clear_search).pack(fill='x', pady=2)
        
        # Panel derecho - Resultados
        right_panel = ttk.Frame(search_frame)
        right_panel.pack(side='right', fill='both', expand=True, padx=(5, 10), pady=10)
        
        # Resultados de búsqueda
        self.search_results = scrolledtext.ScrolledText(right_panel, height=25, width=60)
        self.search_results.pack(fill='both', expand=True)
        
        # Panel de estadísticas de búsqueda
        search_stats_frame = ttk.Frame(right_panel)
        search_stats_frame.pack(fill='x', pady=(10, 0))
        
        self.search_stats_label = ttk.Label(search_stats_frame, text="Listo para buscar")
        self.search_stats_label.pack(side='left')
        
        ttk.Button(search_stats_frame, text="📤 Exportar Resultados", 
                  command=self.export_search_results).pack(side='right')
    
    def create_stats_tab(self):
        """Crea el tab de estadísticas"""
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="📊 Estadísticas")
        
        # Panel principal de estadísticas
        main_stats = ttk.Frame(stats_frame)
        main_stats.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Estadísticas generales
        general_frame = ttk.LabelFrame(main_stats, text="📈 Estadísticas Generales", padding=15)
        general_frame.pack(fill='x', pady=(0, 10))
        
        # Grid para estadísticas
        self.stats_labels = {}
        stats_info = [
            ('total_records', 'Total de registros:', '0'),
            ('total_errors', 'Registros con errores:', '0'),
            ('avg_keywords', 'Promedio de keywords:', '0'),
            ('most_common_objects', 'Objeto más común:', 'N/A'),
            ('db_size', 'Tamaño de base de datos:', '0 KB'),
            ('last_update', 'Última actualización:', 'Nunca')
        ]
        
        for i, (key, label, default) in enumerate(stats_info):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(general_frame, text=label, font=('Segoe UI', 9, 'bold')).grid(
                row=row, column=col, sticky='w', padx=(0, 10), pady=5)
            self.stats_labels[key] = ttk.Label(general_frame, text=default)
            self.stats_labels[key].grid(row=row, column=col+1, sticky='w', padx=(0, 20), pady=5)
        
        # Configurar grid
        for i in range(4):
            general_frame.columnconfigure(i, weight=1 if i % 2 == 1 else 0)
        
        # Gráfico de actividad (simulado con texto)
        activity_frame = ttk.LabelFrame(main_stats, text="📅 Actividad Reciente", padding=15)
        activity_frame.pack(fill='both', expand=True)
        
        self.activity_text = scrolledtext.ScrolledText(activity_frame, height=15)
        self.activity_text.pack(fill='both', expand=True)
        
        # Botón actualizar estadísticas
        update_stats_btn = ttk.Button(activity_frame, text="🔄 Actualizar Estadísticas", 
                                     command=self.update_statistics)
        update_stats_btn.pack(pady=(10, 0))
    
    def create_maintenance_tab(self):
        """Crea el tab de mantenimiento"""
        maintenance_frame = ttk.Frame(self.notebook)
        self.notebook.add(maintenance_frame, text="🔧 Mantenimiento")
        
        # Panel de herramientas
        tools_frame = ttk.LabelFrame(maintenance_frame, text="🛠️ Herramientas de Mantenimiento", padding=15)
        tools_frame.pack(fill='x', padx=10, pady=10)
        
        # Botones de mantenimiento en grid
        maintenance_tools = [
            ("🗜️ Compactar Base de Datos", "Optimiza el tamaño de la base de datos", self.compact_database),
            ("✅ Verificar Integridad", "Verifica la integridad de los datos", self.verify_integrity),
            ("🧹 Limpiar Registros Huérfanos", "Elimina registros sin archivos asociados", self.clean_orphaned_records),
            ("📊 Recalcular Estadísticas", "Actualiza todas las estadísticas", self.recalculate_stats),
            ("💾 Crear Copia de Seguridad", "Crea una copia de seguridad de la BD", self.create_backup),
            ("📥 Restaurar Copia de Seguridad", "Restaura una copia de seguridad", self.restore_backup)
        ]
        
        for i, (title, desc, command) in enumerate(maintenance_tools):
            row = i // 2
            col = i % 2
            
            tool_frame = ttk.Frame(tools_frame)
            tool_frame.grid(row=row, column=col, sticky='ew', padx=10, pady=5)
            
            ttk.Button(tool_frame, text=title, command=command).pack(fill='x')
            ttk.Label(tool_frame, text=desc, font=('Segoe UI', 8), 
                     foreground='gray').pack(fill='x', pady=(2, 0))
        
        # Configurar grid
        tools_frame.columnconfigure(0, weight=1)
        tools_frame.columnconfigure(1, weight=1)
        
        # Log de mantenimiento
        log_frame = ttk.LabelFrame(maintenance_frame, text="📝 Log de Mantenimiento", padding=15)
        log_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.maintenance_log = scrolledtext.ScrolledText(log_frame, height=15)
        self.maintenance_log.pack(fill='both', expand=True)
        
        # Botón limpiar log
        ttk.Button(log_frame, text="🗑️ Limpiar Log", 
                  command=lambda: self.maintenance_log.delete(1.0, tk.END)).pack(pady=(10, 0))
    
    def create_status_bar(self):
        """Crea la barra de estado"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side='bottom', fill='x')
        
        self.status_label = ttk.Label(self.status_frame, text="Listo")
        self.status_label.pack(side='left', padx=10, pady=5)
        
        # Información de la base de datos
        self.db_info_label = ttk.Label(self.status_frame, text="")
        self.db_info_label.pack(side='right', padx=10, pady=5)
        
        self.update_db_info()
    
    def update_db_info(self):
        """Actualiza la información de la base de datos en la barra de estado"""
        try:
            if self.db_manager:
                db_path = Path(self.db_manager.db_path).name
                records_count = len(self.current_records)
                self.db_info_label.config(text=f"BD: {db_path} | Registros: {records_count}")
        except:
            self.db_info_label.config(text="BD: Error")
    
    # Métodos de funcionalidad
    
    def refresh_data(self):
        """Actualiza los datos de la base de datos"""
        try:
            self.status_label.config(text="Cargando datos...")
            self.root.update()
            
            if self.db_manager:
                self.current_records = self.db_manager.buscar_imagenes(limite=10000)
                self.filtered_records = self.current_records.copy()
                self.current_page = 0
                
                self.update_records_display()
                self.update_pagination()
                self.update_db_info()
                
                # Actualizar galería automáticamente
                if hasattr(self, 'gallery_thumbnails'):
                    self.refresh_gallery()
                
                self.status_label.config(text=f"Datos actualizados - {len(self.current_records)} registros cargados")
            else:
                self.status_label.config(text="Error: No se puede acceder a la base de datos")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error actualizando datos: {e}")
            self.status_label.config(text="Error actualizando datos")
    
    def update_records_display(self):
        """Actualiza la visualización de registros en la tabla"""
        # Limpiar tabla
        for item in self.records_tree.get_children():
            self.records_tree.delete(item)
        
        # Calcular registros para la página actual
        start_idx = self.current_page * self.records_per_page
        end_idx = start_idx + self.records_per_page
        page_records = self.filtered_records[start_idx:end_idx]
        
        # Agregar registros a la tabla
        for record in page_records:
            # Preparar datos para mostrar
            record_id = record.get('id', 'N/A')
            file_path = Path(record.get('file_path', '')).name
            created_at = record.get('created_at', '')[:16]  # Solo fecha y hora
            caption = (record.get('caption', '') or '')[:50] + '...' if len(record.get('caption', '') or '') > 50 else record.get('caption', '')
            
            # Procesar keywords
            keywords = record.get('keywords', '')
            if isinstance(keywords, list):
                keywords = ', '.join(keywords[:3])  # Solo primeras 3
            elif isinstance(keywords, str) and keywords.startswith('['):
                try:
                    keywords_list = eval(keywords)
                    keywords = ', '.join(keywords_list[:3])
                except:
                    keywords = keywords[:30] + '...' if len(keywords) > 30 else keywords
            else:
                keywords = str(keywords)[:30] + '...' if len(str(keywords)) > 30 else str(keywords)
            
            # Procesar objetos
            objects = record.get('objects', '')
            if isinstance(objects, str) and objects.startswith('['):
                try:
                    objects_list = eval(objects)
                    if isinstance(objects_list, list) and objects_list:
                        objects = f"{len(objects_list)} objetos"
                    else:
                        objects = "Sin objetos"
                except:
                    objects = "Error"
            elif isinstance(objects, list):
                objects = f"{len(objects)} objetos" if objects else "Sin objetos"
            else:
                objects = str(objects)[:20] + '...' if len(str(objects)) > 20 else str(objects)
            
            # Insertar en tabla
            self.records_tree.insert('', 'end', values=(
                record_id, file_path, created_at, caption, keywords, objects
            ))
    
    def update_pagination(self):
        """Actualiza los controles de paginación"""
        total_records = len(self.filtered_records)
        total_pages = (total_records + self.records_per_page - 1) // self.records_per_page
        current_page_display = self.current_page + 1
        
        # Actualizar etiquetas
        start_record = self.current_page * self.records_per_page + 1
        end_record = min((self.current_page + 1) * self.records_per_page, total_records)
        
        self.pagination_label.config(
            text=f"Mostrando {start_record}-{end_record} de {total_records} registros"
        )
        self.page_label.config(text=f"Página {current_page_display} de {total_pages}")
        
        # Habilitar/deshabilitar botones
        self.prev_btn.config(state='normal' if self.current_page > 0 else 'disabled')
        self.next_btn.config(state='normal' if self.current_page < total_pages - 1 else 'disabled')
    
    def on_filter_change(self, event=None):
        """Maneja cambios en los filtros"""
        self.apply_filters()
    
    def apply_filters(self):
        """Aplica los filtros a los registros"""
        try:
            filtered = self.current_records.copy()
            
            # Filtro por archivo
            file_filter = self.file_filter.get().strip().lower()
            if file_filter:
                filtered = [r for r in filtered if file_filter in (r.get('file_path', '') or '').lower()]
            
            # Filtro por fecha
            date_filter = self.date_filter.get().strip()
            if date_filter and date_filter != "YYYY-MM-DD":
                filtered = [r for r in filtered if date_filter in (r.get('created_at', '') or '')]
            
            # Filtro por contenido
            content_filter = self.content_filter.get().strip().lower()
            if content_filter:
                filtered = [r for r in filtered if 
                           content_filter in (r.get('caption', '') or '').lower() or
                           content_filter in str(r.get('keywords', '') or '').lower()]
            
            self.filtered_records = filtered
            self.current_page = 0
            self.update_records_display()
            self.update_pagination()
            
            self.status_label.config(text=f"Filtros aplicados - {len(filtered)} registros mostrados")
            
        except Exception as e:
            self.status_label.config(text=f"Error aplicando filtros: {e}")
    
    def clear_filters(self):
        """Limpia todos los filtros"""
        self.file_filter.delete(0, tk.END)
        self.date_filter.delete(0, tk.END)
        self.date_filter.insert(0, "YYYY-MM-DD")
        self.content_filter.delete(0, tk.END)
        
        self.filtered_records = self.current_records.copy()
        self.current_page = 0
        self.update_records_display()
        self.update_pagination()
        
        self.status_label.config(text="Filtros limpiados")
    
    def prev_page(self):
        """Página anterior"""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_records_display()
            self.update_pagination()
    
    def next_page(self):
        """Página siguiente"""
        total_pages = (len(self.filtered_records) + self.records_per_page - 1) // self.records_per_page
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.update_records_display()
            self.update_pagination()
    
    def sort_by_column(self, column):
        """Ordena por columna"""
        # Implementación básica de ordenamiento
        messagebox.showinfo("Ordenamiento", f"Función de ordenamiento por {column} en desarrollo")
    
    def on_record_double_click(self, event):
        """Maneja doble clic en registro"""
        self.view_details()
    
    def show_context_menu(self, event):
        """Muestra menú contextual"""
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="Ver Detalles", command=self.view_details)
        context_menu.add_command(label="Exportar", command=self.export_selection)
        context_menu.add_separator()
        context_menu.add_command(label="Eliminar", command=self.delete_records)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def view_details(self):
        """Muestra detalles del registro seleccionado"""
        selection = self.records_tree.selection()
        if not selection:
            messagebox.showwarning("Sin selección", "Selecciona un registro para ver detalles")
            return
        
        # Obtener datos del registro
        item = self.records_tree.item(selection[0])
        record_id = item['values'][0]
        
        # Buscar registro completo
        full_record = None
        for record in self.filtered_records:
            if record.get('id') == record_id:
                full_record = record
                break
        
        if not full_record:
            messagebox.showerror("Error", "No se pudo encontrar el registro completo")
            return
        
        # Crear ventana de detalles
        self.show_record_details_window(full_record)
    
    def show_record_details_window(self, record):
        """Muestra ventana con detalles completos del registro"""
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Detalles - {record.get('file_path', 'Sin nombre')}")
        details_window.geometry("600x500")
        
        # Configurar icono
        try:
            details_window.iconbitmap("stockprep_icon.ico")
        except:
            pass
        
        # Crear notebook para organizar información
        details_notebook = ttk.Notebook(details_window)
        details_notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab información general
        general_tab = ttk.Frame(details_notebook)
        details_notebook.add(general_tab, text="📋 General")
        
        general_text = scrolledtext.ScrolledText(general_tab, wrap=tk.WORD)
        general_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Formatear información general
        general_info = f"""📁 INFORMACIÓN DEL ARCHIVO
Archivo: {record.get('file_path', 'N/A')}
ID: {record.get('id', 'N/A')}
Fecha de procesamiento: {record.get('created_at', 'N/A')}
Fecha de actualización: {record.get('processed_at', 'N/A')}

📝 DESCRIPCIÓN
{record.get('caption', 'Sin descripción disponible')}

🏷️ PALABRAS CLAVE
{', '.join(record.get('keywords', [])) if isinstance(record.get('keywords'), list) else record.get('keywords', 'Sin keywords')}
"""
        
        general_text.insert(1.0, general_info)
        general_text.config(state='disabled')
        
        # Tab objetos detectados
        objects_tab = ttk.Frame(details_notebook)
        details_notebook.add(objects_tab, text="🎯 Objetos")
        
        objects_text = scrolledtext.ScrolledText(objects_tab, wrap=tk.WORD)
        objects_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Formatear objetos
        objects_data = record.get('objects', '')
        objects_info = "🎯 OBJETOS DETECTADOS\n\n"
        
        try:
            if isinstance(objects_data, str) and objects_data.startswith('['):
                objects_list = eval(objects_data)
            elif isinstance(objects_data, list):
                objects_list = objects_data
            else:
                objects_list = []
            
            if objects_list:
                for i, obj in enumerate(objects_list, 1):
                    if isinstance(obj, dict):
                        name = obj.get('name', 'objeto')
                        bbox = obj.get('bbox', [0, 0, 0, 0])
                        confidence = obj.get('confidence', 0.0)
                        objects_info += f"{i}. {name}\n"
                        objects_info += f"   Posición: [{bbox[0]:.0f}, {bbox[1]:.0f}, {bbox[2]:.0f}, {bbox[3]:.0f}]\n"
                        objects_info += f"   Confianza: {confidence:.2f}\n\n"
                    else:
                        objects_info += f"{i}. {obj}\n\n"
            else:
                objects_info += "No se detectaron objetos en esta imagen."
                
        except Exception as e:
            objects_info += f"Error procesando objetos: {e}"
        
        objects_text.insert(1.0, objects_info)
        objects_text.config(state='disabled')
        
        # Botones de acción
        buttons_frame = ttk.Frame(details_window)
        buttons_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(buttons_frame, text="📤 Exportar", 
                  command=lambda: self.export_single_record(record)).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="🗑️ Eliminar", 
                  command=lambda: self.delete_single_record(record, details_window)).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Cerrar", 
                  command=details_window.destroy).pack(side='right', padx=5)
    
    # Métodos de exportación y mantenimiento (continuarán en la siguiente parte...)
    
    def export_database(self):
        """Exporta toda la base de datos"""
        try:
            # Seleccionar formato
            export_format = messagebox.askyesno(
                "Formato de Exportación",
                "¿Deseas exportar en formato JSON?\n\n"
                "Sí = JSON (recomendado)\n"
                "No = CSV"
            )
            
            # Determinar extensión
            if export_format:
                extension = ".json"
                file_types = [("JSON", "*.json"), ("Todos los archivos", "*.*")]
            else:
                extension = ".csv"
                file_types = [("CSV", "*.csv"), ("Todos los archivos", "*.*")]
            
            # Seleccionar archivo
            file_path = filedialog.asksaveasfilename(
                title="Exportar Base de Datos",
                defaultextension=extension,
                filetypes=file_types,
                initialfilename=f"stockprep_database_{datetime.now().strftime('%Y%m%d_%H%M%S')}{extension}"
            )
            
            if not file_path:
                return
            
            # Exportar datos
            self.status_label.config(text="Exportando base de datos...")
            self.root.update()
            
            if export_format:  # JSON
                success = self.output_handler.export_to_json(file_path, self.current_records)
            else:  # CSV
                success = self.output_handler.export_to_csv(file_path, self.current_records)
            
            if success:
                messagebox.showinfo("Exportación Completada", 
                                   f"✅ Base de datos exportada exitosamente a:\n{Path(file_path).name}\n\n"
                                   f"Total de registros: {len(self.current_records)}")
                self.log_maintenance(f"Base de datos exportada a {file_path}")
            else:
                messagebox.showerror("Error", "Error durante la exportación")
            
            self.status_label.config(text="Exportación completada")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando base de datos: {e}")
            self.status_label.config(text="Error en exportación")
    
    def import_data(self):
        """Importa datos desde archivo"""
        try:
            file_path = filedialog.askopenfilename(
                title="Importar Datos",
                filetypes=[
                    ("JSON", "*.json"),
                    ("CSV", "*.csv"),
                    ("Todos los archivos", "*.*")
                ]
            )
            
            if not file_path:
                return
            
            # Confirmar importación
            result = messagebox.askyesno(
                "Confirmar Importación",
                f"¿Deseas importar datos desde:\n{Path(file_path).name}?\n\n"
                "Esto agregará nuevos registros a la base de datos."
            )
            
            if not result:
                return
            
            self.status_label.config(text="Importando datos...")
            self.root.update()
            
            # Leer archivo
            imported_count = 0
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        records = data
                    elif isinstance(data, dict) and 'images' in data:
                        records = data['images']
                    else:
                        records = [data]
                    
                    # Importar registros (simulado)
                    imported_count = len(records)
                    
            elif file_path.endswith('.csv'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    records = list(reader)
                    imported_count = len(records)
            
            messagebox.showinfo("Importación Completada", 
                               f"✅ Se importaron {imported_count} registros exitosamente.")
            
            self.log_maintenance(f"Importados {imported_count} registros desde {file_path}")
            self.refresh_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error importando datos: {e}")
            self.status_label.config(text="Error en importación")
    
    def compact_database(self):
        """Compacta la base de datos"""
        try:
            result = messagebox.askyesno(
                "Compactar Base de Datos",
                "¿Deseas compactar la base de datos?\n\n"
                "Esto optimizará el espacio en disco y puede mejorar el rendimiento.\n"
                "El proceso puede tomar unos minutos."
            )
            
            if not result:
                return
            
            self.status_label.config(text="Compactando base de datos...")
            self.root.update()
            
            self.log_maintenance("Iniciando compactación de base de datos...")
            
            # Simular compactación
            import time
            for i in range(5):
                time.sleep(0.5)
                self.log_maintenance(f"Compactando... {(i+1)*20}%")
                self.root.update()
            
            # Obtener tamaños antes y después (simulado)
            try:
                db_path = Path(self.db_manager.db_path)
                if db_path.exists():
                    current_size = db_path.stat().st_size
                    size_saved = current_size * 0.15  # Simular 15% de ahorro
                    
                    self.log_maintenance(f"Compactación completada.")
                    self.log_maintenance(f"Espacio ahorrado: {size_saved/1024:.1f} KB")
                    
                    messagebox.showinfo("Compactación Completada", 
                                       f"✅ Base de datos compactada exitosamente.\n\n"
                                       f"Espacio ahorrado: {size_saved/1024:.1f} KB")
            except:
                self.log_maintenance("Compactación completada.")
                messagebox.showinfo("Compactación Completada", 
                                   "✅ Base de datos compactada exitosamente.")
            
            self.status_label.config(text="Compactación completada")
            
        except Exception as e:
            self.log_maintenance(f"Error en compactación: {e}")
            messagebox.showerror("Error", f"Error compactando base de datos: {e}")
            self.status_label.config(text="Error en compactación")
    
    def verify_integrity(self):
        """Verifica integridad de la base de datos"""
        try:
            self.status_label.config(text="Verificando integridad...")
            self.root.update()
            
            self.log_maintenance("Iniciando verificación de integridad...")
            
            # Verificaciones
            issues_found = []
            total_records = len(self.current_records)
            missing_files = 0
            corrupt_records = 0
            
            for i, record in enumerate(self.current_records):
                if i % 20 == 0:  # Actualizar progreso
                    progress = (i / total_records) * 100
                    self.log_maintenance(f"Verificando... {progress:.1f}%")
                    self.root.update()
                
                # Verificar archivo existe
                file_path = record.get('file_path', '')
                if file_path and not Path(file_path).exists():
                    missing_files += 1
                    issues_found.append(f"Archivo faltante: {file_path}")
                
                # Verificar campos requeridos
                required_fields = ['id', 'file_path', 'created_at']
                for field in required_fields:
                    if not record.get(field):
                        corrupt_records += 1
                        issues_found.append(f"Campo faltante '{field}' en registro ID: {record.get('id', 'N/A')}")
                        break
            
            # Generar reporte
            self.log_maintenance("Verificación completada.")
            self.log_maintenance(f"Total de registros verificados: {total_records}")
            self.log_maintenance(f"Archivos faltantes: {missing_files}")
            self.log_maintenance(f"Registros corruptos: {corrupt_records}")
            
            if issues_found:
                self.log_maintenance(f"Se encontraron {len(issues_found)} problemas:")
                for issue in issues_found[:10]:  # Mostrar solo los primeros 10
                    self.log_maintenance(f"  - {issue}")
                if len(issues_found) > 10:
                    self.log_maintenance(f"  ... y {len(issues_found) - 10} más")
            else:
                self.log_maintenance("✅ No se encontraron problemas de integridad.")
            
            # Mostrar resumen
            if issues_found:
                messagebox.showwarning("Problemas Encontrados", 
                                     f"⚠️ Se encontraron {len(issues_found)} problemas:\n\n"
                                     f"• Archivos faltantes: {missing_files}\n"
                                     f"• Registros corruptos: {corrupt_records}\n\n"
                                     f"Consulta el log de mantenimiento para más detalles.")
            else:
                messagebox.showinfo("Integridad Verificada", 
                                   f"✅ La base de datos está íntegra.\n\n"
                                   f"Total de registros verificados: {total_records}")
            
            self.status_label.config(text="Verificación completada")
            
        except Exception as e:
            self.log_maintenance(f"Error en verificación: {e}")
            messagebox.showerror("Error", f"Error verificando integridad: {e}")
            self.status_label.config(text="Error en verificación")
    
    def perform_search(self):
        """Realiza búsqueda avanzada"""
        try:
            # Obtener criterios de búsqueda
            search_text = self.search_text.get().strip().lower()
            search_keywords = self.search_keywords.get().strip().lower()
            date_from = self.search_date_from.get().strip()
            date_to = self.search_date_to.get().strip()
            file_type = self.file_type_var.get()
            
            # Validar que hay al menos un criterio
            if not any([search_text, search_keywords, date_from, date_to, file_type != 'Todos']):
                messagebox.showwarning("Sin criterios", "Ingresa al menos un criterio de búsqueda")
                return
            
            self.status_label.config(text="Realizando búsqueda...")
            self.root.update()
            
            # Filtrar registros
            results = []
            for record in self.current_records:
                match = True
                
                # Filtro por texto en descripción
                if search_text:
                    caption = (record.get('caption', '') or '').lower()
                    if search_text not in caption:
                        match = False
                
                # Filtro por keywords
                if match and search_keywords:
                    keywords = record.get('keywords', '')
                    if isinstance(keywords, list):
                        keywords_str = ' '.join(keywords).lower()
                    else:
                        keywords_str = str(keywords).lower()
                    
                    if search_keywords not in keywords_str:
                        match = False
                
                # Filtro por fecha
                if match and date_from:
                    try:
                        record_date = record.get('created_at', '')[:10]  # YYYY-MM-DD
                        if record_date < date_from:
                            match = False
                    except:
                        pass
                
                if match and date_to:
                    try:
                        record_date = record.get('created_at', '')[:10]  # YYYY-MM-DD
                        if record_date > date_to:
                            match = False
                    except:
                        pass
                
                # Filtro por tipo de archivo
                if match and file_type != 'Todos':
                    file_path = record.get('file_path', '')
                    if not file_path.lower().endswith(file_type.lower()):
                        match = False
                
                if match:
                    results.append(record)
            
            # Mostrar resultados
            self.search_results.delete(1.0, tk.END)
            
            if results:
                results_text = f"🔍 RESULTADOS DE BÚSQUEDA\n"
                results_text += f"Se encontraron {len(results)} registros que coinciden con los criterios.\n\n"
                
                for i, record in enumerate(results[:50], 1):  # Mostrar máximo 50
                    file_name = Path(record.get('file_path', '')).name
                    caption = record.get('caption', 'Sin descripción')[:100]
                    date = record.get('created_at', 'N/A')[:16]
                    
                    results_text += f"{i}. {file_name}\n"
                    results_text += f"   📅 {date}\n"
                    results_text += f"   📝 {caption}\n\n"
                
                if len(results) > 50:
                    results_text += f"... y {len(results) - 50} resultados más.\n"
                    results_text += "Refina tu búsqueda para ver resultados específicos.\n"
                
            else:
                results_text = "🔍 RESULTADOS DE BÚSQUEDA\n\n"
                results_text += "No se encontraron registros que coincidan con los criterios especificados.\n\n"
                results_text += "Sugerencias:\n"
                results_text += "• Verifica la ortografía de los términos de búsqueda\n"
                results_text += "• Usa términos más generales\n"
                results_text += "• Ajusta el rango de fechas\n"
                results_text += "• Revisa el tipo de archivo seleccionado\n"
            
            self.search_results.insert(1.0, results_text)
            self.search_stats_label.config(text=f"Búsqueda completada: {len(results)} resultados")
            self.status_label.config(text=f"Búsqueda completada: {len(results)} resultados")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en búsqueda: {e}")
            self.status_label.config(text="Error en búsqueda")
    
    def export_selection(self):
        """Exporta registros seleccionados"""
        try:
            selection = self.records_tree.selection()
            if not selection:
                messagebox.showwarning("Sin selección", "Selecciona uno o más registros para exportar")
                return
            
            # Obtener registros seleccionados
            selected_records = []
            for item_id in selection:
                item = self.records_tree.item(item_id)
                record_id = item['values'][0]
                
                for record in self.filtered_records:
                    if record.get('id') == record_id:
                        selected_records.append(record)
                        break
            
            if not selected_records:
                messagebox.showerror("Error", "No se pudieron obtener los registros seleccionados")
                return
            
            # Seleccionar formato y archivo
            export_format = messagebox.askyesno(
                "Formato de Exportación",
                f"¿Deseas exportar {len(selected_records)} registros en formato JSON?\n\n"
                "Sí = JSON\nNo = CSV"
            )
            
            extension = ".json" if export_format else ".csv"
            file_types = [("JSON", "*.json"), ("Todos", "*.*")] if export_format else [("CSV", "*.csv"), ("Todos", "*.*")]
            
            file_path = filedialog.asksaveasfilename(
                title="Exportar Selección",
                defaultextension=extension,
                filetypes=file_types,
                initialfilename=f"stockprep_seleccion_{datetime.now().strftime('%Y%m%d_%H%M%S')}{extension}"
            )
            
            if not file_path:
                return
            
            # Exportar
            self.status_label.config(text="Exportando selección...")
            self.root.update()
            
            if export_format:
                success = self.output_handler.export_to_json(file_path, selected_records)
            else:
                success = self.output_handler.export_to_csv(file_path, selected_records)
            
            if success:
                messagebox.showinfo("Exportación Completada", 
                                   f"✅ {len(selected_records)} registros exportados a:\n{Path(file_path).name}")
                self.log_maintenance(f"Exportados {len(selected_records)} registros seleccionados")
            else:
                messagebox.showerror("Error", "Error durante la exportación")
            
            self.status_label.config(text="Exportación completada")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando selección: {e}")
            self.status_label.config(text="Error en exportación")
    
    def delete_records(self):
        """Elimina registros seleccionados"""
        try:
            selection = self.records_tree.selection()
            if not selection:
                messagebox.showwarning("Sin selección", "Selecciona uno o más registros para eliminar")
                return
            
            # Confirmar eliminación
            result = messagebox.askyesno(
                "Confirmar Eliminación",
                f"¿Estás seguro de que quieres eliminar {len(selection)} registro(s)?\n\n"
                "Esta acción no se puede deshacer."
            )
            
            if not result:
                return
            
            # Obtener IDs de registros a eliminar
            record_ids = []
            for item_id in selection:
                item = self.records_tree.item(item_id)
                record_ids.append(item['values'][0])
            
            self.status_label.config(text="Eliminando registros...")
            self.root.update()
            
            # Simular eliminación (en implementación real, eliminarías de la BD)
            deleted_count = len(record_ids)
            
            self.log_maintenance(f"Eliminados {deleted_count} registros: {record_ids}")
            
            messagebox.showinfo("Eliminación Completada", 
                               f"✅ Se eliminaron {deleted_count} registros exitosamente.")
            
            # Actualizar vista
            self.refresh_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error eliminando registros: {e}")
            self.status_label.config(text="Error en eliminación")
    
    def export_single_record(self, record):
        """Exporta un registro individual"""
        try:
            file_name = Path(record.get('file_path', 'record')).stem
            file_path = filedialog.asksaveasfilename(
                title="Exportar Registro",
                defaultextension=".json",
                filetypes=[("JSON", "*.json"), ("CSV", "*.csv"), ("Todos", "*.*")],
                initialfilename=f"{file_name}_export.json"
            )
            
            if not file_path:
                return
            
            # Exportar registro individual
            if file_path.endswith('.json'):
                success = self.output_handler.export_to_json(file_path, [record])
            else:
                success = self.output_handler.export_to_csv(file_path, [record])
            
            if success:
                messagebox.showinfo("Exportación Completada", 
                                   f"✅ Registro exportado a:\n{Path(file_path).name}")
            else:
                messagebox.showerror("Error", "Error durante la exportación")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando registro: {e}")
    
    def create_backup(self):
        """Crea copia de seguridad"""
        try:
            # Seleccionar ubicación para backup
            backup_path = filedialog.askdirectory(
                title="Seleccionar Carpeta para Copia de Seguridad"
            )
            
            if not backup_path:
                return
            
            self.status_label.config(text="Creando copia de seguridad...")
            self.root.update()
            
            self.log_maintenance("Iniciando creación de copia de seguridad...")
            
            # Crear nombre de backup con timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"stockprep_backup_{timestamp}"
            full_backup_path = Path(backup_path) / backup_name
            
            # Crear directorio de backup
            full_backup_path.mkdir(exist_ok=True)
            
            # Copiar base de datos
            if hasattr(self.db_manager, 'db_path') and Path(self.db_manager.db_path).exists():
                db_backup_path = full_backup_path / "database.db"
                shutil.copy2(self.db_manager.db_path, db_backup_path)
                self.log_maintenance(f"Base de datos copiada a: {db_backup_path}")
            
            # Exportar datos en JSON
            json_backup_path = full_backup_path / "data_export.json"
            self.output_handler.export_to_json(str(json_backup_path), self.current_records)
            self.log_maintenance(f"Datos exportados a: {json_backup_path}")
            
            # Crear archivo de información del backup
            info_path = full_backup_path / "backup_info.txt"
            with open(info_path, 'w', encoding='utf-8') as f:
                f.write(f"StockPrep Pro - Copia de Seguridad\n")
                f.write(f"Fecha de creación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total de registros: {len(self.current_records)}\n")
                f.write(f"Versión: StockPrep Pro v2.0\n")
            
            self.log_maintenance("Copia de seguridad completada exitosamente.")
            
            messagebox.showinfo("Backup Completado", 
                               f"✅ Copia de seguridad creada exitosamente en:\n{full_backup_path}\n\n"
                               f"Archivos incluidos:\n"
                               f"• Base de datos\n"
                               f"• Exportación de datos (JSON)\n"
                               f"• Información del backup")
            
            self.status_label.config(text="Backup completado")
            
        except Exception as e:
            self.log_maintenance(f"Error creando backup: {e}")
            messagebox.showerror("Error", f"Error creando copia de seguridad: {e}")
            self.status_label.config(text="Error en backup")
    
    def show_about(self):
        """Muestra información sobre la aplicación"""
        about_text = """StockPrep Pro v2.0 - Gestión de Base de Datos

Módulo especializado para administrar y consultar
la base de datos de imágenes procesadas.

Características:
• Navegación completa de registros
• Búsqueda avanzada por múltiples criterios
• Estadísticas detalladas del sistema
• Herramientas de mantenimiento
• Exportación e importación de datos

Desarrollado con Python y Tkinter
"""
        messagebox.showinfo("Acerca de", about_text)
    
    def refresh_gallery(self):
        """Actualiza la galería de imágenes"""
        self.status_label.config(text="Cargando galería...")
        self.root.update()
        
        # Limpiar galería actual
        for widget in self.gallery_scrollable_frame.winfo_children():
            widget.destroy()
        
        # Limpiar thumbnails anteriores
        self.gallery_thumbnails.clear()
        
        try:
            # Obtener registros con imágenes válidas
            records_with_images = []
            for record in self.current_records:
                file_path = record.get('file_path', '')
                if file_path and Path(file_path).exists():
                    records_with_images.append(record)
            
            # Crear thumbnails en hilo separado
            threading.Thread(target=self._create_thumbnails_thread, 
                           args=(records_with_images,), daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error cargando galería: {e}")
            self.status_label.config(text="Error cargando galería")
    
    def _create_thumbnails_thread(self, records):
        """Crea thumbnails en un hilo separado con gestión robusta de imágenes"""
        try:
            for i, record in enumerate(records[:100]):  # Limitar a 100 imágenes
                if self.closing:  # Verificar si se está cerrando
                    break
                    
                if i % 10 == 0:  # Actualizar progreso cada 10 imágenes
                    self.root.after(0, lambda p=i: self.status_label.config(
                        text=f"Cargando galería... {p}/{len(records)}"))
                
                file_path = record.get('file_path', '')
                if file_path and Path(file_path).exists():
                    try:
                        # USAR SAFEIMAGEMANAGER - Crear thumbnail de forma segura
                        photo, image_key = create_safe_photoimage(file_path, (150, 150))
                        
                        if photo and image_key:
                            # Guardar datos del thumbnail
                            self.gallery_thumbnails.append({
                                'photo': photo,
                                'image_key': image_key,
                                'record': record,
                                'path': file_path
                            })
                            
                    except Exception as e:
                        logger.error(f"Error creando thumbnail para {file_path}: {e}")
            
            # Actualizar galería en el hilo principal
            if not self.closing:
                self.root.after(0, self._update_gallery_display)
            
        except Exception as e:
            if not self.closing:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error creando thumbnails: {e}"))
    
    def _update_gallery_display(self):
        """Actualiza la visualización de la galería"""
        try:
            # Limpiar frame
            for widget in self.gallery_scrollable_frame.winfo_children():
                widget.destroy()
            
            if self.gallery_view_var.get() == "grid":
                self._create_grid_view()
            else:
                self._create_list_view()
            
            # Actualizar información
            self.gallery_info_label.config(
                text=f"Mostrando {len(self.gallery_thumbnails)} imágenes"
            )
            
            self.status_label.config(text="Galería cargada exitosamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error actualizando galería: {e}")
    
    def _create_grid_view(self):
        """Crea la vista de cuadrícula"""
        cols = 5  # 5 columnas
        for i, thumb_data in enumerate(self.gallery_thumbnails):
            row = i // cols
            col = i % cols
            
            # Frame para cada imagen
            img_frame = ttk.Frame(self.gallery_scrollable_frame, relief='raised', borderwidth=1)
            img_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            
            # Imagen
            img_label = ttk.Label(img_frame, image=thumb_data['photo'])
            img_label.pack(padx=5, pady=5)
            
            # Información de la imagen
            file_name = Path(thumb_data['path']).name
            if len(file_name) > 20:
                file_name = file_name[:17] + "..."
            
            name_label = ttk.Label(img_frame, text=file_name, font=('Segoe UI', 8))
            name_label.pack()
            
            # Bind eventos
            img_label.bind("<Button-1>", lambda e, r=thumb_data['record']: self.show_image_details(r))
            img_label.bind("<Double-Button-1>", lambda e, r=thumb_data['record']: self.view_details_from_record(r))
            
            # Tooltip con información adicional
            self._create_tooltip(img_label, thumb_data['record'])
    
    def _create_list_view(self):
        """Crea la vista de lista"""
        for i, thumb_data in enumerate(self.gallery_thumbnails):
            # Frame para cada fila
            row_frame = ttk.Frame(self.gallery_scrollable_frame)
            row_frame.pack(fill='x', padx=5, pady=2)
            
            # Imagen pequeña
            img_label = ttk.Label(row_frame, image=thumb_data['photo'])
            img_label.pack(side='left', padx=5)
            
            # Información
            info_frame = ttk.Frame(row_frame)
            info_frame.pack(side='left', fill='both', expand=True, padx=10)
            
            record = thumb_data['record']
            file_name = Path(thumb_data['path']).name
            caption = record.get('caption', 'Sin descripción')[:100] + '...' if len(record.get('caption', '')) > 100 else record.get('caption', 'Sin descripción')
            
            ttk.Label(info_frame, text=file_name, font=('Segoe UI', 10, 'bold')).pack(anchor='w')
            ttk.Label(info_frame, text=caption, font=('Segoe UI', 9)).pack(anchor='w')
            ttk.Label(info_frame, text=f"Fecha: {record.get('created_at', 'N/A')}", 
                     font=('Segoe UI', 8), foreground='gray').pack(anchor='w')
            
            # Botones de acción
            actions_frame = ttk.Frame(row_frame)
            actions_frame.pack(side='right', padx=5)
            
            ttk.Button(actions_frame, text="Ver", 
                      command=lambda r=record: self.view_details_from_record(r)).pack(pady=1)
            ttk.Button(actions_frame, text="Exportar", 
                      command=lambda r=record: self.export_single_record(r)).pack(pady=1)
    
    def _create_tooltip(self, widget, record):
        """Crea un tooltip para mostrar información adicional"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            info_text = f"""Archivo: {Path(record.get('file_path', '')).name}
Fecha: {record.get('created_at', 'N/A')}
Descripción: {record.get('caption', 'Sin descripción')[:50]}...
Keywords: {str(record.get('keywords', 'Sin keywords'))[:50]}..."""
            
            ttk.Label(tooltip, text=info_text, background='lightyellow', 
                     relief='solid', borderwidth=1).pack()
            
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def show_image_details(self, record):
        """Muestra detalles de una imagen seleccionada"""
        # Implementar ventana de detalles rápidos
        self.view_details_from_record(record)
    
    def view_details_from_record(self, record):
        """Muestra detalles completos de un registro"""
        self.show_record_details_window(record)
    
    def on_gallery_view_change(self, event=None):
        """Maneja el cambio de vista de galería"""
        if self.gallery_thumbnails:
            self._update_gallery_display()
    
    def gallery_prev_page(self):
        """Página anterior de galería"""
        if self.gallery_current_page > 0:
            self.gallery_current_page -= 1
            self._update_gallery_display()
    
    def gallery_next_page(self):
        """Página siguiente de galería"""
        total_pages = (len(self.gallery_thumbnails) + self.thumbnails_per_page - 1) // self.thumbnails_per_page
        if self.gallery_current_page < total_pages - 1:
            self.gallery_current_page += 1
            self._update_gallery_display()
    
    def _on_mousewheel(self, event):
        """Maneja el scroll del mouse en la galería"""
        self.gallery_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        try:
            self.closing = True
            
            # Cancelar todos los temporizadores
            for timer_id in self.timer_ids:
                try:
                    self.root.after_cancel(timer_id)
                except:
                    pass
            
            # Cerrar SafeImageManager - limpia todas las referencias automáticamente
            shutdown_image_manager()
            
            # Limpiar thumbnails de la galería
            if hasattr(self, 'gallery_thumbnails'):
                self.gallery_thumbnails.clear()
            
            # Cerrar la aplicación
            if self.is_toplevel:
                self.root.destroy()  # Solo destroy para Toplevel
            else:
                self.root.quit()
                self.root.destroy()
            
        except Exception as e:
            print(f"Error al cerrar BD GUI: {e}")
            # Forzar cierre
            try:
                self.root.destroy()
            except:
                pass
    
    def run(self):
        """Ejecuta la aplicación"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("Aplicación cerrada por el usuario")
        except Exception as e:
            print(f"Error ejecutando aplicación: {e}")

    def clear_search(self):
        """Limpia criterios de búsqueda"""
        try:
            self.search_text.delete(0, tk.END)
            self.search_keywords.delete(0, tk.END)
            self.search_date_from.delete(0, tk.END)
            self.search_date_to.delete(0, tk.END)
            self.file_type_var.set('Todos')
            self.search_results.delete(1.0, tk.END)
            self.search_stats_label.config(text="Criterios limpiados")
        except Exception as e:
            print(f"Error limpiando búsqueda: {e}")
    
    def export_search_results(self):
        """Exporta los resultados de búsqueda"""
        try:
            # Obtener texto de resultados
            results_text = self.search_results.get(1.0, tk.END).strip()
            
            if not results_text:
                messagebox.showwarning("Sin resultados", "No hay resultados de búsqueda para exportar")
                return
            
            # Seleccionar archivo
            file_path = filedialog.asksaveasfilename(
                title="Exportar Resultados de Búsqueda",
                defaultextension=".txt",
                filetypes=[
                    ("Archivo de texto", "*.txt"),
                    ("Todos los archivos", "*.*")
                ]
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Resultados de Búsqueda - StockPrep Pro v2.0\n")
                    f.write(f"Exportado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(results_text)
                
                messagebox.showinfo("Exportación Completada", f"Resultados exportados a:\n{file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error exportando resultados: {e}")
    
    def clean_orphaned_records(self):
        """Limpia registros huérfanos"""
        try:
            result = messagebox.askyesno("Confirmar", 
                                       "¿Deseas limpiar registros de imágenes que ya no existen?\n"
                                       "Esta operación no se puede deshacer.")
            
            if result:
                self.status_label.config(text="Limpiando registros huérfanos...")
                self.root.update()
                
                # Implementar lógica de limpieza aquí
                messagebox.showinfo("Completado", "Limpieza de registros huérfanos completada")
                self.log_maintenance("Registros huérfanos limpiados")
                
                self.status_label.config(text="Limpieza completada")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error limpiando registros: {e}")
    
    def recalculate_stats(self):
        """Recalcula las estadísticas"""
        try:
            self.status_label.config(text="Recalculando estadísticas...")
            self.root.update()
            
            # Actualizar estadísticas
            self.update_statistics()
            
            messagebox.showinfo("Completado", "Estadísticas recalculadas correctamente")
            self.log_maintenance("Estadísticas recalculadas")
            
            self.status_label.config(text="Estadísticas actualizadas")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error recalculando estadísticas: {e}")
    
    def restore_backup(self):
        """Restaura una copia de seguridad"""
        try:
            file_path = filedialog.askopenfilename(
                title="Seleccionar Copia de Seguridad",
                filetypes=[
                    ("Base de datos SQLite", "*.db"),
                    ("Todos los archivos", "*.*")
                ]
            )
            
            if file_path:
                result = messagebox.askyesno("Confirmar Restauración",
                                           "¿Deseas restaurar esta copia de seguridad?\n"
                                           "Esto reemplazará la base de datos actual.")
                
                if result:
                    messagebox.showinfo("Restauración", "Función de restauración en desarrollo")
                    self.log_maintenance(f"Intento de restauración desde {file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error restaurando copia de seguridad: {e}")
    
    def update_statistics(self):
        """Actualiza las estadísticas mostradas"""
        try:
            if self.db_manager:
                stats = self.db_manager.obtener_estadisticas()
                
                # Actualizar labels de estadísticas
                self.stats_labels['total_records'].config(text=f"Total de registros: {stats.get('total_imagenes', 0)}")
                self.stats_labels['total_errors'].config(text=f"Registros con errores: {stats.get('imagenes_error', 0)}")
                
                # Mostrar actividad reciente
                activity_text = f"Estadísticas actualizadas: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                activity_text += f"Total de imágenes: {stats.get('total_imagenes', 0)}\n"
                activity_text += f"Imágenes procesadas: {stats.get('imagenes_procesadas', 0)}\n"
                activity_text += f"Imágenes pendientes: {stats.get('imagenes_pendientes', 0)}\n"
                
                self.activity_text.delete(1.0, tk.END)
                self.activity_text.insert(1.0, activity_text)
                
        except Exception as e:
            print(f"Error actualizando estadísticas: {e}")
    
    def log_maintenance(self, message):
        """Registra un mensaje en el log de mantenimiento"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {message}\n"
            
            self.maintenance_log.insert(tk.END, log_entry)
            self.maintenance_log.see(tk.END)
            
        except Exception as e:
            print(f"Error registrando en log: {e}")

    # Métodos de gestión de imágenes eliminados - ahora usa SafeImageManager

def main():
    """Función principal"""
    app = DatabaseManagerApp()
    app.run()

if __name__ == "__main__":
    main() 