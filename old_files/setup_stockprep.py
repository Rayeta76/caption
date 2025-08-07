#!/usr/bin/env python3
"""
Script de instalación y configuración inicial para StockPrep Pro
"""
import os
import sys
import subprocess
from pathlib import Path


def print_banner():
    """Muestra el banner de bienvenida"""
    banner = """
    ╔════════════════════════════════════════════════════════╗
    ║                   StockPrep Pro v2.0                   ║
    ║        Sistema Inteligente de Procesamiento            ║
    ║              de Imágenes con IA                        ║
    ╚════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_python_version():
    """Verifica la versión de Python"""
    print("🔍 Verificando versión de Python...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"❌ Python {version.major}.{version.minor} detectado")
        print("   Se requiere Python 3.9 o superior")
        return False
    print(f"✅ Python {version.major}.{version.minor} detectado")
    return True


def create_virtual_env():
    """Crea el entorno virtual"""
    print("\n📦 Creando entorno virtual...")
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("   Entorno virtual ya existe")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Entorno virtual creado")
        return True
    except subprocess.CalledProcessError:
        print("❌ Error creando entorno virtual")
        return False


def get_pip_command():
    """Obtiene el comando pip correcto"""
    if os.name == 'nt':  # Windows
        return Path("venv/Scripts/pip.exe")
    else:  # Linux/Mac
        return Path("venv/bin/pip")


def install_dependencies():
    """Instala las dependencias"""
    print("\n📚 Instalando dependencias...")
    pip_cmd = get_pip_command()
    
    if not pip_cmd.exists():
        print("❌ No se encontró pip en el entorno virtual")
        return False
    
    try:
        # Actualizar pip
        print("   Actualizando pip...")
        subprocess.run([str(pip_cmd), "install", "--upgrade", "pip"], check=True)
        
        # Instalar dependencias
        print("   Instalando paquetes (esto puede tardar varios minutos)...")
        subprocess.run([str(pip_cmd), "install", "-r", "requirements.txt"], check=True)
        
        print("✅ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False


def check_cuda():
    """Verifica si CUDA está disponible"""
    print("\n🎮 Verificando CUDA...")
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✅ CUDA disponible: {torch.cuda.get_device_name(0)}")
            print(f"   Versión CUDA: {torch.version.cuda}")
            print(f"   VRAM disponible: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        else:
            print("ℹ️ CUDA no disponible - Se usará CPU")
            print("   Para mejor rendimiento, instala los drivers NVIDIA CUDA")
    except ImportError:
        print("⚠️ PyTorch no instalado aún")


def create_directories():
    """Crea las carpetas necesarias"""
    print("\n📁 Creando estructura de carpetas...")
    
    directories = [
        "models",
        "output",
        "salida",
        "temp",
        "assets"
    ]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        dir_path.mkdir(exist_ok=True)
        print(f"   ✓ {dir_name}/")
    
    print("✅ Estructura de carpetas creada")


def download_model():
    """Instrucciones para descargar el modelo"""
    print("\n🤖 Configuración del modelo Florence-2")
    print("-" * 50)
    print("El modelo debe descargarse manualmente:")
    print()
    print("1. Visita: https://huggingface.co/microsoft/Florence-2-large")
    print("2. Descarga todos los archivos del modelo")
    print("3. Colócalos en: models/Florence-2-large-ft-safetensors/")
    print()
    print("Archivos necesarios:")
    print("  - model.safetensors")
    print("  - config.json")
    print("  - tokenizer.json")
    print("  - preprocessor_config.json")
    print("  - Otros archivos del modelo")
    print("-" * 50)


def create_launch_script():
    """Crea scripts de lanzamiento"""
    print("\n🚀 Creando scripts de lanzamiento...")
    
    # Script para Windows
    if os.name == 'nt':
        with open("run_stockprep.bat", "w") as f:
            f.write("""@echo off
echo Iniciando StockPrep Pro...
call venv\\Scripts\\activate
python main.py
pause
""")
        print("   ✓ run_stockprep.bat creado")
    
    # Script para Linux/Mac
    else:
        with open("run_stockprep.sh", "w") as f:
            f.write("""#!/bin/bash
echo "Iniciando StockPrep Pro..."
source venv/bin/activate
python main.py
""")
        os.chmod("run_stockprep.sh", 0o755)
        print("   ✓ run_stockprep.sh creado")


def main():
    """Función principal de instalación"""
    print_banner()
    
    # Verificaciones
    if not check_python_version():
        return 1
    
    # Instalación
    if not create_virtual_env():
        return 1
    
    # Activar entorno virtual para instalaciones
    activate_cmd = "venv\\Scripts\\activate" if os.name == 'nt' else "source venv/bin/activate"
    print(f"\n💡 Para activar el entorno virtual usa: {activate_cmd}")
    
    if not install_dependencies():
        print("\n⚠️ Hubo errores durante la instalación")
        print("   Intenta instalar las dependencias manualmente:")
        print(f"   {activate_cmd}")
        print("   pip install -r requirements.txt")
        return 1
    
    # Configuración adicional
    check_cuda()
    create_directories()
    download_model()
    create_launch_script()
    
    # Instrucciones finales
    print("\n" + "="*60)
    print("✅ INSTALACIÓN COMPLETADA")
    print("="*60)
    print("\nPara ejecutar StockPrep Pro:")
    
    if os.name == 'nt':
        print("  1. Doble click en run_stockprep.bat")
        print("  O desde terminal:")
        print("     venv\\Scripts\\activate")
        print("     python main.py")
    else:
        print("  1. ./run_stockprep.sh")
        print("  O desde terminal:")
        print("     source venv/bin/activate")
        print("     python main.py")
    
    print("\n¡Disfruta procesando imágenes con IA! 🚀")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Instalación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)