#!/usr/bin/env python3
"""
Diagnóstico de problemas actuales en StockPrep Pro v2.0
1. Cierre incompleto del programa
2. Fallos en la carga de la base de datos durante procesamiento en lote
"""

import sys
import os
import threading
import time
import sqlite3
import gc
from pathlib import Path
from datetime import datetime
import psutil
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_process_cleanup():
    """Verifica si hay procesos huérfanos o threads no cerrados"""
    print("🔍 DIAGNÓSTICO: Cierre incompleto del programa")
    print("=" * 60)
    
    current_process = psutil.Process()
    threads = current_process.threads()
    
    print(f"📊 Proceso actual: {current_process.pid}")
    print(f"🧵 Threads activos: {len(threads)}")
    
    # Mostrar threads activos
    for i, thread in enumerate(threads):
        print(f"  Thread {i+1}: ID={thread.id}, CPU={thread.user_time}")
    
    # Verificar si hay threads daemon
    daemon_threads = [t for t in threading.enumerate() if t.daemon]
    print(f"👻 Threads daemon: {len(daemon_threads)}")
    
    # Verificar threads no daemon
    non_daemon_threads = [t for t in threading.enumerate() if not t.daemon and t != threading.main_thread()]
    print(f"🔒 Threads no-daemon: {len(non_daemon_threads)}")
    
    if non_daemon_threads:
        print("⚠️  PROBLEMA DETECTADO: Threads no-daemon activos")
        for thread in non_daemon_threads:
            print(f"  - {thread.name} (ID: {thread.ident})")
    
    return len(non_daemon_threads) > 0

def check_database_integrity():
    """Verifica la integridad de la base de datos"""
    print("\n🗄️ DIAGNÓSTICO: Integridad de la base de datos")
    print("=" * 60)
    
    db_paths = ["stockprep_images.db", "stockprep_database.db"]
    
    for db_path in db_paths:
        if Path(db_path).exists():
            print(f"📊 Verificando: {db_path}")
            
            try:
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Verificar tablas
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = cursor.fetchall()
                    print(f"  📋 Tablas encontradas: {len(tables)}")
                    
                    for table in tables:
                        table_name = table[0]
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]
                        print(f"    - {table_name}: {count} registros")
                    
                    # Verificar integridad
                    cursor.execute("PRAGMA integrity_check")
                    integrity = cursor.fetchone()[0]
                    if integrity == "ok":
                        print(f"  ✅ Integridad: OK")
                    else:
                        print(f"  ❌ Integridad: {integrity}")
                        
            except Exception as e:
                print(f"  ❌ Error verificando {db_path}: {e}")
        else:
            print(f"📊 {db_path}: No existe")

def check_database_errors():
    """Simula el procesamiento en lote para detectar errores"""
    print("\n🔄 DIAGNÓSTICO: Simulación de procesamiento en lote")
    print("=" * 60)
    
    try:
        # Importar módulos necesarios
        sys.path.append('src')
        from output.output_handler_v2 import OutputHandlerV2
        from core.enhanced_database_manager import EnhancedDatabaseManager
        
        # Crear instancia de prueba
        handler = OutputHandlerV2()
        db_manager = EnhancedDatabaseManager("stockprep_images.db")
        
        print("✅ Módulos importados correctamente")
        
        # Simular múltiples inserciones
        print("🔄 Simulando 10 inserciones consecutivas...")
        
        errors = 0
        for i in range(10):
            try:
                # Datos de prueba
                test_data = {
                    'descripcion': f'Imagen de prueba {i+1}',
                    'keywords': [f'keyword{i+1}', f'test{i+1}'],
                    'objects': {'labels': [f'object{i+1}'], 'scores': [0.95]}
                }
                
                # Intentar inserción directa en base de datos
                success = db_manager.insertar_imagen_manual(
                    f"test_image_{i+1}.jpg",
                    caption=test_data['descripcion'],
                    keywords=test_data['keywords'],
                    objetos=test_data['objects'],
                    estado='completed',
                    modelo_usado='Florence-2'
                )
                
                if success:
                    print(f"  ✅ Inserción {i+1}: OK")
                else:
                    print(f"  ❌ Inserción {i+1}: Falló")
                    errors += 1
                    
            except Exception as e:
                print(f"  ❌ Inserción {i+1}: Error - {e}")
                errors += 1
        
        print(f"\n📊 Resultados: {10-errors} exitosas, {errors} errores")
        
        if errors > 0:
            print("⚠️  PROBLEMA DETECTADO: Errores en inserciones consecutivas")
        
        return errors
        
    except Exception as e:
        print(f"❌ Error en simulación: {e}")
        return 10

