"""
Ejemplo de uso del SafeImageManager - SOLUCIÓN COMPLETA
"""

import tkinter as tk
from tkinter import ttk
from utils.safe_image_manager import create_safe_photoimage, cleanup_photoimage, shutdown_image_manager

class ExampleApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Ejemplo SafeImageManager")
        
        # Label para mostrar imagen
        self.image_label = ttk.Label(self.root, text="Selecciona una imagen")
        self.image_label.pack(pady=20)
        
        # Botón para cargar imagen
        ttk.Button(self.root, text="Cargar Imagen", 
                  command=self.load_image).pack(pady=10)
        
        # Configurar cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def load_image(self):
        """Carga una imagen usando SafeImageManager - SIN ERRORES PYIMAGE"""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        
        if file_path:
            # Limpiar imagen anterior
            if hasattr(self.image_label, '_image_key'):
                cleanup_photoimage(self.image_label._image_key)
            
            # USAR SAFEIMAGEMANAGER - Aplica todas las soluciones automáticamente
            photo, image_key = create_safe_photoimage(file_path, (300, 300))
            
            if photo and image_key:
                self.image_label.config(image=photo, text="")
                self.image_label._image_key = image_key
                print(f"✅ Imagen cargada exitosamente: {file_path}")
            else:
                self.image_label.config(text="❌ Error cargando imagen")
                print(f"❌ No se pudo cargar: {file_path}")
    
    def on_closing(self):
        """Cierre seguro de la aplicación"""
        # Limpiar imagen actual
        if hasattr(self.image_label, '_image_key'):
            cleanup_photoimage(self.image_label._image_key)
        
        # Cerrar SafeImageManager
        shutdown_image_manager()
        
        # Cerrar aplicación
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ExampleApp()
    app.run()
