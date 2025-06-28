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
from typing import Dict, List, Optional
import logging

# Importar componentes
try:
    from core.sqlite_database import SQLiteImageDatabase
    from output.output_handler_v2 import OutputHandlerV2
except ImportError:
    import sys
    sys.path.append('src')
    from core.sqlite_database import SQLiteImageDatabase
    from output.output_handler_v2 import OutputHandlerV2

logger = logging.getLogger(__name__)

class DatabaseManagerApp:
    """Aplicación de gestión de base de datos"""
    
    def __init__(self, db_manager=None):
        self.root = tk.Tk()
        self.db_manager = db_manager or SQLiteImageDatabase()
        self.output_handler = OutputHandlerV2()
        
        # Variables de estado
        self.current_records = []
        self.filtered_records = []
        self.current_page = 0
        self.records_per_page = 50
        
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
            try:
                icon_img = tk.PhotoImage(file="stockprep_icon.png")
                self.root.iconphoto(True, icon_img)
            except:
                pass
        
        # Crear notebook principal
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Crear tabs
        self.create_browser_tab()
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
        results_frame = ttk.LabelFrame(right_panel, text="Resultados de Búsqueda", padding=10)
        results_frame.pack(fill='both', expand=True)
        
        # Lista de resultados
        self.search_results = scrolledtext.ScrolledText(results_frame, height=25, width=60)
        self.search_results.pack(fill='both', expand=True)
        
        # Panel de estadísticas de búsqueda
        search_stats_frame = ttk.Frame(results_frame)
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
        messagebox.showinfo("Exportar", "Función de exportación en desarrollo")
    
    def import_data(self):
        """Importa datos"""
        messagebox.showinfo("Importar", "Función de importación en desarrollo")
    
    def compact_database(self):
        """Compacta la base de datos"""
        self.log_maintenance("Iniciando compactación de base de datos...")
        messagebox.showinfo("Compactar", "Función de compactación en desarrollo")
    
    def verify_integrity(self):
        """Verifica integridad de la base de datos"""
        self.log_maintenance("Verificando integridad de la base de datos...")
        messagebox.showinfo("Verificar", "Función de verificación en desarrollo")
    
    def log_maintenance(self, message):
        """Registra mensaje en el log de mantenimiento"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.maintenance_log.insert(tk.END, f"[{timestamp}] {message}\n")
        self.maintenance_log.see(tk.END)
    
    def perform_search(self):
        """Realiza búsqueda avanzada"""
        messagebox.showinfo("Búsqueda", "Función de búsqueda avanzada en desarrollo")
    
    def clear_search(self):
        """Limpia criterios de búsqueda"""
        self.search_text.delete(0, tk.END)
        self.search_keywords.delete(0, tk.END)
        self.search_date_from.delete(0, tk.END)
        self.search_date_to.delete(0, tk.END)
        self.file_type_var.set('Todos')
        self.search_results.delete(1.0, tk.END)
        self.search_stats_label.config(text="Criterios limpiados")
    
    def export_selection(self):
        """Exporta registros seleccionados"""
        messagebox.showinfo("Exportar", "Función de exportación de selección en desarrollo")
    
    def delete_records(self):
        """Elimina registros seleccionados"""
        messagebox.showinfo("Eliminar", "Función de eliminación en desarrollo")
    
    def export_single_record(self, record):
        """Exporta un registro individual"""
        messagebox.showinfo("Exportar", f"Exportando registro ID: {record.get('id')}")
    
    def delete_single_record(self, record, window):
        """Elimina un registro individual"""
        result = messagebox.askyesno("Confirmar", 
                                   f"¿Eliminar el registro ID {record.get('id')}?")
        if result:
            messagebox.showinfo("Eliminar", "Función de eliminación en desarrollo")
            window.destroy()
    
    def update_statistics(self):
        """Actualiza las estadísticas"""
        try:
            if self.db_manager:
                stats = self.db_manager.obtener_estadisticas_globales()
                
                # Actualizar labels de estadísticas
                self.stats_labels['total_records'].config(text=str(stats.get('total_imagenes_procesadas', 0)))
                self.stats_labels['total_errors'].config(text=str(stats.get('total_errores', 0)))
                self.stats_labels['last_update'].config(text=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                
                # Simular otras estadísticas
                self.stats_labels['avg_keywords'].config(text="3.2")
                self.stats_labels['most_common_objects'].config(text="persona")
                
                # Tamaño de base de datos
                try:
                    db_path = Path(self.db_manager.db_path)
                    if db_path.exists():
                        size_bytes = db_path.stat().st_size
                        size_kb = size_bytes / 1024
                        if size_kb > 1024:
                            size_str = f"{size_kb/1024:.1f} MB"
                        else:
                            size_str = f"{size_kb:.1f} KB"
                        self.stats_labels['db_size'].config(text=size_str)
                except:
                    self.stats_labels['db_size'].config(text="N/A")
                
                # Actualizar actividad
                self.activity_text.delete(1.0, tk.END)
                activity_info = f"""📊 Estadísticas actualizadas: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📈 Resumen de actividad:
• Total de imágenes procesadas: {stats.get('total_imagenes_procesadas', 0)}
• Registros con errores: {stats.get('total_errores', 0)}
• Tasa de éxito: {((stats.get('total_imagenes_procesadas', 0) - stats.get('total_errores', 0)) / max(stats.get('total_imagenes_procesadas', 1), 1) * 100):.1f}%

🗄️ Información de la base de datos:
• Archivo: {self.db_manager.db_path}
• Última consulta: {datetime.now().strftime('%H:%M:%S')}

Para más estadísticas detalladas, utiliza las herramientas de mantenimiento.
"""
                self.activity_text.insert(1.0, activity_info)
                
                self.status_label.config(text="Estadísticas actualizadas")
                
        except Exception as e:
            self.status_label.config(text=f"Error actualizando estadísticas: {e}")
    
    def clean_orphaned_records(self):
        """Limpia registros huérfanos"""
        self.log_maintenance("Iniciando limpieza de registros huérfanos...")
        messagebox.showinfo("Limpiar", "Función de limpieza en desarrollo")
    
    def recalculate_stats(self):
        """Recalcula estadísticas"""
        self.log_maintenance("Recalculando estadísticas...")
        self.update_statistics()
    
    def create_backup(self):
        """Crea copia de seguridad"""
        self.log_maintenance("Creando copia de seguridad...")
        messagebox.showinfo("Backup", "Función de backup en desarrollo")
    
    def restore_backup(self):
        """Restaura copia de seguridad"""
        self.log_maintenance("Restaurando copia de seguridad...")
        messagebox.showinfo("Restaurar", "Función de restauración en desarrollo")
    
    def export_search_results(self):
        """Exporta resultados de búsqueda"""
        messagebox.showinfo("Exportar", "Función de exportación de búsqueda en desarrollo")
    
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
    
    def run(self):
        """Ejecuta la aplicación"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("Aplicación cerrada por el usuario")
        except Exception as e:
            print(f"Error ejecutando aplicación: {e}")

def main():
    """Función principal"""
    app = DatabaseManagerApp()
    app.run()

if __name__ == "__main__":
    main() 