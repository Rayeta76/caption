#!/usr/bin/env python3
"""
Script para crear punto de restauración en Git
StockPrep Pro v2.0 - Antes de mejoras de galería
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

def run_git_command(command):
    """Ejecuta un comando de Git y retorna el resultado"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=Path.cwd())
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"Error ejecutando: {command}")
            print(f"Error: {result.stderr}")
            return None
    except Exception as e:
        print(f"Error ejecutando comando Git: {e}")
        return None

def create_restore_point():
    """Crea un punto de restauración en Git"""
    print("🔄 Creando punto de restauración en Git...")
    
    # Verificar si estamos en un repositorio Git
    if not run_git_command("git status"):
        print("❌ No se encontró un repositorio Git. Inicializando...")
        if not run_git_command("git init"):
            print("❌ Error inicializando repositorio Git")
            return False
    
    # Verificar estado actual
    print("📊 Verificando estado actual del repositorio...")
    status = run_git_command("git status --porcelain")
    
    if not status:
        print("✅ No hay cambios pendientes")
    else:
        print("📝 Cambios detectados:")
        print(status)
    
    # Agregar todos los archivos
    print("📁 Agregando archivos al staging area...")
    if not run_git_command("git add ."):
        print("❌ Error agregando archivos")
        return False
    
    # Crear commit
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_message = f"""Punto de restauración: Antes de mejoras de galería

- Estado actual de la aplicación StockPrep Pro v2.0
- Base de datos SQLite funcionando correctamente
- Galería básica implementada
- Listo para implementar mejoras de galería tipo web de stock
- Implementación de SQLite + FTS5 + WebP BLOB

Fecha: {timestamp}
Versión: StockPrep Pro v2.0
"""
    
    print("💾 Creando commit de restauración...")
    if not run_git_command(f'git commit -m "{commit_message}"'):
        print("❌ Error creando commit")
        return False
    
    # Crear tag para fácil identificación
    tag_name = "v1.0-gallery-before-improvements"
    print(f"🏷️ Creando tag: {tag_name}")
    if not run_git_command(f'git tag -a {tag_name} -m "Versión antes de mejoras de galería"'):
        print("⚠️ Error creando tag (continuando...)")
    
    # Mostrar información del commit
    print("\n✅ Punto de restauración creado exitosamente!")
    print("📋 Información del commit:")
    
    commit_hash = run_git_command("git rev-parse HEAD")
    if commit_hash:
        print(f"   Hash: {commit_hash}")
    
    print(f"   Tag: {tag_name}")
    print(f"   Fecha: {timestamp}")
    
    # Mostrar últimos commits
    print("\n📜 Últimos commits:")
    log = run_git_command("git log --oneline -5")
    if log:
        print(log)
    
    print("\n🎯 Para restaurar este punto en el futuro:")
    print(f"   git checkout {tag_name}")
    print("   o")
    print(f"   git reset --hard {commit_hash}")
    
    return True

def main():
    """Función principal"""
    print("=" * 60)
    print("🔄 STOCKPREP PRO v2.0 - CREAR PUNTO DE RESTAURACIÓN")
    print("=" * 60)
    
    try:
        success = create_restore_point()
        
        if success:
            print("\n🎉 ¡Punto de restauración creado exitosamente!")
            print("🚀 Ahora puedes proceder con las mejoras de galería con confianza.")
        else:
            print("\n❌ Error creando punto de restauración")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Operación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

