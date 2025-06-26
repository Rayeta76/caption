"""
Interfaz moderna "Florence-2 Image Captioning Pro".
Diseño oscuro con acentos coloridos y manejo de estados.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
from PIL import Image, ImageTk
import platform

# Módulos locales
from core.model_manager import Florence2Manager
from core.image_processor import ImageProcessor

# Paleta de colores
COLORS = {
    'bg_primary': '#1a1a2e',
    'bg_secondary': '#16213e',
    'bg_card': '#0f3460',
    'accent_blue': '#0066cc',
    'accent_purple': '#8b5cf6',
    'success': '#10b981',
    'warning': '#f59e0b',
    'danger': '#ef4444',
    'text_primary': '#ffffff',
    'text_secondary': '#94a3b8',
    'border': '#374151'
}

# Estados del botón cargar modelo
ESTADOS_BOTON = {
    'inicial': {'bg': '#0066cc', 'text': '🤖 Cargar Modelo', 'fg': 'white'},
    'cargando': {'bg': '#f59e0b', 'text': '⏳ Cargando...', 'fg': 'white'},
    'listo': {'bg': '#10b981', 'text': '✅ Modelo Listo', 'fg': 'white'},
    'error': {'bg': '#ef4444', 'text': '❌ Error', 'fg': 'white'},
}


class CaptionProApp:
    """Aplicación principal."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Florence-2 Image Captioning Pro")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)

        font_name = 'Segoe UI' if platform.system() == 'Windows' else 'Arial'

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=COLORS['bg_primary'])
        style.configure('Header.TLabel', background=COLORS['bg_primary'],
                        foreground=COLORS['text_primary'], font=(font_name, 18, 'bold'))
        style.configure('SubHeader.TLabel', background=COLORS['bg_primary'],
                        foreground=COLORS['text_secondary'], font=(font_name, 12))
        style.configure('Card.TFrame', background=COLORS['bg_secondary'])
        style.configure('Accent.TButton', background=COLORS['accent_blue'],
                        foreground='white', font=(font_name, 10, 'bold'))
        style.map('Accent.TButton', background=[('active', COLORS['accent_purple'])])
        style.configure('Danger.TButton', background=COLORS['danger'],
                        foreground='white')
        style.configure('Success.TButton', background=COLORS['success'],
                        foreground='white')
        style.configure('Text.TLabel', background=COLORS['bg_secondary'],
                        foreground=COLORS['text_primary'], font=(font_name, 10))

        self.model_manager = Florence2Manager()
        self.processor = ImageProcessor(self.model_manager)

        self.modelo_cargado = False
        self.imagen_actual: Path | None = None
        self.resultado = None

        self._construir_interfaz(font_name)
        self._configurar_acciones()

    # ------------------------------------------------------------------
    def _construir_interfaz(self, font_name: str) -> None:
        self.root.configure(background=COLORS['bg_primary'])

        header = ttk.Frame(self.root, style='Card.TFrame', padding=10)
        header.pack(fill='x')
        ttk.Label(header, text="Florence-2 Image Captioning Pro",
                  style='Header.TLabel').pack(anchor='w')
        ttk.Label(header, text="AI-Powered Image Description Generator",
                  style='SubHeader.TLabel').pack(anchor='w')
        self.lbl_estado_modelo = ttk.Label(header, text="Modelo no cargado",
                                           style='SubHeader.TLabel')
        self.lbl_estado_modelo.pack(anchor='e')

        main = ttk.Frame(self.root)
        main.pack(fill='both', expand=True, padx=10, pady=10)
        main.columnconfigure(0, weight=2)
        main.columnconfigure(1, weight=3)
        main.rowconfigure(0, weight=1)

        # Izquierda
        left = ttk.Frame(main, style='Card.TFrame', padding=10)
        left.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
        left.rowconfigure(1, weight=1)
        self.preview = ttk.Label(left, text="Arrastra o selecciona una imagen",
                                 style='Text.TLabel', anchor='center')
        self.preview.grid(row=0, column=0, sticky='nsew')
        self.btn_select = ttk.Button(left, text="Seleccionar Imagen",
                                     style='Accent.TButton',
                                     command=self.seleccionar_imagen)
        self.btn_select.grid(row=1, column=0, pady=10)

        # Derecha
        right = ttk.Frame(main, style='Card.TFrame', padding=10)
        right.grid(row=0, column=1, sticky='nsew', padx=(5, 0))
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)
        self.txt_resultado = tk.Text(right, height=10, bg=COLORS['bg_primary'],
                                     fg=COLORS['text_primary'], wrap='word',
                                     relief='flat', insertbackground='white',
                                     font=(font_name, 10))
        self.txt_resultado.grid(row=0, column=0, sticky='nsew')
        scrollbar = ttk.Scrollbar(right, command=self.txt_resultado.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.txt_resultado['yscrollcommand'] = scrollbar.set

        acciones = ttk.Frame(right, style='Card.TFrame')
        acciones.grid(row=1, column=0, columnspan=2, pady=10)
        self.btn_cargar = tk.Button(acciones, text="🤖 Cargar Modelo",
                                    command=self.cargar_modelo,
                                    **ESTADOS_BOTON['inicial'])
        self.btn_cargar.pack(side='left', padx=5)
        self.btn_generar = tk.Button(acciones, text="📝 Selecciona Imagen",
                                     state='disabled', bg=COLORS['accent_purple'],
                                     fg='white', command=self.generar_descripcion)
        self.btn_generar.pack(side='left', padx=5)
        self.btn_guardar = ttk.Button(acciones, text="Guardar Resultado",
                                      style='Accent.TButton',
                                      command=self.guardar_resultado)
        self.btn_guardar.pack(side='left', padx=5)
        self.btn_guardar.pack_forget()

        # Progreso
        self.progress = ttk.Progressbar(self.root, mode='determinate', value=0)
        self.progress.pack(fill='x', padx=10, pady=(0, 10))

        footer = ttk.Frame(self.root, style='Card.TFrame', padding=5)
        footer.pack(fill='x')
        self.lbl_info = ttk.Label(footer, text="GPU/CPU Info", style='SubHeader.TLabel')
        self.lbl_info.pack(side='left')
        self.lbl_tiempo = ttk.Label(footer, text="", style='SubHeader.TLabel')
        self.lbl_tiempo.pack(side='right')

    # ------------------------------------------------------------------
    def _configurar_acciones(self) -> None:
        self.root.bind('<Control-o>', lambda e: self.seleccionar_imagen())
        self.root.bind('<F5>', lambda e: self.generar_descripcion())

    # ------------------------------------------------------------------
    def seleccionar_imagen(self) -> None:
        archivo = filedialog.askopenfilename(filetypes=[('Imagenes', '*.png *.jpg *.jpeg *.bmp')])
        if archivo:
            self.imagen_actual = Path(archivo)
            image = Image.open(archivo)
            image.thumbnail((400, 400))
            img = ImageTk.PhotoImage(image)
            self.preview.configure(image=img, text='')
            self.preview.image = img
            self.btn_generar.config(state='normal', text='🚀 Generar Descripción',
                                     bg=COLORS['accent_purple'])
            self.txt_resultado.delete('1.0', 'end')
            self.btn_guardar.pack_forget()

    # ------------------------------------------------------------------
    def cambiar_estado_boton(self, estado: str) -> None:
        props = ESTADOS_BOTON[estado]
        self.btn_cargar.config(bg=props['bg'], fg=props['fg'], text=props['text'])

    # ------------------------------------------------------------------
    def cargar_modelo(self) -> None:
        def tarea():
            self.cambiar_estado_boton('cargando')
            self.lbl_estado_modelo.config(text='Cargando modelo...')
            ok = self.model_manager.cargar_modelo(lambda m: None)
            if ok:
                self.modelo_cargado = True
                self.cambiar_estado_boton('listo')
                self.lbl_estado_modelo.config(text='Modelo cargado')
            else:
                self.cambiar_estado_boton('error')
                self.lbl_estado_modelo.config(text='Error al cargar modelo')
        threading.Thread(target=tarea, daemon=True).start()

    # ------------------------------------------------------------------
    def generar_descripcion(self) -> None:
        if not self.imagen_actual:
            return
        if not self.modelo_cargado:
            messagebox.showwarning('Modelo', 'Carga el modelo primero')
            return

        def tarea():
            self.btn_generar.config(text='⚡ Procesando...', state='disabled', bg=COLORS['accent_blue'])
            self.progress.start(10)
            resultado = self.processor.procesar_imagen(str(self.imagen_actual))
            self.progress.stop()
            if 'error' in resultado:
                messagebox.showerror('Error', resultado['error'])
                self.btn_generar.config(state='normal', text='🚀 Generar Descripción', bg=COLORS['accent_purple'])
                return
            self.resultado = resultado
            self.txt_resultado.delete('1.0', 'end')
            self.txt_resultado.insert('end', resultado.get('descripcion', ''))
            self.btn_generar.config(text='✅ Descripción Lista', bg=COLORS['success'])
            self.btn_guardar.pack(side='left', padx=5)
        threading.Thread(target=tarea, daemon=True).start()

    # ------------------------------------------------------------------
    def guardar_resultado(self) -> None:
        if not self.resultado:
            return
        archivo = filedialog.asksaveasfilename(defaultextension='.txt',
                                               filetypes=[('Texto', '*.txt')])
        if archivo:
            with open(archivo, 'w', encoding='utf-8') as f:
                f.write(self.resultado.get('descripcion', ''))
            messagebox.showinfo('Guardado', 'Resultado guardado')

    # ------------------------------------------------------------------
    def run(self) -> None:
        self.root.mainloop()


if __name__ == '__main__':
    app = CaptionProApp()
    app.run()
