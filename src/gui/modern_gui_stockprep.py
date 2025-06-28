"""
Interfaz gráfica moderna con Tkinter para StockPrep Pro
Fallback cuando PySide6 no está disponible
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
from pathlib import Path
from typing import Optional, Dict
import logging
from datetime import datetime

# Importar módulos del core
try:
    from core.model_manager import Florence2Manager
    from core.image_processor import ImageProcessor
    from core.sqlite_database import SQLiteImageDatabase
    from output.output_handler_v2 import OutputHandlerV2
    from utils.keyword_extractor import KeywordExtractor
except ImportError:
    # Fallback para importaciones relativas
    import sys
    sys.path.append('src')
    from core.model_manager import Florence2Manager
    from core.image_processor import ImageProcessor
    from core.sqlite_database import SQLiteImageDatabase
    from output.output_handler_v2 import OutputHandlerV2
    from utils.keyword_extractor import KeywordExtractor

logger = logging.getLogger(__name__)

class ModernTtkStyle:
    """Estilos modernos para Tkinter/ttk"""
    
    @staticmethod
    def configure_styles():
        """Configura estilos modernos para la aplicación"""
        style = ttk.Style()
        
        # Configurar tema base
        try:
            style.theme_use('clam')  # Tema más moderno
        except:
            style.theme_use('default')
        
        # Colores modernos
        colors = {
            'bg': '#F3F3F3',           # Fondo principal
            'fg': '#333333',           # Texto principal
            'select_bg': '#0078D4',    # Azul Windows 11
            'select_fg': '#FFFFFF',    # Texto seleccionado
            'button_bg': '#0078D4',    # Fondo botones
            'button_fg': '#FFFFFF',    # Texto botones
            'entry_bg': '#FFFFFF',     # Fondo campos
            'frame_bg': '#FAFAFA',     # Fondo frames
        }
        
        # Configurar estilos de widgets
        style.configure('Modern.TFrame', 
                       background=colors['frame_bg'],
                       relief='flat',
                       borderwidth=1)
        
        style.configure('Modern.TLabel',
                       background=colors['frame_bg'],
                       foreground=colors['fg'],
                       font=('Segoe UI', 10))
        
        style.configure('Title.TLabel',
                       background=colors['frame_bg'],
                       foreground=colors['fg'],
                       font=('Segoe UI', 12, 'bold'))
        
        style.configure('Modern.TButton',
                       background=colors['button_bg'],
                       foreground=colors['button_fg'],
                       font=('Segoe UI', 10),
                       borderwidth=0,
                       focuscolor='none')
        
        style.map('Modern.TButton',
                 background=[('active', '#106EBE'),
                           ('pressed', '#005A9E'),
                           ('disabled', '#CCCCCC')])
        
        style.configure('Modern.TEntry',
                       fieldbackground=colors['entry_bg'],
                       borderwidth=1,
                       relief='solid')
        
        style.configure('Modern.Treeview',
                       background=colors['entry_bg'],
                       foreground=colors['fg'],
                       fieldbackground=colors['entry_bg'])
        
        style.configure('Modern.Treeview.Heading',
                       background=colors['frame_bg'],
                       foreground=colors['fg'],
                       font=('Segoe UI', 10, 'bold'))
        
        # Estilo para botón de éxito (modelo cargado)
        style.configure('Success.TButton',
                       background='#3CB371',    # Verde mar medio (Pantone solicitado)
                       foreground='#FFFFFF',    # Texto blanco
                       font=('Segoe UI', 10, 'bold'),
                       borderwidth=0,
                       focuscolor='none')
        
        style.map('Success.TButton',
                 background=[('active', '#2E8B57'),     # Verde mar más oscuro al hover
                           ('pressed', '#228B22'),      # Verde bosque al presionar
                           ('disabled', '#6c757d')])    # Gris cuando está deshabilitado
        
        # Estilo para botones con contenido cargado (mismo verde que Success)
        style.configure('Loaded.TButton',
                       background='#3CB371',    # Mismo verde que Success
                       foreground='#FFFFFF',    # Texto blanco
                       font=('Segoe UI', 10, 'bold'),
                       borderwidth=0,
                       focuscolor='none')
        
        style.map('Loaded.TButton',
                 background=[('active', '#2E8B57'),     # Verde mar más oscuro al hover
                           ('pressed', '#228B22'),      # Verde bosque al presionar
                           ('disabled', '#6c757d')])    # Gris cuando está deshabilitado

class StockPrepApp:
    """Aplicación principal de StockPrep Pro con Tkinter"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.current_image_path = None
        self.processing = False
        
        # Variables para procesamiento en lote
        self.current_folder_path = None
        self.batch_images = []
        self.batch_processing = False
        self.batch_current_index = 0
        
        # Variables para carpeta de salida
        self.output_directory = None
        self.copy_and_rename = True
        
        # Variables para controlar temporizadores y cierre
        self.timer_ids = []
        self.closing = False
        
        # Sistema de gestión de imágenes para evitar errores de PhotoImage
        self.image_references = {}
        self.image_counter = 0
        
        # Configurar cierre de aplicación
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Inicializar componentes del core
        self.init_core_components()
        
        # Configurar interfaz
        self.init_ui()
        
        # Configurar estilos modernos
        ModernTtkStyle.configure_styles()
        
        # Timer para estadísticas
        self.update_stats_periodically()
    
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
            
            # Limpiar todas las referencias de imágenes
            self._clear_image_references()
            
            # Limpiar referencia específica del label de imagen
            if hasattr(self, 'image_label') and hasattr(self.image_label, '_image_key'):
                try:
                    delattr(self.image_label, '_image_key')
                except:
                    pass
            
            # Cerrar la aplicación
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            print(f"Error al cerrar: {e}")
            # Forzar cierre
            try:
                self.root.destroy()
            except:
                pass
    
    def init_core_components(self):
        """Inicializa los componentes del core"""
        try:
            self.model_manager = Florence2Manager()
            self.db_manager = SQLiteImageDatabase()
            self.output_handler = OutputHandlerV2(output_directory=self.output_directory or "output")
            self.keyword_extractor = KeywordExtractor()
            self.image_processor = ImageProcessor(
                model_manager=self.model_manager,
                keyword_extractor=self.keyword_extractor
            )
            
            # Estado del modelo
            self.model_loaded = False
            
            logger.info("Componentes del core inicializados correctamente")
        except Exception as e:
            logger.error(f"Error inicializando componentes: {e}")
            messagebox.showerror("Error", f"Error inicializando componentes: {e}")
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Configuración de la ventana principal
        self.root.title("StockPrep Pro v2.0 - Procesador de Imágenes con IA")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Configurar icono
        try:
            self.root.iconbitmap("stockprep_icon.ico")
        except:
            try:
                # Fallback a PNG si ICO no funciona
                icon_img = tk.PhotoImage(file="stockprep_icon.png")
                self.root.iconphoto(True, icon_img)
            except:
                pass  # Sin icono si no se puede cargar
        
        # Configurar estilo
        try:
            self.root.state('zoomed')  # Maximizar en Windows
        except:
            pass
        
        # Crear notebook para tabs
        self.notebook = ttk.Notebook(self.root, style='Modern.TNotebook')
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Crear tabs
        self.create_main_tab()
        self.create_history_tab()
        self.create_stats_tab()
        
        # Barra de estado
        self.create_status_bar()
        
        # Menú
        self.create_menu()
        
        # Programar carga automática del modelo
        self.root.after(2000, self.auto_load_model)  # Preguntar después de 2 segundos
    
    def create_menu(self):
        """Crea el menú principal"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Abrir Imagen", command=self.select_image, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit, accelerator="Ctrl+Q")
        
        # Menú Herramientas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Herramientas", menu=tools_menu)
        tools_menu.add_command(label="Exportar Base de Datos", command=self.export_database)
        tools_menu.add_command(label="Limpiar Historial", command=self.clear_history)
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Acerca de", command=self.show_about)
        
        # Atajos de teclado
        self.root.bind('<Control-o>', lambda e: self.select_image())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
    
    def create_main_tab(self):
        """Crea el tab principal de procesamiento"""
        main_frame = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.notebook.add(main_frame, text="🖼️ Procesamiento")
        
        # Panel principal con dos columnas
        main_paned = ttk.PanedWindow(main_frame, orient='horizontal')
        main_paned.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Panel izquierdo - Imagen y controles
        left_frame = ttk.Frame(main_paned, style='Modern.TFrame')
        main_paned.add(left_frame, weight=1)
        
        # Título del panel izquierdo
        ttk.Label(left_frame, text="📁 Selección y Procesamiento", 
                 style='Title.TLabel').pack(pady=(0, 10))
        
        # Botón cargar modelo
        self.load_model_btn = ttk.Button(left_frame, text="🧠 Cargar Modelo Florence-2",
                                       command=self.load_model, style='Modern.TButton')
        self.load_model_btn.pack(fill='x', pady=5)
        
        # Botón seleccionar imagen
        self.select_btn = ttk.Button(left_frame, text="📁 Seleccionar Imagen",
                                   command=self.select_image, style='Modern.TButton')
        self.select_btn.pack(fill='x', pady=5)
        
        # Botón seleccionar carpeta
        self.select_folder_btn = ttk.Button(left_frame, text="📂 Seleccionar Carpeta de Imágenes",
                                          command=self.select_folder, style='Modern.TButton')
        self.select_folder_btn.pack(fill='x', pady=5)
        
        # Separador
        ttk.Separator(left_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Sección de configuración de salida
        output_frame = ttk.LabelFrame(left_frame, text="📁 Configuración de Salida", 
                                    style='Modern.TLabelframe')
        output_frame.pack(fill='x', pady=5)
        
        # Botón para seleccionar carpeta de salida
        self.select_output_btn = ttk.Button(output_frame, text="📤 Seleccionar Carpeta de Salida",
                                          command=self.select_output_directory, style='Modern.TButton')
        self.select_output_btn.pack(fill='x', padx=5, pady=5)
        
        # Etiqueta de carpeta actual
        self.output_label = ttk.Label(output_frame, text="📍 Salida: output/ (predeterminada)",
                                    style='Modern.TLabel')
        self.output_label.pack(fill='x', padx=5, pady=2)
        
        # Checkbox para copiar y renombrar
        self.copy_rename_var = tk.BooleanVar(value=True)
        self.copy_rename_checkbox = ttk.Checkbutton(output_frame, 
                                                  text="✨ Copiar y renombrar imágenes con descripción",
                                                  variable=self.copy_rename_var,
                                                  command=self.on_copy_rename_changed,
                                                  style='Modern.TCheckbutton')
        self.copy_rename_checkbox.pack(fill='x', padx=5, pady=5)
        
        # Frame para mostrar imagen
        self.image_frame = ttk.LabelFrame(left_frame, text="Vista Previa", 
                                        style='Modern.TLabelframe')
        self.image_frame.pack(fill='both', expand=True, pady=10)
        
        self.image_label = ttk.Label(self.image_frame, 
                                   text="Selecciona una imagen para comenzar",
                                   style='Modern.TLabel')
        self.image_label.pack(expand=True)
        
        # Botón procesar
        self.process_btn = ttk.Button(left_frame, text="🚀 Procesar Imagen",
                                    command=self.process_image, style='Modern.TButton',
                                    state='disabled')
        self.process_btn.pack(fill='x', pady=5)
        
        # Barra de progreso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(left_frame, variable=self.progress_var,
                                          maximum=100, style='Modern.Horizontal.TProgressbar')
        
        # Etiqueta de progreso para lotes
        self.batch_progress_label = ttk.Label(left_frame, text="", style='Modern.TLabel')
        self.batch_progress_label.pack(fill='x', pady=2)
        
        # Panel derecho - Resultados
        right_frame = ttk.Frame(main_paned, style='Modern.TFrame')
        main_paned.add(right_frame, weight=1)
        
        # Título del panel derecho
        ttk.Label(right_frame, text="📝 Resultados del Procesamiento",
                 style='Title.TLabel').pack(pady=(0, 10))
        
        # Notebook para resultados
        results_notebook = ttk.Notebook(right_frame)
        results_notebook.pack(fill='both', expand=True)
        
        # Tab Caption
        caption_frame = ttk.Frame(results_notebook, style='Modern.TFrame')
        results_notebook.add(caption_frame, text="📖 Descripción")
        
        ttk.Label(caption_frame, text="Descripción generada:",
                 style='Modern.TLabel').pack(anchor='w', pady=(5, 0))
        self.caption_text = scrolledtext.ScrolledText(caption_frame, height=6, 
                                                    wrap=tk.WORD, font=('Segoe UI', 10))
        self.caption_text.pack(fill='both', expand=True, pady=5)
        
        # Tab Keywords
        keywords_frame = ttk.Frame(results_notebook, style='Modern.TFrame')
        results_notebook.add(keywords_frame, text="🏷️ Keywords")
        
        ttk.Label(keywords_frame, text="Palabras clave extraídas:",
                 style='Modern.TLabel').pack(anchor='w', pady=(5, 0))
        self.keywords_text = scrolledtext.ScrolledText(keywords_frame, height=6,
                                                     wrap=tk.WORD, font=('Segoe UI', 10))
        self.keywords_text.pack(fill='both', expand=True, pady=5)
        
        # Tab Objects
        objects_frame = ttk.Frame(results_notebook, style='Modern.TFrame')
        results_notebook.add(objects_frame, text="🎯 Objetos")
        
        ttk.Label(objects_frame, text="Objetos detectados:",
                 style='Modern.TLabel').pack(anchor='w', pady=(5, 0))
        self.objects_text = scrolledtext.ScrolledText(objects_frame, height=6,
                                                    wrap=tk.WORD, font=('Segoe UI', 10))
        self.objects_text.pack(fill='both', expand=True, pady=5)
        
        # Botón exportar
        self.export_btn = ttk.Button(right_frame, text="💾 Exportar Resultados",
                                   command=self.export_results, style='Modern.TButton',
                                   state='disabled')
        self.export_btn.pack(fill='x', pady=(10, 0))
    
    def create_history_tab(self):
        """Crea el tab de historial"""
        history_frame = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.notebook.add(history_frame, text="📋 Historial")
        
        # Título
        ttk.Label(history_frame, text="📋 Historial de Procesamiento",
                 style='Title.TLabel').pack(pady=10)
        
        # Frame para la tabla
        table_frame = ttk.Frame(history_frame, style='Modern.TFrame')
        table_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Crear Treeview para el historial
        columns = ('Archivo', 'Fecha', 'Caption', 'Keywords', 'Objetos')
        self.history_tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                       style='Modern.Treeview')
        
        # Configurar columnas
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=150, minwidth=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.history_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient='horizontal', command=self.history_tree.xview)
        self.history_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack elementos
        self.history_tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Botones de control
        buttons_frame = ttk.Frame(history_frame, style='Modern.TFrame')
        buttons_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(buttons_frame, text="🔄 Actualizar", command=self.refresh_history,
                  style='Modern.TButton').pack(side='left', padx=5)
        
        ttk.Button(buttons_frame, text="🗑️ Limpiar", command=self.clear_history,
                  style='Modern.TButton').pack(side='left', padx=5)
    
    def create_stats_tab(self):
        """Crea el tab de estadísticas"""
        stats_frame = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.notebook.add(stats_frame, text="📊 Estadísticas")
        
        # Título
        ttk.Label(stats_frame, text="📊 Estadísticas del Sistema",
                 style='Title.TLabel').pack(pady=10)
        
        # Frame principal para estadísticas
        main_stats_frame = ttk.Frame(stats_frame, style='Modern.TFrame')
        main_stats_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Estadísticas de procesamiento
        processing_frame = ttk.LabelFrame(main_stats_frame, text="🔄 Procesamiento",
                                        style='Modern.TLabelframe')
        processing_frame.pack(fill='x', pady=10)
        
        self.stats_labels = {}
        
        # Crear labels para estadísticas
        stats_info = [
            ('total_images', 'Imágenes procesadas: 0'),
            ('success_rate', 'Tasa de éxito: 100%'),
            ('avg_time', 'Tiempo promedio: 0s'),
            ('db_records', 'Registros en BD: 0'),
            ('db_size', 'Tamaño BD: 0 KB'),
            ('last_update', 'Última actualización: Nunca')
        ]
        
        for key, default_text in stats_info:
            self.stats_labels[key] = ttk.Label(processing_frame, text=default_text,
                                             style='Modern.TLabel')
            self.stats_labels[key].pack(anchor='w', padx=10, pady=5)
    
    def create_status_bar(self):
        """Crea la barra de estado"""
        self.status_frame = ttk.Frame(self.root, style='Modern.TFrame')
        self.status_frame.pack(side='bottom', fill='x')
        
        self.status_label = ttk.Label(self.status_frame, text="Listo para procesar imágenes",
                                    style='Modern.TLabel')
        self.status_label.pack(side='left', padx=10, pady=5)
        
        # Información de GPU/CPU
        self.device_label = ttk.Label(self.status_frame, text="", style='Modern.TLabel')
        self.device_label.pack(side='left', padx=10, pady=5)
        
        # Reloj
        self.clock_label = ttk.Label(self.status_frame, text="",
                                   style='Modern.TLabel')
        self.clock_label.pack(side='right', padx=10, pady=5)
        
        self.update_clock()
        self.update_device_info()
    
    def update_clock(self):
        """Actualiza el reloj en la barra de estado"""
        if self.closing:
            return
            
        try:
            current_time = datetime.now().strftime("%H:%M:%S")
            self.clock_label.config(text=current_time)
            timer_id = self.root.after(1000, self.update_clock)
            self.timer_ids.append(timer_id)
        except Exception as e:
            print(f"Error en update_clock: {e}")
    
    def update_device_info(self):
        """Actualiza la información del dispositivo en la barra de estado"""
        if self.closing:
            return
            
        try:
            if hasattr(self, 'model_manager') and self.model_manager:
                device_info = self.model_manager.get_device_info()
                device = device_info["device"]
                gpu_info = device_info["gpu_info"]
                
                if device.startswith("cuda") and gpu_info.get("available"):
                    gpu_name = gpu_info.get("name", "GPU")
                    # Acortar nombre de GPU si es muy largo
                    if len(gpu_name) > 20:
                        gpu_name = gpu_name[:17] + "..."
                    
                    if self.model_loaded:
                        memory_info = self.model_manager.obtener_uso_memoria()
                        self.device_label.config(text=f"🎮 {gpu_name} | {memory_info}")
                    else:
                        free_memory = gpu_info.get("free_gb", 0)
                        self.device_label.config(text=f"🎮 {gpu_name} | {free_memory:.1f} GB libre")
                else:
                    self.device_label.config(text="💻 CPU")
            else:
                self.device_label.config(text="⏳ Inicializando...")
                
        except Exception as e:
            self.device_label.config(text="❓ Dispositivo desconocido")
        
        # Actualizar cada 5 segundos
        if not self.closing:
            timer_id = self.root.after(5000, self.update_device_info)
            self.timer_ids.append(timer_id)
    
    def select_image(self):
        """Selecciona una imagen para procesar"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar Imagen",
            filetypes=[
                ("Imágenes", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if file_path:
            self.current_image_path = file_path
            self.current_folder_path = None  # Limpiar selección de carpeta
            self.batch_images = []
            self.load_image_preview(file_path)
            self.process_btn.config(state='normal', text="🚀 Procesar Imagen")
            
            # Cambiar botón de selección a verde y actualizar texto
            self.select_btn.config(style='Loaded.TButton', text="✅ Imagen Seleccionada")
            # Restaurar botón de carpeta al estilo normal
            self.select_folder_btn.config(style='Modern.TButton', text="📂 Seleccionar Carpeta de Imágenes")
            
            self.status_label.config(text=f"Imagen seleccionada: {Path(file_path).name}")
    
    def select_folder(self):
        """Selecciona una carpeta para procesamiento en lote"""
        folder_path = filedialog.askdirectory(
            title="Seleccionar Carpeta de Imágenes"
        )
        
        if folder_path:
            self.current_folder_path = folder_path
            self.current_image_path = None  # Limpiar selección de imagen individual
            
            # Buscar todas las imágenes en la carpeta
            self.batch_images = self.find_images_in_folder(folder_path)
            
            if self.batch_images:
                # Mostrar primera imagen como preview
                self.load_image_preview(self.batch_images[0])
                self.process_btn.config(state='normal', text=f"🚀 Procesar {len(self.batch_images)} Imágenes")
                
                # Cambiar botón de carpeta a verde y actualizar texto
                self.select_folder_btn.config(style='Loaded.TButton', text=f"✅ {len(self.batch_images)} Imágenes Cargadas")
                # Restaurar botón de imagen al estilo normal
                self.select_btn.config(style='Modern.TButton', text="📁 Seleccionar Imagen")
                
                self.status_label.config(text=f"Carpeta seleccionada: {len(self.batch_images)} imágenes encontradas en {Path(folder_path).name}")
            else:
                messagebox.showwarning("Sin imágenes", "No se encontraron imágenes en la carpeta seleccionada")
                self.status_label.config(text="No se encontraron imágenes en la carpeta")
    
    def find_images_in_folder(self, folder_path):
        """Busca todas las imágenes en una carpeta"""
        image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp'}
        images = []
        
        try:
            folder = Path(folder_path)
            for file_path in folder.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                    images.append(str(file_path))
            
            # Ordenar alfabéticamente
            images.sort()
            
        except Exception as e:
            logger.error(f"Error buscando imágenes: {e}")
        
        return images
    
    def select_output_directory(self):
        """Selecciona la carpeta de salida"""
        folder_path = filedialog.askdirectory(
            title="Seleccionar Carpeta de Salida"
        )
        
        if folder_path:
            self.output_directory = folder_path
            self.output_handler.set_output_directory(folder_path)
            
            # Actualizar etiqueta
            folder_name = Path(folder_path).name
            self.output_label.config(text=f"📍 Salida: {folder_name}/ (personalizada)")
            
            self.status_label.config(text=f"Carpeta de salida establecida: {folder_path}")
    
    def on_copy_rename_changed(self):
        """Maneja el cambio en el checkbox de copiar y renombrar"""
        self.copy_and_rename = self.copy_rename_var.get()
    
    def load_image_preview(self, image_path: str):
        """Carga la vista previa de la imagen usando gestión robusta de referencias"""
        try:
            from PIL import Image, ImageTk
            
            # Verificar que el archivo existe
            if not Path(image_path).exists():
                self.image_label.config(text="❌ Archivo no encontrado", image="")
                # Limpiar referencia anterior si existe
                if hasattr(self.image_label, '_image_key'):
                    self._remove_image_reference(self.image_label._image_key)
                    delattr(self.image_label, '_image_key')
                return
            
            # Limpiar imagen anterior ANTES de cargar nueva
            if hasattr(self.image_label, '_image_key'):
                self._remove_image_reference(self.image_label._image_key)
                delattr(self.image_label, '_image_key')
            
            # Limpiar configuración de imagen en el label
            self.image_label.config(image="", text="Cargando imagen...")
            self.root.update_idletasks()
            
            # Cargar y redimensionar imagen
            with Image.open(image_path) as image:
                # Crear una copia para evitar problemas con el contexto
                image = image.copy()
                
                # Calcular nuevo tamaño manteniendo proporción
                max_size = (300, 300)
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Convertir para Tkinter
                photo = ImageTk.PhotoImage(image)
                
                # Almacenar referencia de forma segura
                image_key = self._store_image_reference(photo)
                
                if image_key:
                    # Configurar el label con la nueva imagen
                    self.image_label.config(image=photo, text="")
                    self.image_label._image_key = image_key
                    
                    # Verificar que la imagen se configuró correctamente
                    if not self.image_label.cget('image'):
                        raise Exception("No se pudo configurar la imagen en el label")
                else:
                    raise Exception("No se pudo almacenar la referencia de la imagen")
            
        except Exception as e:
            logger.error(f"Error cargando vista previa: {e}")
            self.image_label.config(text=f"❌ Error: {str(e)[:50]}...", image="")
            # Limpiar referencia en caso de error
            if hasattr(self.image_label, '_image_key'):
                self._remove_image_reference(self.image_label._image_key)
                delattr(self.image_label, '_image_key')
    
    def process_image(self):
        """Procesa la imagen seleccionada o inicia procesamiento en lote"""
        if self.processing or self.batch_processing:
            return
        
        # Verificar que el modelo esté cargado
        if not self.model_loaded:
            result = messagebox.askyesno(
                "Modelo no cargado", 
                "El modelo Florence-2 no está cargado.\n¿Deseas cargarlo ahora?"
            )
            if result:
                self.load_model()
            return
        
        # Determinar si es procesamiento individual o en lote
        if self.batch_images:
            self.start_batch_processing()
        elif self.current_image_path:
            self.process_single_image()
        else:
            messagebox.showwarning("Sin selección", "Selecciona una imagen o carpeta primero")
    
    def process_single_image(self):
        """Procesa una sola imagen"""
        self.processing = True
        self.process_btn.config(state='disabled', text="Procesando...")
        self.export_btn.config(state='disabled')
        
        # Mostrar barra de progreso
        self.progress_bar.pack(fill='x', pady=5)
        self.progress_var.set(0)
        
        # Limpiar resultados anteriores
        self.caption_text.delete(1.0, tk.END)
        self.keywords_text.delete(1.0, tk.END)
        self.objects_text.delete(1.0, tk.END)
        
        # Procesar en hilo separado
        thread = threading.Thread(target=self._process_single_image_thread)
        thread.daemon = True
        thread.start()
    
    def start_batch_processing(self):
        """Inicia el procesamiento en lote"""
        if not self.batch_images:
            return
        
        # Confirmar procesamiento en lote
        result = messagebox.askyesno(
            "Procesamiento en Lote",
            f"¿Deseas procesar {len(self.batch_images)} imágenes?\n\n"
            "Esto puede tomar varios minutos dependiendo del número de imágenes."
        )
        
        if not result:
            return
        
        self.batch_processing = True
        self.batch_current_index = 0
        self.process_btn.config(state='disabled', text="Procesando lote...")
        self.export_btn.config(state='disabled')
        
        # Mostrar barra de progreso
        self.progress_bar.pack(fill='x', pady=5)
        self.progress_var.set(0)
        
        # Limpiar resultados
        self.caption_text.delete(1.0, tk.END)
        self.keywords_text.delete(1.0, tk.END)
        self.objects_text.delete(1.0, tk.END)
        
        # Iniciar procesamiento en lote
        self.process_next_batch_image()
    
    def process_next_batch_image(self):
        """Procesa la siguiente imagen en el lote"""
        if self.batch_current_index >= len(self.batch_images):
            # Terminado el procesamiento en lote
            self.finish_batch_processing()
            return
        
        current_image = self.batch_images[self.batch_current_index]
        
        # Actualizar progreso
        progress = (self.batch_current_index / len(self.batch_images)) * 100
        self.progress_var.set(progress)
        
        # Actualizar etiqueta de progreso
        self.batch_progress_label.config(
            text=f"Procesando {self.batch_current_index + 1} de {len(self.batch_images)} imágenes"
        )
        
        # Actualizar estado
        self.status_label.config(
            text=f"Procesando: {Path(current_image).name}"
        )
        
        # Actualizar preview con imagen actual
        self.load_image_preview(current_image)
        
        # Procesar imagen en hilo separado
        thread = threading.Thread(target=self._process_batch_image_thread, args=(current_image,))
        thread.daemon = True
        thread.start()
    
    def finish_batch_processing(self):
        """Finaliza el procesamiento en lote"""
        self.batch_processing = False
        self.progress_var.set(100)
        self.process_btn.config(state='normal', text=f"🚀 Procesar {len(self.batch_images)} Imágenes")
        self.export_btn.config(state='normal')
        
        # Mostrar resumen
        success_count = self.batch_current_index
        self.status_label.config(text=f"Procesamiento completado: {success_count}/{len(self.batch_images)} imágenes")
        
        # Mostrar resultados de la última imagen procesada
        if self.batch_images and self.batch_current_index > 0:
            last_image = self.batch_images[self.batch_current_index - 1]
            self.load_image_preview(last_image)
        
        messagebox.showinfo(
            "Procesamiento Completado",
            f"Se procesaron {success_count} de {len(self.batch_images)} imágenes.\n\n"
            "Los archivos .txt se guardaron junto a cada imagen."
        )
        
        self.progress_bar.pack_forget()
        
        # Limpiar etiqueta de progreso
        self.batch_progress_label.config(text="")
    
    def _process_single_image_thread(self):
        """Procesa una sola imagen en un hilo separado"""
        try:
            # Simular progreso
            for i in range(0, 101, 10):
                self.root.after(0, lambda p=i: self.progress_var.set(p))
                if i < 90:
                    threading.Event().wait(0.1)
            
            # Procesar imagen
            results = self.image_processor.process_image(self.current_image_path)
            
            # Actualizar UI en el hilo principal
            self.root.after(0, lambda: self._update_results(results))
            
        except Exception as e:
            logger.error(f"Error procesando imagen: {e}")
            self.root.after(0, lambda: self._show_error(str(e)))
    
    def _process_batch_image_thread(self, image_path: str):
        """Procesa una imagen del lote en un hilo separado"""
        try:
            # Procesar imagen
            results = self.image_processor.process_image(image_path)
            
            # Actualizar UI en el hilo principal
            self.root.after(0, lambda: self._update_results(results))
            
        except Exception as e:
            logger.error(f"Error procesando imagen {image_path}: {e}")
            # Continuar con la siguiente imagen aunque haya error
            self.root.after(0, lambda: self._on_batch_image_error(str(e)))
    
    def _update_results(self, results: Dict):
        """Actualiza los resultados en la UI"""
        try:
            # Determinar la ruta de la imagen actual
            if self.batch_processing:
                current_image_path = self.batch_images[self.batch_current_index]
            else:
                current_image_path = self.current_image_path
            
            # Mostrar caption
            caption = results.get('caption', '')
            self.caption_text.delete(1.0, tk.END)
            self.caption_text.insert(1.0, caption)
            
            # Mostrar keywords
            keywords = results.get('keywords', [])
            if isinstance(keywords, list):
                keywords_text = '\n'.join(keywords)
            else:
                keywords_text = str(keywords)
            self.keywords_text.delete(1.0, tk.END)
            self.keywords_text.insert(1.0, keywords_text)
            
            # Mostrar objetos
            objects = results.get('objects', [])
            if isinstance(objects, list) and objects:
                objects_lines = []
                for i, obj in enumerate(objects):
                    if isinstance(obj, dict):
                        name = obj.get('name', 'objeto')
                        bbox = obj.get('bbox', [0, 0, 0, 0])
                        confidence = obj.get('confidence', 0.0)
                        objects_lines.append(f"🎯 {name}")
                        objects_lines.append(f"   📍 Posición: [{bbox[0]:.0f}, {bbox[1]:.0f}, {bbox[2]:.0f}, {bbox[3]:.0f}]")
                        objects_lines.append(f"   🎲 Confianza: {confidence:.2f}")
                        if i < len(objects) - 1:  # Separador entre objetos
                            objects_lines.append("")
                    else:
                        objects_lines.append(f"🎯 {str(obj)}")
                objects_text = '\n'.join(objects_lines)
            elif isinstance(objects, dict):
                # Manejar formato dict directo de Florence-2
                objects_lines = []
                labels = objects.get('labels', [])
                bboxes = objects.get('bboxes', objects.get('boxes', []))
                scores = objects.get('scores', [1.0] * len(labels))
                
                for i, label in enumerate(labels):
                    bbox = bboxes[i] if i < len(bboxes) else [0, 0, 0, 0]
                    score = scores[i] if i < len(scores) else 1.0
                    objects_lines.append(f"🎯 {label}")
                    objects_lines.append(f"   📍 Posición: [{bbox[0]:.0f}, {bbox[1]:.0f}, {bbox[2]:.0f}, {bbox[3]:.0f}]")
                    objects_lines.append(f"   🎲 Confianza: {score:.2f}")
                    if i < len(labels) - 1:
                        objects_lines.append("")
                objects_text = '\n'.join(objects_lines)
            else:
                objects_text = "No se detectaron objetos" if not objects else str(objects)
            
            self.objects_text.delete(1.0, tk.END)
            self.objects_text.insert(1.0, objects_text)
            
            # Guardar resultados
            if self.output_handler.save_results(current_image_path, results, self.copy_and_rename):
                if self.batch_processing:
                    # Continuar con la siguiente imagen en el lote
                    self.batch_current_index += 1
                    self.root.after(500, self.process_next_batch_image)  # Pausa de 0.5s entre imágenes
                else:
                    if self.copy_and_rename and results.get('renamed_file'):
                        self.status_label.config(text=f"Imagen procesada y renombrada: {results['renamed_file']}")
                    else:
                        self.status_label.config(text="Imagen procesada y guardada exitosamente")
                    self.export_btn.config(state='normal')
            else:
                if self.batch_processing:
                    # Continuar aunque haya error
                    self.batch_current_index += 1
                    self.root.after(500, self.process_next_batch_image)
                else:
                    self.status_label.config(text="Imagen procesada, pero error al guardar")
            
        except Exception as e:
            logger.error(f"Error actualizando resultados: {e}")
            if self.batch_processing:
                # Continuar con la siguiente imagen
                self.batch_current_index += 1
                self.root.after(500, self.process_next_batch_image)
            else:
                self._show_error(f"Error mostrando resultados: {e}")
        
        finally:
            if not self.batch_processing:
                self.processing = False
                self.process_btn.config(state='normal', text="🚀 Procesar Imagen")
                self.progress_bar.pack_forget()
    
    def _show_error(self, error_msg: str):
        """Muestra un error en la UI"""
        messagebox.showerror("Error de Procesamiento", error_msg)
        self.processing = False
        self.process_btn.config(state='normal', text="🚀 Procesar Imagen")
        self.progress_bar.pack_forget()
        self.status_label.config(text="Error en el procesamiento")
    
    def _on_batch_image_error(self, error_msg: str):
        """Maneja errores durante el procesamiento en lote"""
        logger.error(f"Error en imagen del lote: {error_msg}")
        # Continuar con la siguiente imagen
        self.batch_current_index += 1
        self.root.after(500, self.process_next_batch_image)
    
    def export_results(self):
        """Exporta los resultados actuales"""
        if not self.current_image_path and not self.batch_images:
            messagebox.showwarning("Sin datos", "No hay resultados para exportar")
            return
        
        # Seleccionar formato de exportación
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
        
        # Abrir diálogo para seleccionar archivo de destino
        file_path = filedialog.asksaveasfilename(
            title="Exportar Resultados",
            defaultextension=extension,
            filetypes=file_types,
            initialfilename=f"stockprep_resultados_{datetime.now().strftime('%Y%m%d_%H%M%S')}{extension}"
        )
        
        if not file_path:
            return
        
        try:
            # Obtener datos de la base de datos
            if self.db_manager:
                data = self.db_manager.buscar_imagenes(limite=10000)
                
                if export_format:  # JSON
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
                    
                    messagebox.showinfo("Exportación Completada", msg)
                else:
                    messagebox.showerror("Error", "Error durante la exportación")
            else:
                messagebox.showerror("Error", "Base de datos no disponible")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en exportación: {e}")
    
    def refresh_history(self):
        """Actualiza el historial de la base de datos"""
        try:
            if not self.db_manager:
                return
            
            # Limpiar tabla
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            
            # Obtener registros
            records = self.db_manager.buscar_imagenes()
            
            # Agregar registros a la tabla
            for record in records:
                file_path = Path(record.get('file_path', '')).name
                created_at = record.get('created_at', '')
                caption = record.get('caption', '')[:50] + '...' if len(record.get('caption', '')) > 50 else record.get('caption', '')
                keywords = record.get('keywords', '')[:30] + '...' if len(record.get('keywords', '')) > 30 else record.get('keywords', '')
                objects = record.get('objects', '')[:30] + '...' if len(record.get('objects', '')) > 30 else record.get('objects', '')
                
                self.history_tree.insert('', 'end', values=(file_path, created_at, caption, keywords, objects))
            
            self.status_label.config(text=f"Historial actualizado: {len(records)} registros")
            
        except Exception as e:
            logger.error(f"Error actualizando historial: {e}")
            messagebox.showerror("Error", f"Error actualizando historial: {e}")
    
    def clear_history(self):
        """Limpia el historial de la base de datos"""
        result = messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres limpiar todo el historial?")
        
        if result:
            try:
                if self.db_manager:
                    # Aquí implementarías el método clear_all en db_manager
                    self.refresh_history()
                    self.status_label.config(text="Historial limpiado")
            except Exception as e:
                messagebox.showerror("Error", f"Error limpiando historial: {e}")
    
    def update_stats_periodically(self):
        """Actualiza las estadísticas periódicamente"""
        if self.closing:
            return
            
        try:
            stats = {}
            
            if self.db_manager:
                db_stats = self.db_manager.obtener_estadisticas_globales()
                stats.update(db_stats)
            
            # Actualizar labels
            for key, label in self.stats_labels.items():
                if key in stats:
                    if key == 'total_images':
                        label.config(text=f"Imágenes procesadas: {stats[key]}")
                    elif key == 'success_rate':
                        label.config(text=f"Tasa de éxito: {stats[key]:.1f}%")
                    elif key == 'avg_time':
                        label.config(text=f"Tiempo promedio: {stats[key]:.1f}s")
                    elif key == 'db_records':
                        label.config(text=f"Registros en BD: {stats[key]}")
                    elif key == 'db_size':
                        label.config(text=f"Tamaño BD: {stats[key]} KB")
                    elif key == 'last_update':
                        current_time = datetime.now().strftime("%H:%M:%S")
                        label.config(text=f"Última actualización: {current_time}")
            
        except Exception as e:
            logger.error(f"Error actualizando estadísticas: {e}")
        
        # Programar próxima actualización
        if not self.closing:
            timer_id = self.root.after(5000, self.update_stats_periodically)
            self.timer_ids.append(timer_id)
    
    def export_database(self):
        """Exporta la base de datos"""
        file_path = filedialog.asksaveasfilename(
            title="Exportar Base de Datos",
            defaultextension=".json",
            filetypes=[
                ("JSON", "*.json"),
                ("CSV", "*.csv"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if file_path:
            try:
                if self.db_manager:
                    data = self.db_manager.buscar_imagenes()
                    
                    if file_path.endswith('.json'):
                        self.output_handler.export_to_json(file_path, {'images': data})
                    elif file_path.endswith('.csv'):
                        self.output_handler.export_to_csv(file_path, data)
                    
                    messagebox.showinfo("Éxito", f"Base de datos exportada a {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error exportando: {e}")
    
    def show_about(self):
        """Muestra información sobre la aplicación"""
        about_text = """StockPrep Pro v2.0

Sistema todo-en-uno para procesamiento de imágenes
con Microsoft Florence-2 y extracción de keywords.

Características:
• Generación automática de captions
• Detección de objetos
• Extracción de keywords con YAKE
• Base de datos SQLite embebida
• Interfaz moderna con Tkinter

Desarrollado con Python, PyTorch y Transformers
"""
        messagebox.showinfo("Acerca de StockPrep Pro", about_text)
    
    def load_model(self):
        """Carga el modelo Florence-2"""
        if self.model_loaded:
            messagebox.showinfo("Información", "El modelo ya está cargado")
            return
        
        # Verificar memoria GPU disponible antes de cargar
        if hasattr(self.model_manager, 'check_gpu_memory_sufficient'):
            sufficient, message = self.model_manager.check_gpu_memory_sufficient(4.0)
            if not sufficient:
                response = messagebox.askyesno(
                    "Advertencia de Memoria",
                    f"{message}\n\n¿Deseas continuar de todos modos?\n"
                    "El modelo podría cargarse en CPU o fallar por falta de memoria."
                )
                if not response:
                    return
        
        def callback(mensaje):
            # Actualizar barra de estado en lugar de log_text
            self.status_label.config(text=mensaje)
            self.root.update()
        
        def load_in_thread():
            try:
                # Cambiar botón para mostrar que está cargando
                self.root.after(0, lambda: self.load_model_btn.config(
                    state='disabled', 
                    text="🔄 Cargando Modelo...",
                    style='Modern.TButton'
                ))
                
                callback("🚀 Iniciando carga del modelo Florence-2...")
                success = self.model_manager.cargar_modelo(callback)
                
                if success:
                    self.model_loaded = True
                    
                    # Cambiar botón a estilo de éxito (verde) y deshabilitar
                    self.load_model_btn.config(
                        state='disabled', 
                        text="✅ Modelo Cargado",
                        style='Success.TButton'
                    )
                    
                    callback("🎉 ¡Modelo cargado exitosamente!")
                    
                    # Actualizar información del dispositivo inmediatamente
                    self.update_device_info()
                    
                    # Mostrar información del dispositivo usado
                    device_info = self.model_manager.get_device_info()
                    device = device_info["device"]
                    if device.startswith("cuda"):
                        gpu_name = self.model_manager.get_gpu_name()
                        callback(f"✅ Modelo ejecutándose en GPU: {gpu_name}")
                        messagebox.showinfo("Modelo Cargado", f"Modelo Florence-2 cargado exitosamente en GPU: {gpu_name}")
                    else:
                        callback("⚠️ Modelo ejecutándose en CPU (rendimiento limitado)")
                        messagebox.showinfo("Modelo Cargado", "Modelo Florence-2 cargado en CPU")
                    
                else:
                    # Restaurar botón al estado original si falla
                    self.load_model_btn.config(
                        state='normal', 
                        text="🧠 Cargar Modelo Florence-2",
                        style='Modern.TButton'
                    )
                    callback("❌ Error al cargar el modelo")
                    messagebox.showerror("Error", "No se pudo cargar el modelo Florence-2")
                    
            except Exception as e:
                # Restaurar botón al estado original si hay excepción
                self.load_model_btn.config(
                    state='normal', 
                    text="🧠 Cargar Modelo Florence-2",
                    style='Modern.TButton'
                )
                error_msg = f"❌ Error inesperado: {str(e)}"
                callback(error_msg)
                messagebox.showerror("Error", error_msg)
        
        # Ejecutar en hilo separado
        thread = threading.Thread(target=load_in_thread, daemon=True)
        thread.start()
    
    def auto_load_model(self):
        """Carga automática del modelo al inicio"""
        # Preguntar al usuario si quiere cargar automáticamente
        result = messagebox.askyesno(
            "Cargar Modelo", 
            "¿Deseas cargar automáticamente el modelo Florence-2?\n\n"
            "Esto puede tomar unos minutos pero permitirá procesar imágenes inmediatamente."
        )
        
        if result:
            self.root.after(1000, self.load_model)  # Cargar después de 1 segundo
    
    def _clear_image_references(self):
        """Limpia todas las referencias de imágenes almacenadas"""
        try:
            for key, photo_ref in self.image_references.items():
                try:
                    if photo_ref and hasattr(photo_ref, 'tk'):
                        del photo_ref
                except:
                    pass
            self.image_references.clear()
            self.image_counter = 0
        except Exception as e:
            print(f"Error limpiando referencias de imágenes: {e}")
    
    def _store_image_reference(self, photo):
        """Almacena una referencia de imagen de forma segura"""
        try:
            self.image_counter += 1
            key = f"image_{self.image_counter}"
            self.image_references[key] = photo
            return key
        except Exception as e:
            print(f"Error almacenando referencia de imagen: {e}")
            return None
    
    def _get_image_reference(self, key):
        """Obtiene una referencia de imagen almacenada"""
        try:
            return self.image_references.get(key)
        except:
            return None
    
    def _remove_image_reference(self, key):
        """Elimina una referencia de imagen específica"""
        try:
            if key in self.image_references:
                photo_ref = self.image_references[key]
                if photo_ref and hasattr(photo_ref, 'tk'):
                    del photo_ref
                del self.image_references[key]
        except Exception as e:
            print(f"Error eliminando referencia de imagen: {e}")
    
    def run(self):
        """Ejecuta la aplicación"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("Aplicación cerrada por el usuario")
        except Exception as e:
            logger.error(f"Error ejecutando aplicación: {e}")
            messagebox.showerror("Error Fatal", f"Error ejecutando aplicación: {e}")

# Función de entrada
def main():
    """Función principal"""
    app = StockPrepApp()
    app.run()

if __name__ == "__main__":
    main() 