#!/usr/bin/env python3
"""
Script de integración para la galería mejorada
StockPrep Pro v2.0 - Integración SQLite + FTS5 + WebP BLOB

Este script integra las mejoras de galería en la aplicación existente:
- Actualiza la base de datos a v2.0
- Migra thumbnails existentes a WebP
- Integra la galería mejorada
"""

import sys
import os
import logging
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import shutil
from datetime import datetime

# Agregar src al path
sys.path.append('src')

try:
    from core.enhanced_database_manager_v2 import EnhancedDatabaseManagerV2
    from core.enhanced_database_manager import EnhancedDatabaseManager
except ImportError as e:
    print(f"Error importando módulos: {e}")
    print("Asegúrate de que los archivos estén en las ubicaciones correctas")
    sys.exit(1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GalleryIntegrator:
    """Clase para integrar la galería mejorada"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔧 Integración Galería Mejorada - StockPrep Pro v2.0")
        self.root.geometry("800x600")
        self.root.minsize(700, 500)
        
        # Configurar icono
        try:
            self.root.iconbitmap("stockprep_icon.ico")
        except:
            pass
        
        # Variables
        self.db_path = "stockprep_images.db"
        self.db_manager_v1 = None
        self.db_manager_v2 = None
        
        # Crear interfaz
        self.create_ui()
        
        # Verificar estado actual
        self.check_current_state()
    
    def create_ui(self):
        """Crear interfaz de usuario"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Título
        title_label = ttk.Label(main_frame, text="🔧 Integración Galería Mejorada", 
                               font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Información
        info_text = """
🚀 MEJORAS A INTEGRAR:

✅ SQLite + FTS5 para búsquedas súper rápidas
✅ Thumbnails WebP en BLOB para rendimiento óptimo  
✅ Vista ampliada al hacer clic en imágenes
✅ Búsqueda visual con imágenes
✅ Navegación intuitiva tipo web de stock
✅ Experiencia mejorada de usuario

🔧 PROCESO DE INTEGRACIÓN:
1. Verificar base de datos actual
2. Crear backup de seguridad
3. Migrar a base de datos v2.0
4. Generar thumbnails WebP
5. Actualizar índices FTS5
6. Probar funcionalidades
        """
        
        info_label = ttk.Label(main_frame, text=info_text, font=('Segoe UI', 10))
        info_label.pack(pady=(0, 20))
        
        # Panel de estado
        self.status_frame = ttk.LabelFrame(main_frame, text="📊 Estado Actual", padding=10)
        self.status_frame.pack(fill='x', pady=(0, 20))
        
        self.status_label = ttk.Label(self.status_frame, text="Verificando estado...", 
                                     font=('Segoe UI', 9))
        self.status_label.pack(anchor='w')
        
        # Panel de progreso
        self.progress_frame = ttk.LabelFrame(main_frame, text="🔄 Progreso", padding=10)
        self.progress_frame.pack(fill='x', pady=(0, 20))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, 
                                           maximum=100)
        self.progress_bar.pack(fill='x', pady=(0, 10))
        
        self.progress_label = ttk.Label(self.progress_frame, text="Listo para comenzar")
        self.progress_label.pack(anchor='w')
        
        # Panel de controles
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill='x')
        
        self.integrate_btn = ttk.Button(controls_frame, text="🚀 Iniciar Integración", 
                                       command=self.start_integration, state='disabled')
        self.integrate_btn.pack(side='left', padx=(0, 10))
        
        self.test_btn = ttk.Button(controls_frame, text="🧪 Probar Galería", 
                                  command=self.test_gallery, state='disabled')
        self.test_btn.pack(side='left', padx=(0, 10))
        
        ttk.Button(controls_frame, text="❌ Cerrar", 
                  command=self.root.quit).pack(side='right')
    
    def check_current_state(self):
        """Verificar estado actual de la base de datos"""
        try:
            # Verificar si existe la base de datos
            if not Path(self.db_path).exists():
                self.status_label.config(text="❌ No se encontró base de datos. Ejecuta la aplicación principal primero.")
                return
            
            # Conectar a base de datos v1
            self.db_manager_v1 = EnhancedDatabaseManager(self.db_path)
            
            # Obtener estadísticas
            stats = self.db_manager_v1.obtener_estadisticas()
            total_images = stats.get('total_imagenes', 0)
            
            if total_images == 0:
                self.status_label.config(text="⚠️ Base de datos vacía. Procesa algunas imágenes primero.")
                return
            
            # Verificar si ya está migrada
            try:
                self.db_manager_v2 = EnhancedDatabaseManagerV2(self.db_path)
                v2_stats = self.db_manager_v2.obtener_estadisticas_galeria()
                images_with_thumbnails = v2_stats.get('imagenes_con_thumbnail', 0)
                
                if images_with_thumbnails == total_images:
                    self.status_label.config(text=f"✅ Base de datos ya migrada. {total_images} imágenes con thumbnails WebP.")
                    self.integrate_btn.config(state='normal', text="🔄 Re-migrar")
                    self.test_btn.config(state='normal')
                else:
                    self.status_label.config(text=f"🔄 Migración necesaria. {total_images} imágenes, {images_with_thumbnails} con thumbnails.")
                    self.integrate_btn.config(state='normal')
            except:
                self.status_label.config(text=f"🔄 Migración necesaria. {total_images} imágenes encontradas.")
                self.integrate_btn.config(state='normal')
            
        except Exception as e:
            logger.error(f"Error verificando estado: {e}")
            self.status_label.config(text=f"❌ Error verificando estado: {e}")
    
    def start_integration(self):
        """Iniciar proceso de integración"""
        try:
            # Confirmar integración
            result = messagebox.askyesno(
                "Confirmar Integración",
                "¿Deseas iniciar la integración de la galería mejorada?\n\n"
                "Esto creará un backup de seguridad y migrará la base de datos.\n"
                "El proceso puede tomar varios minutos dependiendo del número de imágenes."
            )
            
            if not result:
                return
            
            # Deshabilitar botón
            self.integrate_btn.config(state='disabled')
            
            # Iniciar integración en hilo separado
            import threading
            thread = threading.Thread(target=self._integration_process, daemon=True)
            thread.start()
            
        except Exception as e:
            logger.error(f"Error iniciando integración: {e}")
            messagebox.showerror("Error", f"Error iniciando integración: {e}")
            self.integrate_btn.config(state='normal')
    
    def _integration_process(self):
        """Proceso de integración en hilo separado"""
        try:
            # Paso 1: Crear backup
            self._update_progress(10, "Creando backup de seguridad...")
            self._create_backup()
            
            # Paso 2: Inicializar base de datos v2.0
            self._update_progress(20, "Inicializando base de datos v2.0...")
            self.db_manager_v2 = EnhancedDatabaseManagerV2(self.db_path)
            
            # Paso 3: Migrar thumbnails
            self._update_progress(30, "Migrando thumbnails a WebP...")
            self._migrate_thumbnails()
            
            # Paso 4: Actualizar índices FTS5
            self._update_progress(80, "Actualizando índices FTS5...")
            self._update_fts5_indexes()
            
            # Paso 5: Verificar integración
            self._update_progress(90, "Verificando integración...")
            self._verify_integration()
            
            # Completado
            self._update_progress(100, "✅ Integración completada exitosamente!")
            
            # Habilitar botones
            self.root.after(0, lambda: self.integrate_btn.config(state='normal', text="✅ Completado"))
            self.root.after(0, lambda: self.test_btn.config(state='normal'))
            
            # Mostrar mensaje de éxito
            self.root.after(0, lambda: messagebox.showinfo(
                "Integración Completada",
                "✅ La galería mejorada se ha integrado exitosamente!\n\n"
                "Ahora puedes probar las nuevas funcionalidades:\n"
                "• Búsqueda FTS5 súper rápida\n"
                "• Thumbnails WebP optimizados\n"
                "• Vista ampliada de imágenes\n"
                "• Navegación tipo web de stock"
            ))
            
        except Exception as e:
            logger.error(f"Error en proceso de integración: {e}")
            self.root.after(0, lambda: self._update_progress(0, f"❌ Error: {e}"))
            self.root.after(0, lambda: self.integrate_btn.config(state='normal'))
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error en integración: {e}"))
    
    def _update_progress(self, value, message):
        """Actualizar progreso"""
        self.root.after(0, lambda: self.progress_var.set(value))
        self.root.after(0, lambda: self.progress_label.config(text=message))
        self.root.after(0, lambda: self.root.update())
    
    def _create_backup(self):
        """Crear backup de seguridad"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"stockprep_images_backup_{timestamp}.db"
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Backup creado: {backup_path}")
        except Exception as e:
            logger.warning(f"Error creando backup: {e}")
    
    def _migrate_thumbnails(self):
        """Migrar thumbnails existentes a WebP"""
        try:
            # Obtener imágenes sin thumbnails
            with self.db_manager_v2.db_path as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, ruta_completa FROM imagenes WHERE thumbnail_webp IS NULL")
                imagenes_sin_thumbnail = cursor.fetchall()
                
                total = len(imagenes_sin_thumbnail)
                for i, (imagen_id, ruta_completa) in enumerate(imagenes_sin_thumbnail):
                    try:
                        if Path(ruta_completa).exists():
                            # Crear thumbnail WebP
                            thumbnail_webp = self.db_manager_v2._create_webp_thumbnail(ruta_completa)
                            if thumbnail_webp:
                                cursor.execute(
                                    "UPDATE imagenes SET thumbnail_webp = ?, thumbnail_size = ? WHERE id = ?",
                                    (thumbnail_webp, len(thumbnail_webp), imagen_id)
                                )
                                
                                # Actualizar FTS5
                                self.db_manager_v2._update_fts5(cursor, imagen_id)
                        
                        # Actualizar progreso
                        progress = 30 + (i / total) * 40
                        self._update_progress(progress, f"Migrando thumbnail {i+1}/{total}...")
                        
                    except Exception as e:
                        logger.warning(f"Error migrando thumbnail {ruta_completa}: {e}")
                
                conn.commit()
                logger.info(f"Migración completada: {total} thumbnails")
                
        except Exception as e:
            logger.error(f"Error en migración de thumbnails: {e}")
            raise
    
    def _update_fts5_indexes(self):
        """Actualizar índices FTS5"""
        try:
            # Esto se hace automáticamente en la migración
            logger.info("Índices FTS5 actualizados")
        except Exception as e:
            logger.error(f"Error actualizando índices FTS5: {e}")
            raise
    
    def _verify_integration(self):
        """Verificar que la integración fue exitosa"""
        try:
            stats = self.db_manager_v2.obtener_estadisticas_galeria()
            total_images = stats.get('total_imagenes', 0)
            images_with_thumbnails = stats.get('imagenes_con_thumbnail', 0)
            
            if images_with_thumbnails == total_images and total_images > 0:
                logger.info(f"Verificación exitosa: {total_images} imágenes con thumbnails WebP")
            else:
                raise Exception(f"Verificación fallida: {total_images} imágenes, {images_with_thumbnails} con thumbnails")
                
        except Exception as e:
            logger.error(f"Error en verificación: {e}")
            raise
    
    def test_gallery(self):
        """Probar la galería mejorada"""
        try:
            # Importar y ejecutar script de prueba
            import subprocess
            subprocess.Popen([sys.executable, "test_enhanced_gallery.py"])
            
        except Exception as e:
            logger.error(f"Error ejecutando prueba: {e}")
            messagebox.showerror("Error", f"Error ejecutando prueba: {e}")
    
    def run(self):
        """Ejecutar la aplicación"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("Aplicación cerrada por el usuario")
        except Exception as e:
            logger.error(f"Error ejecutando aplicación: {e}")
            messagebox.showerror("Error", f"Error ejecutando aplicación: {e}")

def main():
    """Función principal"""
    print("=" * 60)
    print("🔧 INTEGRACIÓN GALERÍA MEJORADA - STOCKPREP PRO v2.0")
    print("=" * 60)
    print("🚀 Mejoras a integrar:")
    print("   • SQLite + FTS5 para búsquedas súper rápidas")
    print("   • Thumbnails WebP en BLOB para rendimiento óptimo")
    print("   • Vista ampliada al hacer clic en imágenes")
    print("   • Búsqueda visual con imágenes")
    print("   • Navegación intuitiva tipo web de stock")
    print("=" * 60)
    
    try:
        app = GalleryIntegrator()
        app.run()
    except Exception as e:
        print(f"❌ Error ejecutando aplicación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

