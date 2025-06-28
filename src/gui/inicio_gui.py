"""
GUI de Inicio - Menú Principal de StockPrep Pro v2.0
Permite acceder a los diferentes módulos del sistema
"""
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from datetime import datetime
import threading

# Importar módulos del core
try:
    from core.sqlite_database import SQLiteImageDatabase
    from core.model_manager import Florence2Manager
except ImportError:
    # Fallback para importaciones relativas
    sys.path.append('src')
    from core.sqlite_database import SQLiteImageDatabase
    from core.model_manager import Florence2Manager

class ModernStartupStyle:
    """Estilos modernos para la página de inicio"""
    
    @staticmethod
    def configure_styles():
        """Configura estilos modernos para la aplicación"""
        style = ttk.Style()
        
        # Configurar tema base
        try:
            style.theme_use('clam')
        except:
            style.theme_use('default')
        
        # Colores del tema
        colors = {
            'bg': '#F5F5F5',           # Fondo principal
            'card_bg': '#FFFFFF',      # Fondo de tarjetas
            'primary': '#0078D4',      # Azul principal
            'success': '#3CB371',      # Verde éxito
            'text': '#323130',         # Texto principal
            'text_light': '#605E5C',   # Texto secundario
            'border': '#E1DFDD',       # Bordes
        }
        
        # Estilo para frame principal
        style.configure('Main.TFrame',
                       background=colors['bg'],
                       relief='flat')
        
        # Estilo para tarjetas (cards)
        style.configure('Card.TFrame',
                       background=colors['card_bg'],
                       relief='solid',
                       borderwidth=1)
        
        # Estilo para títulos
        style.configure('Title.TLabel',
                       background=colors['card_bg'],
                       foreground=colors['text'],
                       font=('Segoe UI', 16, 'bold'))
        
        # Estilo para subtítulos
        style.configure('Subtitle.TLabel',
                       background=colors['card_bg'],
                       foreground=colors['text_light'],
                       font=('Segoe UI', 10))
        
        # Estilo para botones principales
        style.configure('MainButton.TButton',
                       background=colors['primary'],
                       foreground='white',
                       font=('Segoe UI', 12, 'bold'),
                       borderwidth=0,
                       focuscolor='none',
                       padding=(20, 15))
        
        style.map('MainButton.TButton',
                 background=[('active', '#106EBE'),
                           ('pressed', '#005A9E')])
        
        # Estilo para botones secundarios
        style.configure('SecondButton.TButton',
                       background=colors['success'],
                       foreground='white',
                       font=('Segoe UI', 11, 'bold'),
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 10))
        
        style.map('SecondButton.TButton',
                 background=[('active', '#2E8B57'),
                           ('pressed', '#228B22')])

