#!/usr/bin/env python3
"""
Script para verificar que la solución de base de datos funciona correctamente
"""

import sys
from pathlib import Path

# Añadir src al path
sys.path.append(str(Path(__file__).parent / "src"))

def verificar_solucion():
    """Verifica que OutputHandlerV2 esté configurado correctamente"""
    
    print("🔍 VERIFICANDO SOLUCIÓN DE BASE DE DATOS")
    print("=" * 50)
    
    try:
        # Importar OutputHandlerV2
        from output.output_handler_v2 import OutputHandlerV2
        
        # Crear instancia con configuración por defecto
        handler = OutputHandlerV2()
        
        # Verificar qué base de datos está usando
        db_path = handler.db_manager.db_path
        
        print(f"✅ OutputHandlerV2 importado correctamente")
        print(f"📊 Base de datos configurada: {db_path}")
        
        if "stockprep_images.db" in str(db_path):
            print("✅ CORRECTO: Usando stockprep_images.db")
            print("✅ Ahora todo el sistema usa la misma base de datos")
        else:
            print("❌ ERROR: Aún usando base de datos incorrecta")
            return False
            
        # Verificar que las bases de datos existen
        db_images = Path("stockprep_images.db")
        db_database = Path("stockprep_database.db")
        
        print(f"\n📁 Estado de archivos de base de datos:")
        if db_images.exists():
            size_kb = db_images.stat().st_size / 1024
            print(f"  📊 stockprep_images.db: {size_kb:.1f} KB (ACTIVA)")
        else:
            print(f"  📊 stockprep_images.db: No existe (se creará automáticamente)")
            
        if db_database.exists():
            size_kb = db_database.stat().st_size / 1024
            print(f"  📊 stockprep_database.db: {size_kb:.1f} KB (ya no se usa)")
        
        print(f"\n🎯 SOLUCIÓN APLICADA EXITOSAMENTE")
        print(f"📋 Próximos pasos:")
        print(f"  1. Reinicia la aplicación StockPrep")
        print(f"  2. Procesa una imagen nueva")
        print(f"  3. Abre el módulo 'Gestión de Base de Datos'")
        print(f"  4. ¡Deberías ver los datos guardados!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importando OutputHandlerV2: {e}")
        return False
    except Exception as e:
        print(f"❌ Error verificando: {e}")
        return False

def mostrar_estadisticas_bd():
    """Muestra estadísticas de las bases de datos"""
    
    print(f"\n📊 ESTADÍSTICAS DE BASES DE DATOS")
    print("=" * 40)
    
    try:
        from core.enhanced_database_manager import EnhancedDatabaseManager
        
        # Verificar stockprep_images.db
        if Path("stockprep_images.db").exists():
            db_manager = EnhancedDatabaseManager("stockprep_images.db")
            stats = db_manager.obtener_estadisticas()
            
            print(f"📊 stockprep_images.db (ACTIVA):")
            print(f"  - Total imágenes: {stats.get('total_imagenes', 0)}")
            print(f"  - Procesadas hoy: {stats.get('procesadas_hoy', 0)}")
            print(f"  - Última actualización: {stats.get('ultima_actualizacion', 'Nunca')}")
        
        # Verificar stockprep_database.db
        if Path("stockprep_database.db").exists():
            db_manager2 = EnhancedDatabaseManager("stockprep_database.db")
            stats2 = db_manager2.obtener_estadisticas()
            
            print(f"\n📊 stockprep_database.db (anterior):")
            print(f"  - Total imágenes: {stats2.get('total_imagenes', 0)}")
            print(f"  - Procesadas hoy: {stats2.get('procesadas_hoy', 0)}")
            
            if stats2.get('total_imagenes', 0) > 0:
                print(f"\n💡 SUGERENCIA: Tienes {stats2.get('total_imagenes', 0)} imágenes en la BD anterior.")
                print(f"   Puedes migrarlas manualmente si es necesario.")
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")

if __name__ == "__main__":
    if verificar_solucion():
        mostrar_estadisticas_bd()
        print(f"\n🎉 ¡SOLUCIÓN COMPLETADA CON ÉXITO!")
    else:
        print(f"\n❌ Hubo problemas con la solución") 