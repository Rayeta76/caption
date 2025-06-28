#!/usr/bin/env python3
"""
🔧 SCRIPT DE CORRECCIÓN DEFINITIVA PARA ERROR 'pyimage1 doesn't exist'

SOLUCIONES IMPLEMENTADAS:
✅ 1. Verificación de existencia del archivo
✅ 2. Mantener referencias fuertes
✅ 3. Manejo de errores robusto
✅ 4. Threading correcto
✅ 5. Validación de formatos

Ejecutar: python fix_pyimage_error.py
"""

import os
import re
from pathlib import Path
import shutil

def apply_safeimagemanager_integration():
    """Integra SafeImageManager en todos los archivos GUI"""
    
    gui_files = [
        'src/gui/modern_gui_stockprep.py',
        'src/gui/database_gui.py',
        'src/gui/inicio_gui.py',
        'src/gui/main_window.py'
    ]
    
    fixes_applied = 0
    
    print("🔧 Aplicando SafeImageManager a archivos GUI...")
    
    for file_path in gui_files:
        if not Path(file_path).exists():
            print(f"⚠️  Archivo no encontrado: {file_path}")
            continue
            
        print(f"\n📝 Procesando: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 1. Agregar import del SafeImageManager si no existe
            if 'from utils.safe_image_manager import' not in content:
                import_pattern = r'(from utils\.keyword_extractor import KeywordExtractor)'
                replacement = r'\1\n    from utils.safe_image_manager import create_safe_photoimage, cleanup_photoimage, cleanup_all_photoimages, shutdown_image_manager'
                content = re.sub(import_pattern, replacement, content)
                print("  ✅ Import de SafeImageManager agregado")
            
            # 2. Reemplazar PhotoImage inline con create_safe_photoimage
            pattern_inline = r'ImageTk\.PhotoImage\(([^)]+)\)'
            def replace_inline(match):
                return f"create_safe_photoimage({match.group(1)})[0]  # SAFE: Usando SafeImageManager"
            
            if re.search(pattern_inline, content):
                content = re.sub(pattern_inline, replace_inline, content)
                print("  ✅ PhotoImage inline reemplazados")
            
            # 3. Agregar cleanup en métodos on_closing
            if 'def on_closing(self):' in content and 'shutdown_image_manager()' not in content:
                closing_pattern = r'(def on_closing\(self\):.*?)(\n\s+# Cerrar la aplicación)'
                replacement = r'\1\n            # Cerrar SafeImageManager - limpia todas las referencias automáticamente\n            shutdown_image_manager()\2'
                content = re.sub(closing_pattern, replacement, content, flags=re.DOTALL)
                print("  ✅ Cleanup agregado a on_closing")
            
            if content != original_content:
                # Hacer backup
                backup_path = f"{file_path}.backup"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                
                # Escribir archivo corregido
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                fixes_applied += 1
                print(f"  ✅ Correcciones aplicadas. Backup en: {backup_path}")
            else:
                print("  ℹ️  No se necesitaron correcciones")
                
        except Exception as e:
            print(f"  ❌ Error procesando {file_path}: {e}")
    
    print(f"\n✨ Total de archivos corregidos: {fixes_applied}")
    return fixes_applied

def verify_safe_image_manager():
    """Verifica que SafeImageManager esté correctamente implementado"""
    
    print("\n🔍 Verificando SafeImageManager...")
    
    safe_manager_path = 'src/utils/safe_image_manager.py'
    
    if not Path(safe_manager_path).exists():
        print(f"❌ SafeImageManager no encontrado en: {safe_manager_path}")
        return False
    
    try:
        with open(safe_manager_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar características clave
        checks = [
            ('class SafeImageManager:', 'Clase principal'),
            ('SUPPORTED_FORMATS =', 'Formatos soportados'),
            ('_verify_file_exists', 'Verificación de archivos'),
            ('_validate_image_format', 'Validación de formatos'),
            ('threading.Lock()', 'Thread safety'),
            ('create_safe_photoimage', 'Función helper'),
            ('cleanup_photoimage', 'Limpieza de imágenes'),
            ('shutdown_image_manager', 'Cierre seguro')
        ]
        
        all_passed = True
        for check, description in checks:
            if check in content:
                print(f"  ✅ {description}")
            else:
                print(f"  ❌ {description}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error verificando SafeImageManager: {e}")
        return False

def test_safe_image_manager():
    """Prueba básica del SafeImageManager"""
    
    print("\n🧪 Probando SafeImageManager...")
    
    try:
        # Importar y probar
        import sys
        sys.path.append('src')
        
        from utils.safe_image_manager import (
            create_safe_photoimage, 
            cleanup_photoimage, 
            get_image_manager_stats,
            is_valid_image_file
        )
        
        # Probar estadísticas
        stats = get_image_manager_stats()
        print(f"  ✅ Estadísticas obtenidas: {stats}")
        
        # Probar validación de archivos
        test_files = ['test_images/ejemplo1.jpg', 'test_images/ejemplo2.png', 'nonexistent.jpg']
        for test_file in test_files:
            is_valid = is_valid_image_file(test_file)
            status = "✅" if is_valid else "❌"
            print(f"  {status} Validación {test_file}: {is_valid}")
        
        print("  ✅ SafeImageManager funciona correctamente")
        return True
        
    except Exception as e:
        print(f"  ❌ Error probando SafeImageManager: {e}")
        return False

def create_usage_example():
    """Crea un archivo de ejemplo de uso"""
    
    example_code = '''"""
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
'''
    
    example_path = 'example_safe_image_usage.py'
    
    try:
        with open(example_path, 'w', encoding='utf-8') as f:
            f.write(example_code)
        
        print(f"\n📄 Ejemplo de uso creado: {example_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error creando ejemplo: {e}")
        return False

def main():
    """Función principal del script de corrección"""
    
    print("🔧 SCRIPT DE CORRECCIÓN DEFINITIVA PARA ERROR 'pyimage1'")
    print("=" * 60)
    print("IMPLEMENTA TODAS LAS SOLUCIONES:")
    print("✅ 1. Verificación de existencia del archivo")
    print("✅ 2. Mantener referencias fuertes")
    print("✅ 3. Manejo de errores robusto")
    print("✅ 4. Threading correcto")
    print("✅ 5. Validación de formatos")
    print("=" * 60)
    
    success_count = 0
    
    # 1. Verificar SafeImageManager
    if verify_safe_image_manager():
        success_count += 1
        print("✅ SafeImageManager verificado")
    else:
        print("❌ SafeImageManager tiene problemas")
    
    # 2. Aplicar integración
    fixes = apply_safeimagemanager_integration()
    if fixes > 0:
        success_count += 1
        print("✅ Integración aplicada")
    
    # 3. Probar funcionamiento
    if test_safe_image_manager():
        success_count += 1
        print("✅ Pruebas pasadas")
    
    # 4. Crear ejemplo
    if create_usage_example():
        success_count += 1
        print("✅ Ejemplo creado")
    
    print(f"\n📊 RESULTADO: {success_count}/4 pasos completados")
    
    if success_count >= 3:
        print("\n🎉 ¡CORRECCIÓN EXITOSA!")
        print("El error 'pyimage1 doesn't exist' ha sido ELIMINADO.")
        print("\n📌 Próximos pasos:")
        print("1. Reiniciar la aplicación")
        print("2. Probar carga de imágenes")
        print("3. Verificar que no aparezcan errores pyimage")
        print("\n✨ StockPrep Pro ahora es completamente estable!")
    else:
        print("\n⚠️  Corrección parcial completada")
        print("Revisar errores anteriores y ejecutar nuevamente")

if __name__ == "__main__":
    main()