def check_threading_issues():
    """Verifica problemas específicos de threading"""
    print("\n🧵 DIAGNÓSTICO: Problemas de threading")
    print("=" * 60)
    
    # Verificar si hay locks activos
    active_locks = []
    for obj in gc.get_objects():
        if isinstance(obj, threading.Lock):
            if obj.locked():
                active_locks.append(obj)
    
    print(f"🔒 Locks activos: {len(active_locks)}")
    
    # Verificar eventos
    active_events = []
    for obj in gc.get_objects():
        if isinstance(obj, threading.Event):
            active_events.append(obj)
    
    print(f"📡 Events activos: {len(active_events)}")
    
    # Verificar semáforos
    active_semaphores = []
    for obj in gc.get_objects():
        if isinstance(obj, threading.Semaphore):
            active_semaphores.append(obj)
    
    print(f"🚦 Semáforos activos: {len(active_semaphores)}")
    
    return len(active_locks) + len(active_events) + len(active_semaphores)

def check_concurrent_database_access():
    """Verifica problemas de acceso concurrente a la base de datos"""
    print("\n🔄 DIAGNÓSTICO: Acceso concurrente a base de datos")
    print("=" * 60)
    
    try:
        sys.path.append('src')
        from core.enhanced_database_manager import EnhancedDatabaseManager
        
        db_manager = EnhancedDatabaseManager("stockprep_images.db")
        
        # Simular acceso concurrente
        print("🔄 Simulando acceso concurrente...")
        
        def worker(worker_id):
            """Worker para simular acceso concurrente"""
            try:
                for i in range(5):
                    success = db_manager.insertar_imagen_manual(
                        f"concurrent_test_{worker_id}_{i}.jpg",
                        caption=f"Test concurrente {worker_id}-{i}",
                        keywords=[f"concurrent{worker_id}", f"test{i}"],
                        objetos=[],
                        estado='completed',
                        modelo_usado='Florence-2'
                    )
                    time.sleep(0.1)  # Pequeña pausa
                return True
            except Exception as e:
                print(f"  ❌ Worker {worker_id}: Error - {e}")
                return False
        
        # Crear múltiples threads
        threads = []
        results = []
        
        for i in range(3):
            thread = threading.Thread(target=lambda: results.append(worker(i+1)))
            threads.append(thread)
            thread.start()
        
        # Esperar a que terminen
        for thread in threads:
            thread.join()
        
        success_count = sum(results)
        print(f"📊 Resultados: {success_count}/3 workers exitosos")
        
        if success_count < 3:
            print("⚠️  PROBLEMA DETECTADO: Errores en acceso concurrente")
        
        return 3 - success_count
        
    except Exception as e:
        print(f"❌ Error en prueba de concurrencia: {e}")
        return 3

def main():
    """Función principal de diagnóstico"""
    print("🔍 DIAGNÓSTICO COMPLETO - StockPrep Pro v2.0")
    print("=" * 80)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Ejecutar diagnósticos
    cleanup_issues = check_process_cleanup()
    check_database_integrity()
    db_errors = check_database_errors()
    threading_issues = check_threading_issues()
    concurrent_errors = check_concurrent_database_access()
    
    # Resumen
    print("\n📋 RESUMEN DE DIAGNÓSTICO")
    print("=" * 60)
    
    issues_found = 0
    
    if cleanup_issues:
        print("❌ PROBLEMA 1: Cierre incompleto detectado")
        print("   - Threads no-daemon activos")
        print("   - Posible fuga de memoria")
        issues_found += 1
    
    if db_errors > 0:
        print("❌ PROBLEMA 2: Errores en base de datos detectados")
        print(f"   - {db_errors} errores en inserciones consecutivas")
        print("   - Posible problema de concurrencia")
        issues_found += 1
    
    if threading_issues > 0:
        print("❌ PROBLEMA 3: Problemas de threading detectados")
        print(f"   - {threading_issues} objetos de sincronización activos")
        print("   - Posible deadlock o bloqueo")
        issues_found += 1
    
    if concurrent_errors > 0:
        print("❌ PROBLEMA 4: Problemas de concurrencia detectados")
        print(f"   - {concurrent_errors} errores en acceso concurrente")
        print("   - Posible problema de locks en base de datos")
        issues_found += 1
    
    if issues_found == 0:
        print("✅ No se detectaron problemas críticos")
    else:
        print(f"\n⚠️  Total de problemas detectados: {issues_found}")
        print("🔧 Se recomienda aplicar las correcciones correspondientes")

if __name__ == "__main__":
    main() 