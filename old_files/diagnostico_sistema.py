#!/usr/bin/env python3
"""
Script de Diagnóstico del Sistema - StockPrep Pro v2.0
Verifica que todos los componentes estén funcionando correctamente
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Añadir src al path
sys.path.append('src')

def print_header(title):
    """Imprime un encabezado formateado"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def check_dependencies():
    """Verifica las dependencias del sistema"""
    print_header("VERIFICACIÓN DE DEPENDENCIAS")
    
    dependencies = [
        ('tkinter', 'Interfaz gráfica básica'),
        ('PIL', 'Procesamiento de imágenes'),
        ('torch', 'PyTorch para Florence-2'),
        ('transformers', 'Modelos de Hugging Face'),
        ('yake', 'Extracción de keywords'),
        ('sqlite3', 'Base de datos'),
        ('pathlib', 'Manejo de rutas'),
        ('json', 'Procesamiento JSON'),
        ('csv', 'Exportación CSV')
    ]
    
    results = []
    for dep, desc in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep:<15} - {desc}")
            results.append(True)
        except ImportError:
            print(f"❌ {dep:<15} - {desc} (FALTANTE)")
            results.append(False)
    
    # Verificar dependencias opcionales
    try:
        import PySide6
        print(f"✅ {'PySide6':<15} - Interfaz moderna (OPCIONAL)")
    except ImportError:
        print(f"⚠️ {'PySide6':<15} - Interfaz moderna (OPCIONAL - No instalado)")
    
    return all(results)

def check_core_modules():
    """Verifica los módulos del core"""
    print_header("VERIFICACIÓN DE MÓDULOS DEL CORE")
    
    modules = [
        ('core.sqlite_database', 'SQLiteImageDatabase'),
        ('core.model_manager', 'Florence2Manager'),
        ('core.image_processor', 'ImageProcessor'),
        ('utils.keyword_extractor', 'KeywordExtractor'),
        ('output.output_handler_v2', 'OutputHandlerV2')
    ]
    
    results = []
    for module, class_name in modules:
        try:
            mod = __import__(module, fromlist=[class_name])
            cls = getattr(mod, class_name)
            print(f"✅ {module:<25} - {class_name}")
            results.append(True)
        except (ImportError, AttributeError) as e:
            print(f"❌ {module:<25} - {class_name} (ERROR: {e})")
            results.append(False)
    
    return all(results)

def check_gui_modules():
    """Verifica los módulos de GUI"""
    print_header("VERIFICACIÓN DE MÓDULOS GUI")
    
    gui_modules = [
        ('gui.inicio_gui', 'StockPrepStartupApp'),
        ('gui.modern_gui_stockprep', 'StockPrepApp'),
        ('gui.database_gui', 'DatabaseManagerApp')
    ]
    
    results = []
    for module, class_name in gui_modules:
        try:
            mod = __import__(module, fromlist=[class_name])
            cls = getattr(mod, class_name)
            print(f"✅ {module:<25} - {class_name}")
            results.append(True)
        except (ImportError, AttributeError) as e:
            print(f"❌ {module:<25} - {class_name} (ERROR: {e})")
            results.append(False)
    
    return all(results)

