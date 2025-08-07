#!/usr/bin/env python3
"""
Script para inicializar el repositorio Git de StockPrep Pro v2.0
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, cwd=None):
    """Ejecuta un comando y retorna el resultado"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando: {command}")
        print(f"Error: {e.stderr}")
        return None

def check_git_installed():
    """Verifica si Git está instalado"""
    result = run_command("git --version")
    if result:
        print(f"✅ Git encontrado: {result}")
        return True
    else:
        print("❌ Git no está instalado. Por favor instala Git primero.")
        return False

def init_git_repo():
    """Inicializa el repositorio Git"""
    print("🚀 Inicializando repositorio Git...")
    
    # Verificar si ya es un repositorio Git
    if os.path.exists(".git"):
        print("✅ Repositorio Git ya existe")
        return True
    
    # Inicializar repositorio
    result = run_command("git init")
    if not result:
        return False
    
    print("✅ Repositorio Git inicializado")
    return True

def add_files():
    """Agrega archivos al staging area"""
    print("📁 Agregando archivos...")
    
    # Agregar todos los archivos
    result = run_command("git add .")
    if not result:
        return False
    
    print("✅ Archivos agregados al staging area")
    return True

def create_initial_commit():
    """Crea el commit inicial"""
    print("💾 Creando commit inicial...")
    
    commit_message = """🚀 Initial commit: StockPrep Pro v2.0

✨ Características principales:
- Procesamiento de imágenes con Microsoft Florence-2
- 3 niveles de detalle (mínimo, medio, largo)
- Optimizaciones TF32 para RTX 4090
- Interfaz PySide6 estilo Windows 11
- Procesamiento en lote
- Base de datos SQLite integrada
- Exportación múltiple (JSON, CSV, XML)

🔧 Optimizaciones implementadas:
- TF32 habilitado para aceleración GPU
- cuDNN benchmark para máximo rendimiento
- Gestión inteligente de memoria CUDA
- Detección automática de GPU

📚 Documentación completa incluida
"""
    
    result = run_command(f'git commit -m "{commit_message}"')
    if not result:
        return False
    
    print("✅ Commit inicial creado")
    return True

def setup_remote_repo():
    """Configura el repositorio remoto"""
    print("🌐 Configurando repositorio remoto...")
    
    # Solicitar URL del repositorio
    print("\n📝 Para configurar el repositorio remoto:")
    print("1. Crea un repositorio en GitHub")
    print("2. Copia la URL del repositorio")
    print("3. Ejecuta los siguientes comandos:")
    print()
    print("git remote add origin https://github.com/tu-usuario/stockprep-pro.git")
    print("git branch -M main")
    print("git push -u origin main")
    print()
    
    # Preguntar si quiere configurar ahora
    response = input("¿Quieres configurar el repositorio remoto ahora? (s/n): ").lower()
    
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        repo_url = input("Ingresa la URL del repositorio: ").strip()
        
        if repo_url:
            # Agregar remote
            result = run_command(f'git remote add origin {repo_url}')
            if not result:
                return False
            
            # Cambiar nombre de rama a main
            result = run_command("git branch -M main")
            if not result:
                return False
            
            print("✅ Repositorio remoto configurado")
            print("📤 Para subir al repositorio, ejecuta: git push -u origin main")
            return True
    
    return True

def create_gitignore():
    """Verifica que .gitignore existe"""
    if not os.path.exists(".gitignore"):
        print("❌ .gitignore no encontrado")
        return False
    
    print("✅ .gitignore encontrado")
    return True

def show_status():
    """Muestra el estado del repositorio"""
    print("\n📊 Estado del repositorio:")
    result = run_command("git status")
    if result:
        print(result)

def main():
    """Función principal"""
    print("🎯 Inicializando repositorio Git para StockPrep Pro v2.0")
    print("=" * 60)
    
    # Verificar Git
    if not check_git_installed():
        sys.exit(1)
    
    # Verificar .gitignore
    if not create_gitignore():
        print("⚠️  Asegúrate de que .gitignore esté configurado correctamente")
    
    # Inicializar repositorio
    if not init_git_repo():
        sys.exit(1)
    
    # Agregar archivos
    if not add_files():
        sys.exit(1)
    
    # Crear commit inicial
    if not create_initial_commit():
        sys.exit(1)
    
    # Configurar remoto
    setup_remote_repo()
    
    # Mostrar estado
    show_status()
    
    print("\n🎉 ¡Repositorio Git inicializado correctamente!")
    print("\n📋 Próximos pasos:")
    print("1. Subir al repositorio remoto: git push -u origin main")
    print("2. Crear releases en GitHub")
    print("3. Configurar GitHub Actions (opcional)")
    print("4. Invitar colaboradores")
    
    print("\n🔗 Enlaces útiles:")
    print("- GitHub: https://github.com/tu-usuario/stockprep-pro")
    print("- Issues: https://github.com/tu-usuario/stockprep-pro/issues")
    print("- Releases: https://github.com/tu-usuario/stockprep-pro/releases")

if __name__ == "__main__":
    main() 