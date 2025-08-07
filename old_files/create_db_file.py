#!/usr/bin/env python3
"""
Script de prueba para el sistema de base de datos SQLite de StockPrep Pro v2.0
Demuestra todas las funcionalidades del EnhancedDatabaseManager
"""

import os
import sys
import logging
from pathlib import Path

# Agregar el directorio src al path para importar módulos
sys.path.append(str(Path(__file__).parent / "src"))

from src.core.enhanced_database_manager import EnhancedDatabaseManager, procesar_directorio_imagenes

def configurar_logging():
    """Configurar el sistema de logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('database_test.log'),
            logging.StreamHandler()
        ]
    )

def crear_archivos_prueba():
    """Crear archivos de prueba para demostrar el sistema"""
    # Crear directorio de prueba
    test_dir = Path("test_images")
    test_dir.mkdir(exist_ok=True)
    
    # Crear archivos de ejemplo (simulados)
    archivos_prueba = [
        {
            'imagen': 'ejemplo1.jpg',
            'caption': 'Una hermosa imagen de paisaje con montañas y lago',
            'keywords': ['paisaje', 'montañas', 'lago', 'naturaleza', 'cielo'],
            'objects': [
                {'nombre': 'montaña', 'bbox': [10, 20, 100, 150], 'confianza': 0.95},
                {'nombre': 'lago', 'bbox': [150, 200, 300, 280], 'confianza': 0.88},
                {'nombre': 'cielo', 'bbox': [0, 0, 400, 100], 'confianza': 0.92}
            ]
        },
        {
            'imagen': 'ejemplo2.png',
            'caption': 'Retrato de una persona sonriendo en un jardín',
            'keywords': ['retrato', 'persona', 'sonrisa', 'jardín', 'flores'],
            'objects': [
                {'nombre': 'persona', 'bbox': [50, 30, 200, 300], 'confianza': 0.97},
                {'nombre': 'flores', 'bbox': [220, 250, 350, 320], 'confianza': 0.85}
            ]
        },
        {
            'imagen': 'ejemplo3.jpg',
            'caption': 'Arquitectura moderna con edificios de cristal',
            'keywords': ['arquitectura', 'edificios', 'cristal', 'moderno', 'ciudad'],
            'objects': [
                {'nombre': 'edificio', 'bbox': [0, 50, 400, 500], 'confianza': 0.93},
                {'nombre': 'cristal', 'bbox': [100, 100, 300, 400], 'confianza': 0.89}
            ]
        }
    ]
    
    # Crear archivos de prueba
    for archivo in archivos_prueba:
        # Crear archivo de imagen simulado (vacío)
        imagen_path = test_dir / archivo['imagen']
        with open(imagen_path, 'wb') as f:
            # Escribir un pequeño archivo binario simulado
            f.write(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)  # Header PNG falso
        
        # Crear archivos TXT correspondientes
        nombre_base = imagen_path.stem
        
        # Archivo caption
        caption_file = test_dir / f"{nombre_base}_caption.txt"
        with open(caption_file, 'w', encoding='utf-8') as f:
            f.write(archivo['caption'])
        
        # Archivo keywords
        keywords_file = test_dir / f"{nombre_base}_keywords.txt"
        with open(keywords_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(archivo['keywords']))
        
        # Archivo objects
        objects_file = test_dir / f"{nombre_base}_objects.txt"
        with open(objects_file, 'w', encoding='utf-8') as f:
            import json
            f.write(json.dumps(archivo['objects'], indent=2, ensure_ascii=False))
    
    print(f"✅ Archivos de prueba creados en: {test_dir}")
    return test_dir

def probar_insercion_automatica(db_manager, test_dir):
    """Probar la inserción automática desde archivos TXT"""
    print("\n🔄 Probando inserción automática...")
    
    # Obtener todas las imágenes del directorio de prueba
    imagenes = list(test_dir.glob("*.jpg")) + list(test_dir.glob("*.png"))
    
    for imagen in imagenes:
        exito = db_manager.insertar_imagen_automatica(str(imagen), str(test_dir))
        if exito:
            print(f"✅ Insertada automáticamente: {imagen.name}")
        else:
            print(f"❌ Error al insertar: {imagen.name}")

def probar_insercion_manual(db_manager):
    """Probar la inserción manual de imágenes"""
    print("\n🔄 Probando inserción manual...")
    
    # Crear una imagen de prueba manual
    manual_image = Path("test_images/manual_test.jpg")
    with open(manual_image, 'wb') as f:
        f.write(b'\xFF\xD8\xFF' + b'\x00' * 50)  # Header JPEG falso
    
    exito = db_manager.insertar_imagen_manual(
        str(manual_image),
        titulo="Imagen de prueba manual",
        descripcion="Esta imagen fue insertada manualmente para pruebas",
        caption="Imagen de prueba creada manualmente",
        keywords=["prueba", "manual", "test", "database"],
        objetos=[
            {"nombre": "objeto_test", "bbox": [10, 10, 50, 50], "confianza": 0.90}
        ],
        estado="completed",
        modelo_usado="Manual",
        notas="Insertada como prueba del sistema",
        etiquetas=["test", "manual", "demo"]
    )
    
    if exito:
        print("✅ Imagen insertada manualmente con éxito")
    else:
        print("❌ Error en inserción manual")

def probar_busquedas(db_manager):
    """Probar diferentes tipos de búsquedas"""
    print("\n🔍 Probando búsquedas...")
    
    # Búsqueda básica - todas las imágenes
    todas = db_manager.buscar_imagenes()
    print(f"📊 Total de imágenes en la base de datos: {len(todas)}")
    
    # Búsqueda por estado
    completadas = db_manager.buscar_imagenes({'estado': 'completed'})
    print(f"📊 Imágenes completadas: {len(completadas)}")
    
    # Búsqueda por formato
    jpg_images = db_manager.buscar_imagenes({'formato': 'jpg'})
    print(f"📊 Imágenes JPG: {len(jpg_images)}")
    
    # Búsqueda por keyword
    paisaje_images = db_manager.buscar_imagenes({'keyword': 'paisaje'})
    print(f"📊 Imágenes con keyword 'paisaje': {len(paisaje_images)}")
    
    # Mostrar detalles de una imagen
    if todas:
        print(f"\n📋 Detalles de la primera imagen:")
        imagen = todas[0]
        print(f"   Nombre: {imagen['nombre_original']}")
        print(f"   Estado: {imagen['estado']}")
        print(f"   Caption: {imagen['caption']}")
        print(f"   Keywords: {imagen['keywords']}")
        print(f"   Objetos: {len(imagen['objetos_detectados'])} detectados")

def probar_estadisticas(db_manager):
    """Probar la generación de estadísticas"""
    print("\n📊 Generando estadísticas...")
    
    stats = db_manager.obtener_estadisticas()
    
    print(f"📈 Estadísticas de la base de datos:")
    print(f"   Total de imágenes: {stats.get('total_imagenes', 0)}")
    print(f"   Imágenes procesadas: {stats.get('imagenes_procesadas', 0)}")
    print(f"   Imágenes pendientes: {stats.get('imagenes_pendientes', 0)}")
    print(f"   Imágenes con error: {stats.get('imagenes_error', 0)}")
    
    if stats.get('por_formato'):
        print(f"   Por formato: {stats['por_formato']}")
    
    if stats.get('por_modelo_ia'):
        print(f"   Por modelo IA: {stats['por_modelo_ia']}")
    
    tamano = stats.get('tamano', {})
    if tamano.get('total_bytes'):
        total_mb = tamano['total_bytes'] / (1024 * 1024)
        print(f"   Tamaño total: {total_mb:.2f} MB")

def probar_exportacion(db_manager):
    """Probar la exportación de datos"""
    print("\n💾 Probando exportación...")
    
    # Exportar en formato JSON
    archivo_json = db_manager.exportar_datos('json')
    if archivo_json:
        print(f"✅ Datos exportados a JSON: {archivo_json}")
    
    # Exportar en formato CSV
    archivo_csv = db_manager.exportar_datos('csv')
    if archivo_csv:
        print(f"✅ Datos exportados a CSV: {archivo_csv}")

def probar_actualizacion_ia(db_manager):
    """Probar la actualización con procesamiento IA"""
    print("\n🤖 Probando actualización de procesamiento IA...")
    
    # Buscar una imagen para actualizar
    imagenes = db_manager.buscar_imagenes(limite=1)
    if imagenes:
        imagen_id = imagenes[0]['id']
        
        exito = db_manager.actualizar_procesamiento_ia(
            imagen_id=imagen_id,
            caption="Caption actualizado por IA",
            keywords=["actualizado", "ia", "florence-2", "nuevo"],
            objetos=[
                {"nombre": "objeto_actualizado", "bbox": [20, 20, 80, 80], "confianza": 0.95}
            ],
            modelo_usado="Florence-2-Updated",
            confianza=0.92
        )
        
        if exito:
            print(f"✅ Imagen ID {imagen_id} actualizada con procesamiento IA")
        else:
            print(f"❌ Error al actualizar imagen ID {imagen_id}")

def probar_procesamiento_directorio():
    """Probar el procesamiento completo de un directorio"""
    print("\n📁 Probando procesamiento de directorio completo...")
    
    test_dir = Path("test_images")
    if test_dir.exists():
        stats = procesar_directorio_imagenes(
            directorio=str(test_dir),
            output_dir=str(test_dir),
            db_path="stockprep_database.db"
        )
        
        print(f"📊 Estadísticas del procesamiento:")
        print(f"   Total encontradas: {stats['total_encontradas']}")
        print(f"   Insertadas exitosamente: {stats['insertadas_exitosamente']}")
        print(f"   Ya existían: {stats['ya_existian']}")
        print(f"   Errores: {stats['errores']}")

def limpiar_archivos_prueba():
    """Limpiar archivos de prueba"""
    print("\n🧹 Limpiando archivos de prueba...")
    
    import shutil
    
    # Eliminar directorio de prueba
    test_dir = Path("test_images")
    if test_dir.exists():
        shutil.rmtree(test_dir)
        print("✅ Directorio de prueba eliminado")
    
    # Eliminar archivos de base de datos de prueba
    db_files = ["stockprep_database.db", "test_stockprep.db"]
    for db_file in db_files:
        if Path(db_file).exists():
            os.remove(db_file)
            print(f"✅ Base de datos eliminada: {db_file}")
    
    # Eliminar archivos de exportación
    export_files = list(Path(".").glob("export_imagenes_*.json")) + list(Path(".").glob("export_imagenes_*.csv"))
    for export_file in export_files:
        export_file.unlink()
        print(f"✅ Archivo de exportación eliminado: {export_file}")

def main():
    """Función principal para ejecutar todas las pruebas"""
    print("🚀 Iniciando pruebas del sistema de base de datos SQLite")
    print("=" * 60)
    
    # Configurar logging
    configurar_logging()
    
    try:
        # Crear archivos de prueba
        test_dir = crear_archivos_prueba()
        
        # Crear gestor de base de datos
        print("\n📊 Creando gestor de base de datos...")
        db_manager = EnhancedDatabaseManager("stockprep_database.db")
        print("✅ Base de datos inicializada correctamente")
        
        # Ejecutar pruebas
        probar_insercion_automatica(db_manager, test_dir)
        probar_insercion_manual(db_manager)
        probar_busquedas(db_manager)
        probar_estadisticas(db_manager)
        probar_actualizacion_ia(db_manager)
        probar_exportacion(db_manager)
        probar_procesamiento_directorio()
        
        print("\n✅ Todas las pruebas completadas exitosamente!")
        print("=" * 60)
        
        # Preguntar si limpiar archivos
        respuesta = input("\n¿Deseas limpiar los archivos de prueba? (s/n): ").lower().strip()
        if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
            limpiar_archivos_prueba()
        else:
            print("🔧 Archivos de prueba conservados para inspección manual")
            print("   - Base de datos: stockprep_database.db")
            print("   - Directorio de prueba: test_images/")
            print("   - Archivos de exportación: export_imagenes_*.json/csv")
        
    except Exception as e:
        print(f"❌ Error durante las pruebas: {e}")
        logging.error(f"Error en las pruebas: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 