def check_database():
    """Verifica la base de datos"""
    print_header("VERIFICACIÓN DE BASE DE DATOS")
    
    try:
        from core.sqlite_database import SQLiteImageDatabase
        
        # Crear instancia de prueba
        db = SQLiteImageDatabase()
        print(f"✅ Base de datos inicializada: {db.db_path}")
        
        # Verificar que el archivo existe
        db_path = Path(db.db_path)
        if db_path.exists():
            size = db_path.stat().st_size
            print(f"✅ Archivo de BD existe: {size} bytes")
        else:
            print(f"⚠️ Archivo de BD no existe (se creará al usarse)")
        
        # Probar estadísticas
        stats = db.obtener_estadisticas_globales()
        print(f"✅ Estadísticas obtenidas: {stats.get('total_imagenes_procesadas', 0)} imágenes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        return False

def check_files():
    """Verifica archivos importantes"""
    print_header("VERIFICACIÓN DE ARCHIVOS")
    
    important_files = [
        ('main.py', 'Archivo principal'),
        ('stockprep_icon.ico', 'Icono de la aplicación'),
        ('src/gui/inicio_gui.py', 'GUI de inicio'),
        ('src/gui/modern_gui_stockprep.py', 'GUI de reconocimiento'),
        ('src/gui/database_gui.py', 'GUI de base de datos'),
        ('src/core/model_manager.py', 'Gestor de modelo'),
        ('src/core/sqlite_database.py', 'Base de datos'),
        ('src/output/output_handler_v2.py', 'Manejador de salidas')
    ]
    
    results = []
    for file_path, desc in important_files:
        path = Path(file_path)
        if path.exists():
            size = path.stat().st_size
            print(f"✅ {file_path:<35} - {desc} ({size} bytes)")
            results.append(True)
        else:
            print(f"❌ {file_path:<35} - {desc} (FALTANTE)")
            results.append(False)
    
    return all(results)

def check_model_compatibility():
    """Verifica compatibilidad del modelo"""
    print_header("VERIFICACIÓN DE COMPATIBILIDAD DEL MODELO")
    
    try:
        import torch
        print(f"✅ PyTorch versión: {torch.__version__}")
        
        # Verificar CUDA
        if torch.cuda.is_available():
            gpu_count = torch.cuda.device_count()
            current_device = torch.cuda.current_device()
            gpu_name = torch.cuda.get_device_name(current_device)
            print(f"✅ CUDA disponible: {gpu_count} GPU(s)")
            print(f"✅ GPU actual: {gpu_name}")
        else:
            print(f"⚠️ CUDA no disponible - Se usará CPU")
        
        # Verificar transformers
        import transformers
        print(f"✅ Transformers versión: {transformers.__version__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando modelo: {e}")
        return False

def run_basic_functionality_test():
    """Ejecuta una prueba básica de funcionalidad"""
    print_header("PRUEBA BÁSICA DE FUNCIONALIDAD")
    
    try:
        # Probar base de datos
        from core.sqlite_database import SQLiteImageDatabase
        db = SQLiteImageDatabase()
        print("✅ Base de datos: OK")
        
        # Probar extractor de keywords
        from utils.keyword_extractor import KeywordExtractor
        extractor = KeywordExtractor()
        keywords = extractor.extract_keywords("Esta es una prueba de extracción de palabras clave")
        print(f"✅ Extractor de keywords: {len(keywords)} keywords extraídas")
        
        # Probar output handler
        from output.output_handler_v2 import OutputHandlerV2
        handler = OutputHandlerV2()
        print("✅ Output handler: OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de funcionalidad: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_report():
    """Genera un reporte completo del sistema"""
    print_header("REPORTE DEL SISTEMA")
    
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python: {sys.version}")
    print(f"💻 Plataforma: {sys.platform}")
    print(f"📁 Directorio actual: {os.getcwd()}")
    print(f"🛣️ Python path: {sys.executable}")

def main():
    """Función principal de diagnóstico"""
    print("🚀 StockPrep Pro v2.0 - Diagnóstico del Sistema")
    print(f"Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Ejecutar todas las verificaciones
    tests = [
        ("Dependencias", check_dependencies),
        ("Módulos Core", check_core_modules),
        ("Módulos GUI", check_gui_modules),
        ("Base de Datos", check_database),
        ("Archivos", check_files),
        ("Compatibilidad Modelo", check_model_compatibility),
        ("Funcionalidad Básica", run_basic_functionality_test)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error ejecutando {test_name}: {e}")
            results.append((test_name, False))
    
    # Generar reporte final
    generate_report()
    
    print_header("RESUMEN FINAL")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    total = len(results)
    percentage = (passed / total) * 100
    
    print(f"\n📊 Resultado: {passed}/{total} pruebas pasaron ({percentage:.1f}%)")
    
    if percentage == 100:
        print("🎉 ¡Excelente! El sistema está completamente funcional.")
    elif percentage >= 80:
        print("✅ El sistema está mayormente funcional. Revisa los errores menores.")
    elif percentage >= 60:
        print("⚠️ El sistema tiene algunos problemas. Revisa los errores.")
    else:
        print("❌ El sistema tiene problemas significativos. Revisa la instalación.")
    
    print(f"\nPara ejecutar la aplicación: python main.py")
    print(f"Para más ayuda, consulta: README_NUEVA_ESTRUCTURA.md")

if __name__ == "__main__":
    main() 