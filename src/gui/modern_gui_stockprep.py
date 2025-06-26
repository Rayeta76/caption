"""
Interfaz gráfica moderna para StockPrep
Con diseño colorido y contemporáneo
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
from pathlib import Path
import os
from datetime import datetime
import json

# Importar módulos locales
from core.model_manager import Florence2Manager
from core.image_processor import ImageProcessor
from core.database_manager import ImageDatabase
from utils.translator import Translator
from io.report_generator import ReportGenerator
from utils.metrics import MetricasProcessor

class StockPrepApp:
    """Interfaz gráfica moderna con diseño colorido"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("StockPrep Pro - Florence-2 AI")
        self.root.geometry("1200x800")
        
        # Colores modernos (paleta profesional)
        self.colors = {
            'bg_primary': '#1e1e2e',        # Fondo principal oscuro
            'bg_secondary': '#2a2a3e',      # Fondo secundario
            'bg_card': '#323244',           # Fondo de tarjetas
            'blue': '#2563eb',              # Azul para acciones
            'accent': '#7c3aed',            # Morado principal
            'accent_hover': '#9333ea',      # Morado hover
            'success': '#10b981',           # Verde éxito
            'warning': '#f59e0b',           # Amarillo advertencia
            'danger': '#ef4444',            # Rojo error
            'text_primary': '#f8f8f2',      # Texto principal
            'text_secondary': '#a0a0c0',    # Texto secundario
            'border': '#44475a',            # Bordes
            'gradient_start': '#667eea',    # Gradiente inicio
            'gradient_end': '#764ba2'       # Gradiente fin
        }
        
        # Configurar estilo
        self.setup_styles()
        
        # Variables
        self.setup_variables()
        
        # Componentes
        self.model_manager = None
        self.processor = None
        self.database = ImageDatabase()
        self.translator = Translator()
        self.metrics = MetricasProcessor()
        
        # Crear interfaz
        self.create_widgets()
        
        # Centrar ventana
        self.center_window()
        
        # Iniciar verificación de mensajes
        self.check_queue()
    
    def setup_styles(self):
        """Configura los estilos modernos de ttk"""
        self.style = ttk.Style()
        
        # Configurar el tema base
        self.root.configure(bg=self.colors['bg_primary'])
        
        # Estilo para frames
        self.style.configure(
            'Modern.TFrame',
            background=self.colors['bg_primary'],
            relief='flat'
        )
        
        # Estilo para labels
        self.style.configure(
            'Modern.TLabel',
            background=self.colors['bg_primary'],
            foreground=self.colors['text_primary'],
            font=('Segoe UI', 10)
        )
        
        # Estilo para títulos
        self.style.configure(
            'Title.TLabel',
            background=self.colors['bg_primary'],
            foreground=self.colors['text_primary'],
            font=('Segoe UI', 24, 'bold')
        )
        
        # Estilo para subtítulos
        self.style.configure(
            'Subtitle.TLabel',
            background=self.colors['bg_primary'],
            foreground=self.colors['text_secondary'],
            font=('Segoe UI', 12)
        )
        
        # Estilo para botones modernos
        self.style.configure(
            'Modern.TButton',
            background=self.colors['accent'],
            foreground='white',
            borderwidth=0,
            focuscolor='none',
            font=('Segoe UI', 11, 'bold')
        )
        
        self.style.map(
            'Modern.TButton',
            background=[('active', self.colors['accent_hover'])],
            foreground=[('active', 'white')]
        )
        
        # Estilo para progreso
        self.style.configure(
            'Modern.Horizontal.TProgressbar',
            background=self.colors['accent'],
            troughcolor=self.colors['bg_card'],
            borderwidth=0,
            lightcolor=self.colors['accent'],
            darkcolor=self.colors['accent']
        )
    
    def setup_variables(self):
        """Inicializa las variables de la aplicación"""
        self.carpeta_entrada = tk.StringVar()
        self.carpeta_salida = tk.StringVar(value=str(Path.cwd() / "salida"))
        self.formato_salida = tk.StringVar(value="JSON")
        self.idioma_actual = tk.StringVar(value="es")
        self.incluir_objetos = tk.BooleanVar(value=True)
        self.renombrar_archivos = tk.BooleanVar(value=True)
        self.generar_txt = tk.BooleanVar(value=True)
        self.generar_informe = tk.BooleanVar(value=True)
        
        self.queue = queue.Queue()
        self.procesando = False
        self.modelo_cargado = False
    
    def create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        # Frame principal con padding
        main_container = ttk.Frame(self.root, style='Modern.TFrame', padding="20")
        main_container.grid(row=0, column=0, sticky="nsew")
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        
        # Header con gradiente (simulado)
        self.create_header(main_container)
        
        # Área principal con 2 columnas
        content_frame = ttk.Frame(main_container, style='Modern.TFrame')
        content_frame.grid(row=1, column=0, sticky="nsew", pady=(20, 0))
        content_frame.columnconfigure(0, weight=3)
        content_frame.columnconfigure(1, weight=2)
        main_container.rowconfigure(1, weight=1)
        
        # Panel izquierdo
        left_panel = ttk.Frame(content_frame, style='Modern.TFrame')
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Panel derecho
        right_panel = ttk.Frame(content_frame, style='Modern.TFrame')
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Crear secciones
        self.create_folder_section(left_panel)
        self.create_options_section(left_panel)
        self.create_action_buttons(left_panel)
        self.create_progress_section(left_panel)
        
        self.create_stats_section(right_panel)
        self.create_log_section(right_panel)
        
        # Footer
        self.create_footer(main_container)
    
    def create_header(self, parent):
        """Crea el header con diseño moderno"""
        header_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], height=100)
        header_frame.grid(row=0, column=0, sticky="ew", padx=-20, pady=(-20, 0))
        header_frame.grid_propagate(False)
        
        # Contenido del header
        header_content = tk.Frame(header_frame, bg=self.colors['bg_secondary'])
        header_content.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo/Título
        title_label = tk.Label(
            header_content,
            text="StockPrep Pro",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary']
        )
        title_label.pack()
        
        # Subtítulo
        subtitle_label = tk.Label(
            header_content,
            text="Procesamiento Inteligente de Imágenes con Florence-2 AI",
            font=('Segoe UI', 14),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_secondary']
        )
        subtitle_label.pack()
        
        # Selector de idioma
        lang_frame = tk.Frame(header_frame, bg=self.colors['bg_secondary'])
        lang_frame.place(relx=0.95, rely=0.5, anchor="e")
        
        languages = [("🇪🇸 ES", "es"), ("🇬🇧 EN", "en"), ("🇫🇷 FR", "fr")]
        for text, lang in languages:
            btn = self.create_modern_button(
                lang_frame, text, 
                lambda l=lang: self.cambiar_idioma(l),
                width=8, small=True
            )
            btn.pack(side=tk.LEFT, padx=2)
    
    def create_folder_section(self, parent):
        """Crea la sección de selección de carpetas"""
        # Card container
        card = self.create_card(parent, "Carpetas de Trabajo")
        card.pack(fill="x", pady=(0, 15))
        
        # Carpeta entrada
        input_frame = tk.Frame(card, bg=self.colors['bg_card'])
        input_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(
            input_frame,
            text="📁 Carpeta de imágenes:",
            font=('Segoe UI', 11),
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary']
        ).pack(anchor="w")
        
        entry_frame = tk.Frame(input_frame, bg=self.colors['bg_card'])
        entry_frame.pack(fill="x", pady=(5, 0))
        
        self.entrada_entry = self.create_modern_entry(entry_frame, self.carpeta_entrada)
        self.entrada_entry.pack(side=tk.LEFT, fill="x", expand=True)
        
        self.create_modern_button(
            entry_frame, "Examinar",
            self.seleccionar_carpeta_entrada,
            width=12
        ).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Carpeta salida
        output_frame = tk.Frame(card, bg=self.colors['bg_card'])
        output_frame.pack(fill="x")
        
        tk.Label(
            output_frame,
            text="💾 Carpeta de salida:",
            font=('Segoe UI', 11),
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary']
        ).pack(anchor="w")
        
        entry_frame2 = tk.Frame(output_frame, bg=self.colors['bg_card'])
        entry_frame2.pack(fill="x", pady=(5, 0))
        
        self.salida_entry = self.create_modern_entry(entry_frame2, self.carpeta_salida)
        self.salida_entry.pack(side=tk.LEFT, fill="x", expand=True)
        
        self.create_modern_button(
            entry_frame2, "Examinar",
            self.seleccionar_carpeta_salida,
            width=12
        ).pack(side=tk.RIGHT, padx=(10, 0))
    
    def create_options_section(self, parent):
        """Crea la sección de opciones"""
        card = self.create_card(parent, "Opciones de Procesamiento")
        card.pack(fill="x", pady=(0, 15))
        
        # Grid de opciones
        options_grid = tk.Frame(card, bg=self.colors['bg_card'])
        options_grid.pack(fill="x")
        
        # Columna 1
        col1 = tk.Frame(options_grid, bg=self.colors['bg_card'])
        col1.pack(side=tk.LEFT, fill="both", expand=True)
        
        self.create_modern_checkbox(col1, "🎯 Detectar objetos", self.incluir_objetos)
        self.create_modern_checkbox(col1, "✏️ Renombrar archivos", self.renombrar_archivos)
        
        # Columna 2
        col2 = tk.Frame(options_grid, bg=self.colors['bg_card'])
        col2.pack(side=tk.LEFT, fill="both", expand=True)
        
        self.create_modern_checkbox(col2, "📄 Generar archivos .txt", self.generar_txt)
        self.create_modern_checkbox(col2, "📊 Generar informe HTML", self.generar_informe)
        
        # Formato de salida
        format_frame = tk.Frame(card, bg=self.colors['bg_card'])
        format_frame.pack(fill="x", pady=(15, 0))
        
        tk.Label(
            format_frame,
            text="📋 Formato de exportación:",
            font=('Segoe UI', 11),
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary']
        ).pack(side=tk.LEFT)
        
        formats = ["JSON", "CSV", "XML"]
        for fmt in formats:
            self.create_modern_radio(
                format_frame, fmt, 
                self.formato_salida, fmt
            ).pack(side=tk.LEFT, padx=10)
    
    def create_action_buttons(self, parent):
        """Crea los botones de acción principales"""
        card = self.create_card(parent, "Acciones")
        card.pack(fill="x", pady=(0, 15))
        
        button_frame = tk.Frame(card, bg=self.colors['bg_card'])
        button_frame.pack(fill="x")
        
        # Botón cargar modelo
        self.btn_cargar = self.create_modern_button(
            button_frame,
            "🤖 Cargar Modelo Florence-2",
            self.cargar_modelo,
            bg_color=self.colors['blue'],
            width=25,
            height=2
        )
        self.btn_cargar.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón procesar
        self.btn_procesar = self.create_modern_button(
            button_frame,
            "🚀 Procesar Imágenes",
            self.procesar_imagenes,
            bg_color=self.colors['accent'],
            width=25,
            height=2
        )
        self.btn_procesar.pack(side=tk.LEFT, padx=(0, 10))
        self.btn_procesar.config(state=tk.DISABLED)
        
        # Botón detener
        self.btn_detener = self.create_modern_button(
            button_frame,
            "⏹️ Detener",
            self.detener_procesamiento,
            bg_color=self.colors['danger'],
            width=15,
            height=2
        )
        self.btn_detener.pack(side=tk.LEFT)
        self.btn_detener.config(state=tk.DISABLED)
    
    def create_progress_section(self, parent):
        """Crea la sección de progreso"""
        card = self.create_card(parent, "Progreso")
        card.pack(fill="x")
        
        # Barra de progreso moderna
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            card,
            variable=self.progress_var,
            style='Modern.Horizontal.TProgressbar',
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack(fill="x", pady=(0, 10))
        
        # Texto de estado
        self.status_label = tk.Label(
            card,
            text="Esperando...",
            font=('Segoe UI', 11),
            bg=self.colors['bg_card'],
            fg=self.colors['text_secondary']
        )
        self.status_label.pack(anchor="w")
        
        # Información adicional
        info_frame = tk.Frame(card, bg=self.colors['bg_card'])
        info_frame.pack(fill="x", pady=(10, 0))
        
        self.info_labels = {}
        for key, text in [
            ('current', '📷 Imagen actual: --'),
            ('processed', '✅ Procesadas: 0'),
            ('errors', '❌ Errores: 0'),
            ('time', '⏱️ Tiempo: --')
        ]:
            label = tk.Label(
                info_frame,
                text=text,
                font=('Segoe UI', 10),
                bg=self.colors['bg_card'],
                fg=self.colors['text_secondary']
            )
            label.pack(side=tk.LEFT, padx=10)
            self.info_labels[key] = label
    
    def create_stats_section(self, parent):
        """Crea la sección de estadísticas"""
        card = self.create_card(parent, "Estadísticas en Tiempo Real")
        card.pack(fill="x", pady=(0, 15))
        
        # Grid de estadísticas
        stats_grid = tk.Frame(card, bg=self.colors['bg_card'])
        stats_grid.pack(fill="both", expand=True)
        
        self.stat_cards = {}
        
        # Crear mini-cards para estadísticas
        stats_data = [
            ('gpu', '🎮 GPU', '0.0 GB / 24.0 GB', self.colors['accent']),
            ('fps', '⚡ Velocidad', '0 img/min', self.colors['success']),
            ('quality', '⭐ Calidad', '0%', self.colors['warning']),
            ('total', '📊 Total', '0 imágenes', self.colors['gradient_start'])
        ]
        
        for i, (key, title, value, color) in enumerate(stats_data):
            stat_card = self.create_stat_card(stats_grid, title, value, color)
            stat_card.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
            self.stat_cards[key] = stat_card['value_label']
        
        stats_grid.columnconfigure(0, weight=1)
        stats_grid.columnconfigure(1, weight=1)
    
    def create_log_section(self, parent):
        """Crea la sección de log"""
        card = self.create_card(parent, "Registro de Actividad", expand=True)
        card.pack(fill="both", expand=True)
        
        # Frame para el log con scrollbar
        log_frame = tk.Frame(card, bg=self.colors['bg_card'])
        log_frame.pack(fill="both", expand=True)
        
        # Text widget con estilo moderno
        self.log_text = tk.Text(
            log_frame,
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            font=('Consolas', 10),
            wrap=tk.WORD,
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        
        # Scrollbar moderna
        scrollbar = tk.Scrollbar(
            log_frame,
            command=self.log_text.yview,
            bg=self.colors['bg_secondary']
        )
        
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(side=tk.LEFT, fill="both", expand=True)
        
        # Tags para colores en el log
        self.log_text.tag_config('info', foreground=self.colors['text_primary'])
        self.log_text.tag_config('success', foreground=self.colors['success'])
        self.log_text.tag_config('warning', foreground=self.colors['warning'])
        self.log_text.tag_config('error', foreground=self.colors['danger'])
        
        # Mensaje de bienvenida
        self.log("✨ Bienvenido a StockPrep Pro", "info")
        self.log("🚀 Sistema listo para procesar imágenes con IA", "success")
    
    def create_footer(self, parent):
        """Crea el footer con información"""
        footer = tk.Frame(parent, bg=self.colors['bg_secondary'], height=50)
        footer.grid(row=2, column=0, sticky="ew", padx=-20, pady=(20, -20))
        
        footer_text = tk.Label(
            footer,
            text="StockPrep Pro v2.0 | Florence-2 AI | Desarrollado con ❤️ para profesionales",
            font=('Segoe UI', 10),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_secondary']
        )
        footer_text.place(relx=0.5, rely=0.5, anchor="center")
    
    # Métodos auxiliares para crear widgets
    def create_card(self, parent, title, expand=False):
        """Crea una tarjeta con título"""
        card = tk.Frame(parent, bg=self.colors['bg_card'], relief=tk.FLAT)
        card.pack_propagate(not expand)
        
        # Borde sutil
        card.config(highlightbackground=self.colors['border'], highlightthickness=1)
        
        # Padding interno
        inner = tk.Frame(card, bg=self.colors['bg_card'])
        inner.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Título
        if title:
            title_label = tk.Label(
                inner,
                text=title,
                font=('Segoe UI', 13, 'bold'),
                bg=self.colors['bg_card'],
                fg=self.colors['text_primary']
            )
            title_label.pack(anchor="w", pady=(0, 10))
        
        return inner
    
    def create_modern_button(self, parent, text, command, bg_color=None, width=20, height=1, small=False):
        """Crea un botón moderno"""
        if bg_color is None:
            bg_color = self.colors['accent']
        
        font_size = 9 if small else 11
        
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg='white',
            font=('Segoe UI', font_size, 'bold'),
            relief=tk.FLAT,
            width=width,
            height=height,
            cursor='hand2',
            activebackground=self.colors['accent_hover'],
            activeforeground='white'
        )
        
        # Efecto hover
        def on_enter(e):
            btn['background'] = self.colors['accent_hover']
        
        def on_leave(e):
            btn['background'] = bg_color
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def create_modern_entry(self, parent, variable):
        """Crea un entry moderno"""
        entry = tk.Entry(
            parent,
            textvariable=variable,
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            font=('Segoe UI', 11),
            relief=tk.FLAT,
            insertbackground=self.colors['text_primary']
        )
        entry.config(highlightbackground=self.colors['border'], highlightthickness=1)
        return entry
    
    def create_modern_checkbox(self, parent, text, variable):
        """Crea un checkbox moderno"""
        cb = tk.Checkbutton(
            parent,
            text=text,
            variable=variable,
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary'],
            font=('Segoe UI', 11),
            selectcolor=self.colors['bg_card'],
            activebackground=self.colors['bg_card'],
            activeforeground=self.colors['text_primary'],
            highlightthickness=0
        )
        cb.pack(anchor="w", pady=5)
        return cb
    
    def create_modern_radio(self, parent, text, variable, value):
        """Crea un radio button moderno"""
        rb = tk.Radiobutton(
            parent,
            text=text,
            variable=variable,
            value=value,
            bg=self.colors['bg_card'],
            fg=self.colors['text_primary'],
            font=('Segoe UI', 11),
            selectcolor=self.colors['bg_card'],
            activebackground=self.colors['bg_card'],
            activeforeground=self.colors['text_primary'],
            highlightthickness=0
        )
        return rb
    
    def create_stat_card(self, parent, title, value, color):
        """Crea una mini tarjeta de estadística"""
        frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        frame.config(highlightbackground=color, highlightthickness=2)
        
        inner = tk.Frame(frame, bg=self.colors['bg_secondary'])
        inner.pack(fill="both", expand=True, padx=10, pady=10)
        
        title_label = tk.Label(
            inner,
            text=title,
            font=('Segoe UI', 10),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_secondary']
        )
        title_label.pack(anchor="w")
        
        value_label = tk.Label(
            inner,
            text=value,
            font=('Segoe UI', 14, 'bold'),
            bg=self.colors['bg_secondary'],
            fg=color
        )
        value_label.pack(anchor="w")
        
        return {'frame': frame, 'value_label': value_label}
    
    # Métodos de funcionalidad
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
    
    def log(self, message, level="info"):
        """Añade un mensaje al log con color"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, formatted_message, level)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def cambiar_idioma(self, idioma):
        """Cambia el idioma de la interfaz"""
        self.idioma_actual.set(idioma)
        self.translator.set_language(idioma)
        self.log(f"Idioma cambiado a: {idioma.upper()}", "info")
        # Aquí actualizarías todos los textos de la interfaz
    
    def seleccionar_carpeta_entrada(self):
        """Selecciona la carpeta de entrada"""
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta de imágenes")
        if carpeta:
            self.carpeta_entrada.set(carpeta)
            # Contar imágenes
            extensiones = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
            imagenes = [f for f in Path(carpeta).iterdir() if f.suffix.lower() in extensiones]
            self.log(f"📁 Carpeta seleccionada: {len(imagenes)} imágenes encontradas", "success")
    
    def seleccionar_carpeta_salida(self):
        """Selecciona la carpeta de salida"""
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta de salida")
        if carpeta:
            self.carpeta_salida.set(carpeta)
            self.log(f"💾 Carpeta de salida: {carpeta}", "info")
    
    def cargar_modelo(self):
        """Carga el modelo en un hilo separado"""
        # Cambiar estado visual del botón
        self.btn_cargar.config(
            state=tk.DISABLED,
            text='Cargando...',
            bg=self.colors['warning']
        )

        def cargar():
            try:
                self.queue.put(('log', 'Iniciando carga del modelo Florence-2...', 'info'))
                self.queue.put(('button_state', 'cargar', 'disabled'))
                
                self.model_manager = Florence2Manager()
                
                def progress_callback(msg):
                    self.queue.put(('log', msg, 'info'))
                
                if self.model_manager.cargar_modelo(callback=progress_callback):
                    self.processor = ImageProcessor(self.model_manager)
                    self.queue.put(('modelo_cargado', True))
                    self.queue.put(('log', '✅ Modelo cargado correctamente', 'success'))
                    self.queue.put(('update_stat', 'gpu', self.model_manager.obtener_uso_memoria()))
                else:
                    self.queue.put(('log', '❌ Error al cargar el modelo', 'error'))
                    self.queue.put(('modelo_error', True))

            except Exception as e:
                self.queue.put(('log', f'Error: {str(e)}', 'error'))
                self.queue.put(('modelo_error', True))
        
        thread = threading.Thread(target=cargar, daemon=True)
        thread.start()
    
    def procesar_imagenes(self):
        """Procesa las imágenes seleccionadas"""
        if not self.carpeta_entrada.get():
            messagebox.showerror("Error", "Selecciona una carpeta de imágenes")
            return

        self.procesando = True
        self.btn_procesar.config(
            state=tk.DISABLED,
            text='Procesando...',
            bg=self.colors['blue']
        )
        self.btn_detener.config(state=tk.NORMAL)
        
        def procesar():
            try:
                carpeta_entrada = Path(self.carpeta_entrada.get())
                carpeta_salida = Path(self.carpeta_salida.get())
                carpeta_salida.mkdir(exist_ok=True, parents=True)
                
                # Buscar imágenes
                extensiones = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
                imagenes = [f for f in carpeta_entrada.iterdir() if f.suffix.lower() in extensiones]
                
                if not imagenes:
                    self.queue.put(('log', '❌ No se encontraron imágenes', 'error'))
                    return
                
                self.queue.put(('log', f'🚀 Procesando {len(imagenes)} imágenes...', 'info'))
                self.metrics.reset()
                
                resultados = []
                for i, imagen_path in enumerate(imagenes):
                    if not self.procesando:
                        break
                    
                    # Actualizar progreso
                    progress = ((i + 1) / len(imagenes)) * 100
                    self.queue.put(('progress', progress))
                    self.queue.put(('update_info', {
                        'current': f'📷 Imagen actual: {imagen_path.name}',
                        'processed': f'✅ Procesadas: {i+1}/{len(imagenes)}',
                        'time': f'⏱️ Tiempo: {self.metrics.get_tiempo_transcurrido()}'
                    }))
                    
                    # Procesar imagen
                    import time
                    start_time = time.time()
                    
                    resultado = self.processor.procesar_imagen(str(imagen_path))
                    
                    process_time = time.time() - start_time
                    self.metrics.actualizar(process_time, 0)
                    
                    if 'error' not in resultado:
                        # Procesar resultado exitoso
                        self.procesar_resultado_exitoso(resultado, imagen_path, carpeta_salida)
                        resultados.append(resultado)
                        self.queue.put(('log', f'✅ {imagen_path.name} procesada', 'success'))
                    else:
                        self.metrics.registrar_error()
                        self.queue.put(('log', f'❌ Error en {imagen_path.name}: {resultado["error"]}', 'error'))
                    
                    # Actualizar estadísticas
                    self.queue.put(('update_stat', 'gpu', self.model_manager.obtener_uso_memoria()))
                    self.queue.put(('update_stat', 'fps', f'{self.metrics.get_velocidad():.1f} img/min'))
                    self.queue.put(('update_stat', 'total', f'{i+1} imágenes'))
                
                # Generar reportes finales
                if resultados:
                    self.generar_reportes_finales(resultados, carpeta_salida)
                
                self.queue.put(('procesamiento_completo', len(resultados)))
                
            except Exception as e:
                self.queue.put(('log', f'Error crítico: {str(e)}', 'error'))
            finally:
                self.procesando = False
                self.queue.put(('button_state', 'detener', 'disabled'))
        
        thread = threading.Thread(target=procesar, daemon=True)
        thread.start()
    
    def procesar_resultado_exitoso(self, resultado, imagen_path, carpeta_salida):
        """Procesa un resultado exitoso"""
        # Mejorar caption
        if 'descripcion' in resultado:
            from utils.caption_enhancer import CaptionEnhancer
            enhancer = CaptionEnhancer(self.translator)
            resultado['descripcion'] = enhancer.mejorar_caption(resultado['descripcion'])
        
        # Guardar en base de datos
        registro_id = self.database.guardar_imagen(
            nombre_original=imagen_path.name,
            nombre_nuevo=resultado.get('nombre_nuevo', ''),
            descripcion=resultado.get('descripcion', ''),
            keywords=resultado.get('keywords', []),
            ruta_original=str(imagen_path),
            ruta_nueva=str(carpeta_salida / resultado.get('nombre_nuevo', imagen_path.name))
        )
        
        resultado['db_id'] = registro_id
        
        # Generar archivo .txt si está activado
        if self.generar_txt.get():
            self.generar_archivo_txt(resultado, carpeta_salida)
        
        # Renombrar/copiar archivo si está activado
        if self.renombrar_archivos.get():
            self.copiar_con_nuevo_nombre(imagen_path, resultado, carpeta_salida)
    
    def generar_archivo_txt(self, resultado, carpeta_salida):
        """Genera un archivo .txt descriptivo para la imagen"""
        nombre_base = Path(resultado.get('archivo', 'imagen')).stem
        txt_path = carpeta_salida / f"{nombre_base}_descripcion.txt"
        
        contenido = f"""INFORMACIÓN DE LA IMAGEN