class StockPrepStartupApp:
    """Aplicación de inicio de StockPrep Pro"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.db_manager = None
        self.model_manager = None
        
        # Inicializar componentes básicos
        self.init_core_components()
        
        # Configurar interfaz
        self.init_ui()
        
        # Configurar estilos
        ModernStartupStyle.configure_styles()
        
        # Obtener estadísticas iniciales
        self.update_stats()
    
    def init_core_components(self):
        """Inicializa los componentes básicos del core"""
        try:
            self.db_manager = SQLiteImageDatabase()
            self.model_manager = Florence2Manager()
        except Exception as e:
            print(f"⚠️ Error inicializando componentes: {e}")
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Configuración de la ventana principal
        self.root.title("StockPrep Pro v2.0 - Centro de Control")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Configurar icono
        try:
            self.root.iconbitmap("stockprep_icon.ico")
        except:
            try:
                icon_img = tk.PhotoImage(file="stockprep_icon.png")
                self.root.iconphoto(True, icon_img)
            except:
                pass
        
        # Frame principal
        main_frame = ttk.Frame(self.root, style='Main.TFrame')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título principal
        title_frame = ttk.Frame(main_frame, style='Main.TFrame')
        title_frame.pack(fill='x', pady=(0, 30))
        
        title_label = ttk.Label(title_frame, 
                               text="🚀 StockPrep Pro v2.0",
                               font=('Segoe UI', 24, 'bold'),
                               background='#F5F5F5',
                               foreground='#323130')
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame,
                                 text="Sistema Inteligente de Procesamiento de Imágenes",
                                 font=('Segoe UI', 12),
                                 background='#F5F5F5',
                                 foreground='#605E5C')
        subtitle_label.pack(pady=(5, 0))
        
        # Container para las tarjetas
        cards_frame = ttk.Frame(main_frame, style='Main.TFrame')
        cards_frame.pack(fill='both', expand=True)
        
        # Crear tarjetas de módulos
        self.create_module_cards(cards_frame)
        
        # Panel de estadísticas
        self.create_stats_panel(main_frame)
        
        # Barra de estado
        self.create_status_bar()
    
    def create_module_cards(self, parent):
        """Crea las tarjetas de los módulos disponibles"""
        # Frame para las dos columnas principales
        modules_frame = ttk.Frame(parent, style='Main.TFrame')
        modules_frame.pack(fill='both', expand=True)
        
        # Columna izquierda - Reconocimiento de Imágenes
        left_frame = ttk.Frame(modules_frame, style='Main.TFrame')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        self.create_recognition_card(left_frame)
        
        # Columna derecha - Base de Datos
        right_frame = ttk.Frame(modules_frame, style='Main.TFrame')
        right_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        self.create_database_card(right_frame)
    
    def create_recognition_card(self, parent):
        """Crea la tarjeta del módulo de reconocimiento"""
        # Tarjeta principal
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(fill='both', expand=True, pady=(0, 10))
        
        # Contenido de la tarjeta
        content_frame = ttk.Frame(card, style='Card.TFrame')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Icono y título
        header_frame = ttk.Frame(content_frame, style='Card.TFrame')
        header_frame.pack(fill='x', pady=(0, 15))
        
        title_label = ttk.Label(header_frame,
                               text="🖼️ Reconocimiento de Imágenes",
                               style='Title.TLabel')
        title_label.pack()
        
        # Descripción
        desc_text = """
Procesa imágenes individuales o en lote usando IA avanzada:

• Generación automática de descripciones (captions)
• Detección y localización de objetos
• Extracción inteligente de palabras clave
• Exportación en múltiples formatos
• Renombrado automático de archivos
        """.strip()
        
        desc_label = ttk.Label(content_frame,
                              text=desc_text,
                              style='Subtitle.TLabel',
                              justify='left')
        desc_label.pack(fill='x', pady=(0, 20))
        
        # Botón principal
        main_button = ttk.Button(content_frame,
                                text="🚀 Abrir Reconocimiento de Imágenes",
                                style='MainButton.TButton',
                                command=self.open_recognition_module)
        main_button.pack(fill='x', pady=(0, 10))
        
        # Botón de configuración
        config_button = ttk.Button(content_frame,
                                  text="⚙️ Configurar Modelo",
                                  style='SecondButton.TButton',
                                  command=self.configure_model)
        config_button.pack(fill='x')
    
    def create_database_card(self, parent):
        """Crea la tarjeta del módulo de base de datos"""
        # Tarjeta principal
        card = ttk.Frame(parent, style='Card.TFrame')
        card.pack(fill='both', expand=True, pady=(0, 10))
        
        # Contenido de la tarjeta
        content_frame = ttk.Frame(card, style='Card.TFrame')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Icono y título
        header_frame = ttk.Frame(content_frame, style='Card.TFrame')
        header_frame.pack(fill='x', pady=(0, 15))
        
        title_label = ttk.Label(header_frame,
                               text="🗄️ Gestión de Base de Datos",
                               style='Title.TLabel')
        title_label.pack()
        
        # Descripción
        desc_text = """
Administra y consulta todas las imágenes procesadas:

