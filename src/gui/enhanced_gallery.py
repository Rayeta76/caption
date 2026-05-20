"""
Enhanced Gallery - Galería Mejorada tipo Web de Stock
StockPrep Pro v2.0 - Con SQLite + FTS5 + WebP BLOB

Funcionalidades:
- Vista ampliada al hacer clic
- Búsqueda visual con imágenes
- Thumbnails WebP optimizados
- Navegación intuitiva
- Experiencia tipo web de stock
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from datetime import datetime
import json
import threading
from typing import Dict, List, Optional, Tuple
import logging
from PIL import Image, ImageTk
import io

# Importar componentes
try:
    from core.enhanced_database_manager_v2 import EnhancedDatabaseManagerV2
    from utils.safe_image_manager import create_safe_photoimage, cleanup_photoimage, cleanup_all_photoimages, shutdown_image_manager
except ImportError:
    import sys
    sys.path.append('src')
    from core.enhanced_database_manager_v2 import EnhancedDatabaseManagerV2
    from utils.safe_image_manager import create_safe_photoimage, cleanup_photoimage, cleanup_all_photoimages, shutdown_image_manager

logger = logging.getLogger(__name__)

class EnhancedGallery:
    """
    Galería mejorada tipo web de stock con SQLite + FTS5 + WebP
    """
    
    def __init__(self, parent, db_manager=None):
        """
        Inicializar la galería mejorada
        
        Args:
            parent: Widget padre
            db_manager: Instancia del gestor de base de datos v2.0
        """
        self.parent = parent
        self.db_manager = db_manager or EnhancedDatabaseManagerV2("stockprep_images.db")
        
        # Variables de estado
        self.current_images = []
        self.filtered_images = []
        self.current_page = 0
        self.images_per_page = 20
        self.current_view = "grid"  # grid, list, large
        
        # Variables para thumbnails
        self.thumbnails = {}
        self.loading_thumbnails = set()
        
        # Variables para vista ampliada
        self.image_viewer_window = None
        self.current_image_index = 0
        
        # Configurar interfaz
        self.init_ui()
        
        # Cargar imágenes iniciales
        self.load_images()
    
    def init_ui(self):
        """Inicializar la interfaz de usuario"""
        # Frame principal
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Panel superior - Controles
        self.create_controls_panel()
        
        # Panel principal - Galería
        self.create_gallery_panel()
        
        # Panel inferior - Información y paginación
        self.create_bottom_panel()
    
    def create_controls_panel(self):
        """Crear panel de controles superior"""
        controls_frame = ttk.Frame(self.main_frame)
        controls_frame.pack(fill='x', pady=(0, 10))
        
        # Título
        title_label = ttk.Label(controls_frame, text="🖼️ Galería de Imágenes Stock", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(side='left')
        
        # Controles de búsqueda
        search_frame = ttk.Frame(controls_frame)
        search_frame.pack(side='right')
        
        # Campo de búsqueda
        ttk.Label(search_frame, text="🔍 Buscar:").pack(side='left', padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side='left', padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
        
        # Botón de búsqueda
        search_btn = ttk.Button(search_frame, text="Buscar", command=self.perform_search)
        search_btn.pack(side='left', padx=(0, 10))
        
        # Botón limpiar búsqueda
        clear_btn = ttk.Button(search_frame, text="Limpiar", command=self.clear_search)
        clear_btn.pack(side='left', padx=(0, 10))
        
        # Controles de vista
        view_frame = ttk.Frame(controls_frame)
        view_frame.pack(side='right', padx=(20, 0))
        
        ttk.Label(view_frame, text="Vista:").pack(side='left', padx=(0, 5))
        self.view_var = tk.StringVar(value="grid")
        view_combo = ttk.Combobox(view_frame, textvariable=self.view_var,
                                 values=["grid", "list", "large"], width=10, state="readonly")
        view_combo.pack(side='left', padx=(0, 10))
        view_combo.bind('<<ComboboxSelected>>', self.on_view_change)
        
        # Botón actualizar
        refresh_btn = ttk.Button(view_frame, text="🔄 Actualizar", command=self.refresh_gallery)
        refresh_btn.pack(side='left')
    
    def create_gallery_panel(self):
        """Crear panel principal de la galería"""
        # Frame para la galería
        self.gallery_frame = ttk.Frame(self.main_frame)
        self.gallery_frame.pack(fill='both', expand=True)
        
        # Canvas con scrollbar
        self.gallery_canvas = tk.Canvas(self.gallery_frame, bg='white')
        self.gallery_scrollbar = ttk.Scrollbar(self.gallery_frame, orient="vertical", 
                                             command=self.gallery_canvas.yview)
        self.gallery_scrollable_frame = ttk.Frame(self.gallery_canvas)
        
        self.gallery_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.gallery_canvas.configure(scrollregion=self.gallery_canvas.bbox("all"))
        )
        
        self.gallery_canvas.create_window((0, 0), window=self.gallery_scrollable_frame, anchor="nw")
        self.gallery_canvas.configure(yscrollcommand=self.gallery_scrollbar.set)
        
        self.gallery_canvas.pack(side="left", fill="both", expand=True)
        self.gallery_scrollbar.pack(side="right", fill="y")
        
        # Bind eventos
        self.gallery_canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.gallery_canvas.bind("<Button-4>", self._on_mousewheel)
        self.gallery_canvas.bind("<Button-5>", self._on_mousewheel)
    
    def create_bottom_panel(self):
        """Crear panel inferior con información y paginación"""
        bottom_frame = ttk.Frame(self.main_frame)
        bottom_frame.pack(fill='x', pady=(10, 0))
        
        # Información de la galería
        self.info_label = ttk.Label(bottom_frame, text="Cargando galería...")
        self.info_label.pack(side='left')
        
        # Controles de paginación
        pagination_frame = ttk.Frame(bottom_frame)
        pagination_frame.pack(side='right')
        
        self.prev_btn = ttk.Button(pagination_frame, text="◀ Anterior", 
                                  command=self.prev_page, state='disabled')
        self.prev_btn.pack(side='left', padx=2)
        
        self.page_label = ttk.Label(pagination_frame, text="Página 1")
        self.page_label.pack(side='left', padx=10)
        
        self.next_btn = ttk.Button(pagination_frame, text="Siguiente ▶", 
                                  command=self.next_page, state='disabled')
        self.next_btn.pack(side='left', padx=2)
    
    def load_images(self):
        """Cargar imágenes desde la base de datos"""
        try:
            # Obtener imágenes con thumbnails
            self.current_images = self.db_manager.buscar_imagenes_por_filtros(
                {'tiene_thumbnail': True}, limite=1000
            )
            self.filtered_images = self.current_images.copy()
            
            # Actualizar interfaz
            self.update_gallery_display()
            self.update_pagination()
            self.update_info()
            
        except Exception as e:
            logger.error(f"Error cargando imágenes: {e}")
            messagebox.showerror("Error", f"Error cargando imágenes: {e}")
    
    def perform_search(self):
        """Realizar búsqueda FTS5"""
        try:
            query = self.search_var.get().strip()
            
            if not query:
                self.filtered_images = self.current_images.copy()
            else:
                # Búsqueda FTS5
                self.filtered_images = self.db_manager.buscar_imagenes_fts5(query, limite=1000)
            
            self.current_page = 0
            self.update_gallery_display()
            self.update_pagination()
            self.update_info()
            
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
            messagebox.showerror("Error", f"Error en búsqueda: {e}")
    
    def clear_search(self):
        """Limpiar búsqueda"""
        self.search_var.set("")
        self.filtered_images = self.current_images.copy()
        self.current_page = 0
        self.update_gallery_display()
        self.update_pagination()
        self.update_info()
    
    def on_search_change(self, event=None):
        """Manejar cambios en el campo de búsqueda"""
        # Búsqueda en tiempo real (opcional)
        pass
    
    def on_view_change(self, event=None):
        """Manejar cambio de vista"""
        self.current_view = self.view_var.get()
        self.update_gallery_display()
    
    def update_gallery_display(self):
        """Actualizar la visualización de la galería"""
        # Limpiar frame
        for widget in self.gallery_scrollable_frame.winfo_children():
            widget.destroy()
        
        # Calcular imágenes para la página actual
        start_idx = self.current_page * self.images_per_page
        end_idx = start_idx + self.images_per_page
        page_images = self.filtered_images[start_idx:end_idx]
        
        if self.current_view == "grid":
            self._create_grid_view(page_images)
        elif self.current_view == "list":
            self._create_list_view(page_images)
        elif self.current_view == "large":
            self._create_large_view(page_images)
    
    def _create_grid_view(self, images):
        """Crear vista de cuadrícula"""
        cols = 5  # 5 columnas
        for i, image_data in enumerate(images):
            row = i // cols
            col = i % cols
            
            # Frame para cada imagen
            img_frame = ttk.Frame(self.gallery_scrollable_frame, relief='raised', borderwidth=1)
            img_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            
            # Crear thumbnail
            self._create_thumbnail(img_frame, image_data, size=(200, 200))
            
            # Configurar grid
            self.gallery_scrollable_frame.columnconfigure(col, weight=1)
            self.gallery_scrollable_frame.rowconfigure(row, weight=1)
    
    def _create_list_view(self, images):
        """Crear vista de lista"""
        for i, image_data in enumerate(images):
            # Frame para cada fila
            row_frame = ttk.Frame(self.gallery_scrollable_frame)
            row_frame.pack(fill='x', padx=5, pady=2)
            
            # Crear thumbnail pequeño
            self._create_thumbnail(row_frame, image_data, size=(100, 100), show_info=True)
    
    def _create_large_view(self, images):
        """Crear vista grande"""
        cols = 3  # 3 columnas para vista grande
        for i, image_data in enumerate(images):
            row = i // cols
            col = i % cols
            
            # Frame para cada imagen
            img_frame = ttk.Frame(self.gallery_scrollable_frame, relief='raised', borderwidth=1)
            img_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            
            # Crear thumbnail grande
            self._create_thumbnail(img_frame, image_data, size=(300, 300))
            
            # Configurar grid
            self.gallery_scrollable_frame.columnconfigure(col, weight=1)
            self.gallery_scrollable_frame.rowconfigure(row, weight=1)
    
    def _create_thumbnail(self, parent, image_data, size=(200, 200), show_info=False):
        """Crear thumbnail para una imagen"""
        try:
            # Frame para la imagen
            img_frame = ttk.Frame(parent)
            img_frame.pack(fill='both', expand=True, padx=5, pady=5)
            
            # Obtener thumbnail WebP
            thumbnail_webp = self.db_manager.obtener_thumbnail_webp(image_data['id'])
            
            if thumbnail_webp:
                # Convertir WebP a PhotoImage
                try:
                    with Image.open(io.BytesIO(thumbnail_webp)) as img:
                        img = img.resize(size, Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        
                        # Label para la imagen
                        img_label = ttk.Label(img_frame, image=photo)
                        img_label.pack()
                        img_label.image = photo  # Mantener referencia
                        
                        # Bind eventos
                        img_label.bind("<Button-1>", lambda e, data=image_data: self.show_image_viewer(data))
                        img_label.bind("<Double-Button-1>", lambda e, data=image_data: self.show_image_viewer(data))
                        
                        # Tooltip
                        self._create_tooltip(img_label, image_data)
                        
                except Exception as e:
                    logger.warning(f"Error creando thumbnail: {e}")
                    self._create_placeholder(img_frame, size)
            else:
                self._create_placeholder(img_frame, size)
            
            # Información adicional si se solicita
            if show_info:
                self._create_image_info(img_frame, image_data)
                
        except Exception as e:
            logger.error(f"Error creando thumbnail: {e}")
            self._create_placeholder(parent, size)
    
    def _create_placeholder(self, parent, size):
        """Crear placeholder para imagen sin thumbnail"""
        placeholder = ttk.Label(parent, text="🖼️\nSin thumbnail", 
                               font=('Segoe UI', 10), foreground='gray')
        placeholder.pack(expand=True)
    
    def _create_image_info(self, parent, image_data):
        """Crear información de la imagen"""
        info_frame = ttk.Frame(parent)
        info_frame.pack(fill='x', pady=(5, 0))
        
        # Nombre del archivo
        file_name = Path(image_data.get('file_path', '')).name
        if len(file_name) > 30:
            file_name = file_name[:27] + "..."
        
        name_label = ttk.Label(info_frame, text=file_name, font=('Segoe UI', 9, 'bold'))
        name_label.pack(anchor='w')
        
        # Caption
        caption = image_data.get('caption', 'Sin descripción')
        if len(caption) > 50:
            caption = caption[:47] + "..."
        
        caption_label = ttk.Label(info_frame, text=caption, font=('Segoe UI', 8))
        caption_label.pack(anchor='w')
        
        # Fecha
        date = image_data.get('fecha_creacion', 'N/A')[:10]
        date_label = ttk.Label(info_frame, text=f"📅 {date}", 
                              font=('Segoe UI', 8), foreground='gray')
        date_label.pack(anchor='w')
    
    def _create_tooltip(self, widget, image_data):
        """Crear tooltip con información de la imagen"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            # Información del tooltip
            file_name = Path(image_data.get('file_path', '')).name
            caption = image_data.get('caption', 'Sin descripción')
            keywords = image_data.get('keywords', [])
            keywords_text = ', '.join(keywords[:5]) if keywords else 'Sin keywords'
            
            info_text = f"""📁 {file_name}
📝 {caption[:100]}{'...' if len(caption) > 100 else ''}
🏷️ {keywords_text}
📅 {image_data.get('fecha_creacion', 'N/A')[:10]}"""
            
            ttk.Label(tooltip, text=info_text, background='lightyellow', 
                     relief='solid', borderwidth=1, font=('Segoe UI', 9)).pack()
            
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def show_image_viewer(self, image_data):
        """Mostrar visor de imagen ampliada"""
        try:
            # Crear ventana de visor
            self.image_viewer_window = tk.Toplevel(self.parent)
            self.image_viewer_window.title(f"Visor de Imagen - {Path(image_data.get('file_path', '')).name}")
            self.image_viewer_window.geometry("1000x700")
            self.image_viewer_window.minsize(800, 600)
            
            # Configurar icono
            try:
                self.image_viewer_window.iconbitmap("stockprep_icon.ico")
            except:
                pass
            
            # Encontrar índice de la imagen actual
            self.current_image_index = self.filtered_images.index(image_data)
            
            # Crear interfaz del visor
            self._create_image_viewer_ui(image_data)
            
        except Exception as e:
            logger.error(f"Error mostrando visor de imagen: {e}")
            messagebox.showerror("Error", f"Error mostrando imagen: {e}")
    
    def _create_image_viewer_ui(self, image_data):
        """Crear interfaz del visor de imagen"""
        # Frame principal
        main_frame = ttk.Frame(self.image_viewer_window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Panel superior - Controles
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill='x', pady=(0, 10))
        
        # Botones de navegación
        nav_frame = ttk.Frame(controls_frame)
        nav_frame.pack(side='left')
        
        prev_btn = ttk.Button(nav_frame, text="◀ Anterior", command=self.prev_image)
        prev_btn.pack(side='left', padx=2)
        
        self.image_counter_label = ttk.Label(nav_frame, text="")
        self.image_counter_label.pack(side='left', padx=10)
        
        next_btn = ttk.Button(nav_frame, text="Siguiente ▶", command=self.next_image)
        next_btn.pack(side='left', padx=2)
        
        # Botones de acción
        actions_frame = ttk.Frame(controls_frame)
        actions_frame.pack(side='right')
        
        ttk.Button(actions_frame, text="📤 Exportar", 
                  command=lambda: self.export_image(image_data)).pack(side='left', padx=2)
        ttk.Button(actions_frame, text="ℹ️ Información", 
                  command=lambda: self.show_image_info(image_data)).pack(side='left', padx=2)
        ttk.Button(actions_frame, text="❌ Cerrar", 
                  command=self.image_viewer_window.destroy).pack(side='left', padx=2)
        
        # Panel de imagen
        image_frame = ttk.Frame(main_frame)
        image_frame.pack(fill='both', expand=True)
        
        # Canvas para la imagen
        self.image_canvas = tk.Canvas(image_frame, bg='white')
        self.image_canvas.pack(fill='both', expand=True)
        
        # Cargar y mostrar imagen
        self._load_and_display_image(image_data)
        
        # Panel inferior - Información
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill='x', pady=(10, 0))
        
        # Información de la imagen
        file_name = Path(image_data.get('file_path', '')).name
        caption = image_data.get('caption', 'Sin descripción')
        
        ttk.Label(info_frame, text=f"📁 {file_name}", font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        ttk.Label(info_frame, text=f"📝 {caption}", font=('Segoe UI', 9)).pack(anchor='w')
        
        # Actualizar contador
        self._update_image_counter()
    
    def _load_and_display_image(self, image_data):
        """Cargar y mostrar imagen en el visor"""
        try:
            file_path = image_data.get('file_path', '')
            if not file_path or not Path(file_path).exists():
                self.image_canvas.create_text(400, 300, text="❌ Imagen no encontrada", 
                                            font=('Segoe UI', 14), fill='red')
                return
            
            # Cargar imagen
            with Image.open(file_path) as img:
                # Obtener tamaño del canvas
                self.image_canvas.update()
                canvas_width = self.image_canvas.winfo_width()
                canvas_height = self.image_canvas.winfo_height()
                
                if canvas_width <= 1 or canvas_height <= 1:
                    # Canvas aún no está listo, programar para más tarde
                    self.image_viewer_window.after(100, lambda: self._load_and_display_image(image_data))
                    return
                
                # Calcular tamaño para ajustar a canvas
                img_width, img_height = img.size
                scale = min(canvas_width / img_width, canvas_height / img_height, 1.0)
                
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                
                # Redimensionar imagen
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Convertir a PhotoImage
                photo = ImageTk.PhotoImage(img)
                
                # Limpiar canvas
                self.image_canvas.delete("all")
                
                # Mostrar imagen centrada
                x = (canvas_width - new_width) // 2
                y = (canvas_height - new_height) // 2
                self.image_canvas.create_image(x, y, anchor='nw', image=photo)
                
                # Mantener referencia
                self.image_canvas.image = photo
                
        except Exception as e:
            logger.error(f"Error cargando imagen: {e}")
            self.image_canvas.create_text(400, 300, text=f"❌ Error cargando imagen: {e}", 
                                        font=('Segoe UI', 12), fill='red')
    
    def prev_image(self):
        """Imagen anterior en el visor"""
        if self.current_image_index > 0:
            self.current_image_index -= 1
            image_data = self.filtered_images[self.current_image_index]
            self._load_and_display_image(image_data)
            self._update_image_counter()
    
    def next_image(self):
        """Imagen siguiente en el visor"""
        if self.current_image_index < len(self.filtered_images) - 1:
            self.current_image_index += 1
            image_data = self.filtered_images[self.current_image_index]
            self._load_and_display_image(image_data)
            self._update_image_counter()
    
    def _update_image_counter(self):
        """Actualizar contador de imágenes"""
        if hasattr(self, 'image_counter_label'):
            current = self.current_image_index + 1
            total = len(self.filtered_images)
            self.image_counter_label.config(text=f"{current} de {total}")
    
    def export_image(self, image_data):
        """Exportar imagen"""
        try:
            file_path = image_data.get('file_path', '')
            if not file_path or not Path(file_path).exists():
                messagebox.showerror("Error", "Archivo de imagen no encontrado")
                return
            
            # Seleccionar destino
            dest_path = filedialog.asksaveasfilename(
                title="Exportar Imagen",
                defaultextension=Path(file_path).suffix,
                filetypes=[
                    ("Imágenes", "*.jpg;*.jpeg;*.png;*.bmp;*.tiff"),
                    ("Todos los archivos", "*.*")
                ],
                initialfilename=Path(file_path).name
            )
            
            if dest_path:
                # Copiar archivo
                import shutil
                shutil.copy2(file_path, dest_path)
                messagebox.showinfo("Éxito", f"Imagen exportada a:\n{dest_path}")
                
        except Exception as e:
            logger.error(f"Error exportando imagen: {e}")
            messagebox.showerror("Error", f"Error exportando imagen: {e}")
    
    def show_image_info(self, image_data):
        """Mostrar información detallada de la imagen"""
        try:
            info_window = tk.Toplevel(self.image_viewer_window)
            info_window.title("Información de la Imagen")
            info_window.geometry("500x400")
            
            # Crear notebook para organizar información
            notebook = ttk.Notebook(info_window)
            notebook.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Tab información general
            general_tab = ttk.Frame(notebook)
            notebook.add(general_tab, text="📋 General")
            
            general_text = tk.Text(general_tab, wrap=tk.WORD)
            general_text.pack(fill='both', expand=True, padx=10, pady=10)
            
            # Formatear información
            info_text = f"""📁 INFORMACIÓN DEL ARCHIVO
Archivo: {Path(image_data.get('file_path', '')).name}
Ruta: {image_data.get('file_path', 'N/A')}
ID: {image_data.get('id', 'N/A')}
Tamaño: {image_data.get('tamano_bytes', 0):,} bytes
Dimensiones: {image_data.get('ancho', 0)} x {image_data.get('alto', 0)} píxeles
Formato: {image_data.get('formato', 'N/A')}

📅 FECHAS
Creación: {image_data.get('fecha_creacion', 'N/A')}
Procesamiento: {image_data.get('fecha_procesamiento', 'N/A')}
Actualización: {image_data.get('fecha_actualizacion', 'N/A')}

🤖 PROCESAMIENTO IA
Modelo: {image_data.get('modelo_ia_usado', 'N/A')}
Estado: {image_data.get('estado', 'N/A')}
Confianza: {image_data.get('confianza_promedio', 'N/A')}
"""
            
            general_text.insert(1.0, info_text)
            general_text.config(state='disabled')
            
            # Tab descripción
            desc_tab = ttk.Frame(notebook)
            notebook.add(desc_tab, text="📝 Descripción")
            
            desc_text = tk.Text(desc_tab, wrap=tk.WORD)
            desc_text.pack(fill='both', expand=True, padx=10, pady=10)
            
            caption = image_data.get('caption', 'Sin descripción disponible')
            desc_text.insert(1.0, caption)
            desc_text.config(state='disabled')
            
            # Tab keywords
            keywords_tab = ttk.Frame(notebook)
            notebook.add(keywords_tab, text="🏷️ Keywords")
            
            keywords_text = tk.Text(keywords_tab, wrap=tk.WORD)
            keywords_text.pack(fill='both', expand=True, padx=10, pady=10)
            
            keywords = image_data.get('keywords', [])
            keywords_str = ', '.join(keywords) if keywords else 'Sin keywords'
            keywords_text.insert(1.0, keywords_str)
            keywords_text.config(state='disabled')
            
        except Exception as e:
            logger.error(f"Error mostrando información: {e}")
            messagebox.showerror("Error", f"Error mostrando información: {e}")
    
    def update_pagination(self):
        """Actualizar controles de paginación"""
        total_images = len(self.filtered_images)
        total_pages = (total_images + self.images_per_page - 1) // self.images_per_page
        current_page_display = self.current_page + 1
        
        # Actualizar etiquetas
        start_image = self.current_page * self.images_per_page + 1
        end_image = min((self.current_page + 1) * self.images_per_page, total_images)
        
        self.page_label.config(text=f"Página {current_page_display} de {total_pages}")
        
        # Habilitar/deshabilitar botones
        self.prev_btn.config(state='normal' if self.current_page > 0 else 'disabled')
        self.next_btn.config(state='normal' if self.current_page < total_pages - 1 else 'disabled')
    
    def update_info(self):
        """Actualizar información de la galería"""
        total_images = len(self.filtered_images)
        self.info_label.config(text=f"Mostrando {total_images} imágenes")
    
    def prev_page(self):
        """Página anterior"""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_gallery_display()
            self.update_pagination()
    
    def next_page(self):
        """Página siguiente"""
        total_pages = (len(self.filtered_images) + self.images_per_page - 1) // self.images_per_page
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.update_gallery_display()
            self.update_pagination()
    
    def refresh_gallery(self):
        """Actualizar galería"""
        self.load_images()
    
    def _on_mousewheel(self, event):
        """Manejar scroll del mouse"""
        if event.delta:
            self.gallery_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        elif event.num == 4:
            self.gallery_canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.gallery_canvas.yview_scroll(1, "units")
    
    def cleanup(self):
        """Limpiar recursos"""
        try:
            # Cerrar ventana de visor si está abierta
            if self.image_viewer_window and self.image_viewer_window.winfo_exists():
                self.image_viewer_window.destroy()
            
            # Limpiar thumbnails
            self.thumbnails.clear()
            
        except Exception as e:
            logger.error(f"Error en cleanup: {e}")


# Función de utilidad para crear galería
def create_enhanced_gallery(parent, db_manager=None) -> EnhancedGallery:
    """
    Crear una instancia de la galería mejorada
    
    Args:
        parent: Widget padre
        db_manager: Instancia del gestor de base de datos v2.0
        
    Returns:
        Instancia de EnhancedGallery
    """
    return EnhancedGallery(parent, db_manager)


if __name__ == "__main__":
    # Ejemplo de uso
    root = tk.Tk()
    root.title("Galería Mejorada - StockPrep Pro v2.0")
    root.geometry("1200x800")
    
    # Crear galería
    gallery = create_enhanced_gallery(root)
    
    # Configurar cierre
    def on_closing():
        gallery.cleanup()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Ejecutar
    root.mainloop()