======================

Archivo: {resultado.get('archivo', 'N/A')}
Fecha de procesamiento: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

DESCRIPCIÓN:
{resultado.get('descripcion', 'Sin descripción')}

PALABRAS CLAVE:
{', '.join(resultado.get('keywords', []))}

OBJETOS DETECTADOS:
{self.formatear_objetos(resultado.get('objetos', {}))}

---
Generado por StockPrep Pro - Florence-2 AI
"""
        
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(contenido)
    
    def formatear_objetos(self, objetos):
        """Formatea la lista de objetos detectados"""
        if isinstance(objetos, dict) and 'labels' in objetos:
            return ', '.join(objetos['labels'])
        return 'Ninguno detectado'
    
    def copiar_con_nuevo_nombre(self, imagen_path, resultado, carpeta_salida):
        """Copia la imagen con un nuevo nombre basado en la descripción"""
        import shutil
        from utils.filename_generator import FilenameGenerator
        
        generator = FilenameGenerator()
        nuevo_nombre = generator.generar_nombre(
            resultado.get('descripcion', ''),
            imagen_path.suffix
        )
        
        destino = carpeta_salida / nuevo_nombre
        shutil.copy2(imagen_path, destino)
        
        resultado['nombre_nuevo'] = nuevo_nombre
        resultado['ruta_nueva'] = str(destino)
    
    def generar_reportes_finales(self, resultados, carpeta_salida):
        """Genera los reportes finales"""
        try:
            # Exportar en el formato seleccionado
            from io.output_handler import OutputHandler
            handler = OutputHandler(carpeta_salida)
            
            formato = self.formato_salida.get()
            archivo_salida = handler.exportar(resultados, formato)
            self.queue.put(('log', f'📄 Archivo {formato} generado: {archivo_salida}', 'success'))
            
            # Generar informe HTML si está activado
            if self.generar_informe.get():
                report_gen = ReportGenerator()
                informe_path = report_gen.generar_informe_html(
                    resultados, 
                    carpeta_salida,
                    self.metrics.get_resumen()
                )
                self.queue.put(('log', f'📊 Informe HTML generado: {informe_path}', 'success'))
                
                # Abrir el informe en el navegador
                import webbrowser
                webbrowser.open(str(informe_path))
                
        except Exception as e:
            self.queue.put(('log', f'Error generando reportes: {str(e)}', 'error'))
    
    def detener_procesamiento(self):
        """Detiene el procesamiento"""
        self.procesando = False
        self.log("⏹️ Procesamiento detenido por el usuario", "warning")
    
    def check_queue(self):
        """Verifica mensajes en la cola"""
        try:
            while True:
                tipo, *datos = self.queue.get_nowait()
                
                if tipo == 'log':
                    self.log(datos[0], datos[1] if len(datos) > 1 else 'info')
                elif tipo == 'progress':
                    self.progress_var.set(datos[0])
                elif tipo == 'update_info':
                    for key, value in datos[0].items():
                        if key in self.info_labels:
                            self.info_labels[key].config(text=value)
                elif tipo == 'update_stat':
                    key, value = datos[0], datos[1]
                    if key in self.stat_cards:
                        self.stat_cards[key].config(text=value)
                elif tipo == 'button_state':
                    button, state = datos[0], datos[1]
                    if button == 'cargar':
                        self.btn_cargar.config(state=state)
                        if state == tk.NORMAL:
                            self.btn_cargar.config(
                                text='🤖 Cargar Modelo Florence-2',
                                bg=self.colors['blue']
                            )
                    elif button == 'procesar':
                        self.btn_procesar.config(state=state)
                        if state == tk.NORMAL:
                            self.btn_procesar.config(
                                text='🚀 Procesar Imágenes',
                                bg=self.colors['accent']
                            )
                    elif button == 'detener':
                        self.btn_detener.config(state=state)
                elif tipo == 'modelo_error':
                    self.btn_cargar.config(
                        text='❌ Error al cargar',
                        state=tk.NORMAL,
                        bg=self.colors['danger']
                    )
                elif tipo == 'modelo_cargado':
                    self.modelo_cargado = True
                    self.btn_cargar.config(
                        text="✅ Modelo Cargado",
                        state=tk.DISABLED,
                        bg=self.colors['success']
                    )
                    self.btn_procesar.config(state=tk.NORMAL)
                elif tipo == 'procesamiento_completo':
                    total = datos[0]
                    self.log(f"🎉 Procesamiento completado: {total} imágenes", "success")
                    messagebox.showinfo(
                        "Completado",
                        f"Se procesaron {total} imágenes exitosamente.\n"
                        "Revisa la carpeta de salida para ver los resultados."
                    )
                    self.btn_procesar.config(
                        text='✅ Completado',
                        state=tk.NORMAL,
                        bg=self.colors['success']
                    )
                    
        except queue.Empty:
            pass
        
        self.root.after(100, self.check_queue)
    
    def run(self):
        """Inicia la aplicación"""
        self.root.mainloop()


if __name__ == "__main__":
    app = StockPrepApp()
    app.run()