• Búsqueda avanzada por contenido y metadatos
• Visualización de historial completo
• Exportación masiva de datos
• Estadísticas detalladas del sistema
• Gestión de archivos y copias de seguridad
        """.strip()
        
        desc_label = ttk.Label(content_frame,
                              text=desc_text,
                              style='Subtitle.TLabel',
                              justify='left')
        desc_label.pack(fill='x', pady=(0, 20))
        
        # Botón principal
        main_button = ttk.Button(content_frame,
                                text="🗄️ Abrir Gestión de Base de Datos",
                                style='MainButton.TButton',
                                command=self.open_database_module)
        main_button.pack(fill='x', pady=(0, 10))
        
        # Botón de estadísticas
        stats_button = ttk.Button(content_frame,
                                 text="📊 Ver Estadísticas",
                                 style='SecondButton.TButton',
                                 command=self.show_quick_stats)
        stats_button.pack(fill='x')
    
    def create_stats_panel(self, parent):
        """Crea el panel de estadísticas rápidas"""
        stats_frame = ttk.LabelFrame(parent, text="📊 Resumen del Sistema", padding=15)
        stats_frame.pack(fill='x', pady=(20, 0))
        
        # Frame para estadísticas en columnas
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill='x')
        
        # Estadísticas básicas
        self.stats_labels = {}
        
        stats_info = [
            ('total_images', 'Imágenes Procesadas', '0'),
            ('total_size', 'Tamaño Base de Datos', '0 KB'),
            ('last_activity', 'Última Actividad', 'Nunca'),
            ('model_status', 'Estado del Modelo', 'No cargado')
        ]
        
        for i, (key, label, default) in enumerate(stats_info):
            row = i // 2
            col = i % 2
            
            stat_frame = ttk.Frame(stats_grid)
            stat_frame.grid(row=row, column=col, sticky='ew', padx=10, pady=5)
            
            ttk.Label(stat_frame, text=f"{label}:", font=('Segoe UI', 9, 'bold')).pack(anchor='w')
            self.stats_labels[key] = ttk.Label(stat_frame, text=default, font=('Segoe UI', 9))
            self.stats_labels[key].pack(anchor='w')
        
        # Configurar grid
        stats_grid.columnconfigure(0, weight=1)
        stats_grid.columnconfigure(1, weight=1)
    
    def create_status_bar(self):
        """Crea la barra de estado"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side='bottom', fill='x')
        
        self.status_label = ttk.Label(self.status_frame, 
                                    text="Listo - Selecciona un módulo para comenzar",
                                    font=('Segoe UI', 9))
        self.status_label.pack(side='left', padx=10, pady=5)
        
        # Reloj
        self.clock_label = ttk.Label(self.status_frame, text="", font=('Segoe UI', 9))
        self.clock_label.pack(side='right', padx=10, pady=5)
        
        self.update_clock()
    
    def update_clock(self):
        """Actualiza el reloj"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.clock_label.config(text=current_time)
        self.root.after(1000, self.update_clock)
    
    def update_stats(self):
        """Actualiza las estadísticas del sistema"""
        try:
            if self.db_manager:
                stats = self.db_manager.obtener_estadisticas_globales()
                
                # Actualizar estadísticas
                total_images = stats.get('total_imagenes_procesadas', 0)
                self.stats_labels['total_images'].config(text=str(total_images))
                
                # Tamaño de base de datos (aproximado)
                try:
                    db_path = Path(self.db_manager.db_path)
                    if db_path.exists():
                        size_bytes = db_path.stat().st_size
                        size_kb = size_bytes / 1024
                        if size_kb > 1024:
                            size_str = f"{size_kb/1024:.1f} MB"
                        else:
                            size_str = f"{size_kb:.1f} KB"
                        self.stats_labels['total_size'].config(text=size_str)
                except:
                    self.stats_labels['total_size'].config(text="N/A")
                
                # Última actividad
                if total_images > 0:
                    self.stats_labels['last_activity'].config(text="Reciente")
                else:
                    self.stats_labels['last_activity'].config(text="Sin actividad")
            
            # Estado del modelo
            if self.model_manager:
                if hasattr(self.model_manager, 'model') and self.model_manager.model:
                    self.stats_labels['model_status'].config(text="✅ Cargado")
                else:
                    self.stats_labels['model_status'].config(text="⚠️ No cargado")
            
        except Exception as e:
            print(f"Error actualizando estadísticas: {e}")
    
    def open_recognition_module(self):
        """Abre el módulo de reconocimiento de imágenes"""
        self.status_label.config(text="Iniciando módulo de reconocimiento...")
        self.root.update()
        
        try:
            # Usar siempre Tkinter para evitar conflictos con QApplication
            from gui.modern_gui_stockprep import StockPrepApp
            
            # Ocultar ventana de inicio
            self.root.withdraw()
            
            # Crear y ejecutar la aplicación de reconocimiento
            app = StockPrepApp()
            app.run()
            
            # Mostrar ventana de inicio al cerrar
            self.root.deiconify()
            
            # Actualizar estadísticas al regresar
            self.update_stats()
            self.status_label.config(text="Módulo de reconocimiento cerrado")
            
        except Exception as e:
            # Asegurar que la ventana de inicio se muestre incluso si hay error
            self.root.deiconify()
            messagebox.showerror("Error", f"Error abriendo módulo de reconocimiento: {e}")
            self.status_label.config(text="Error al abrir módulo de reconocimiento")
            print(f"Error detallado: {e}")
            import traceback
            traceback.print_exc()
    
    def open_database_module(self):
        """Abre el módulo de gestión de base de datos"""
        self.status_label.config(text="Iniciando módulo de base de datos...")
        self.root.update()
        
        try:
            from gui.database_gui import DatabaseManagerApp
            
            # Ocultar ventana de inicio
            self.root.withdraw()
            
            # Crear y ejecutar la aplicación de base de datos
            app = DatabaseManagerApp(self.db_manager)
            app.run()
            
            # Mostrar ventana de inicio al cerrar
            self.root.deiconify()
            
            # Actualizar estadísticas al regresar
            self.update_stats()
            self.status_label.config(text="Módulo de base de datos cerrado")
            
        except Exception as e:
            # Asegurar que la ventana de inicio se muestre incluso si hay error
            self.root.deiconify()
            messagebox.showerror("Error", f"Error abriendo módulo de base de datos: {e}")
            self.status_label.config(text="Error al abrir módulo de base de datos")
            print(f"Error detallado: {e}")
            import traceback
            traceback.print_exc()
    
    def configure_model(self):
        """Abre configuración del modelo"""
        messagebox.showinfo("Configuración", 
                           "La configuración del modelo se realiza desde el módulo de reconocimiento.\n\n"
                           "Usa el botón 'Abrir Reconocimiento de Imágenes' y luego 'Cargar Modelo'.")
    
    def show_quick_stats(self):
        """Muestra estadísticas rápidas"""
        try:
            if self.db_manager:
                stats = self.db_manager.obtener_estadisticas_globales()
                
                msg = f"""📊 Estadísticas del Sistema

🖼️ Imágenes procesadas: {stats.get('total_imagenes_procesadas', 0)}
❌ Errores registrados: {stats.get('total_errores', 0)}

💾 Base de datos: {self.db_manager.db_path}
📅 Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Para estadísticas detalladas, usa el módulo de Base de Datos."""
                
                messagebox.showinfo("Estadísticas Rápidas", msg)
            else:
                messagebox.showwarning("Sin datos", "No se puede acceder a la base de datos")
        except Exception as e:
            messagebox.showerror("Error", f"Error obteniendo estadísticas: {e}")
    
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
    app = StockPrepStartupApp()
    app.run()

if __name__ == "__main__":
    main() 