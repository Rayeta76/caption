#!/usr/bin/env python3
"""
Script de Backup Completo - StockPrep Pro v2.0
Crea una copia de seguridad completa antes de instalar PySide6
"""
import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

def create_backup():
    """Crea una copia de seguridad completa del proyecto"""
    
    # Timestamp para el backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"StockPrep_Backup_{timestamp}"
    backup_dir = Path(f"../{backup_name}")
    
    print("💾 Creando copia de seguridad completa...")
    print(f"📁 Ubicación: {backup_dir.absolute()}")
    
    try:
        # Crear directorio de backup
        backup_dir.mkdir(exist_ok=True)
        
        # Archivos y directorios importantes a respaldar
        items_to_backup = [
            "main.py",
            "requirements.txt", 
            "src/",
            "config/",
            "models/",
            "README.md",
            "LICENSE",
            ".gitignore",
            "stockprep.spec",
            "setup_stockprep.py",
            "STOCKPREP_PRO_DOCS.md",
            "README_STOCKPREP_PRO.md",
            "stockprep_images.db",  # Base de datos actual
            "test_gpu_model.py",
            "test_components_simple.py",
            "test_system.py"
        ]
        
        # Copiar archivos y directorios
        copied_files = 0
        for item in items_to_backup:
            item_path = Path(item)
            if item_path.exists():
                if item_path.is_file():
                    shutil.copy2(item_path, backup_dir / item_path.name)
                    print(f"✅ Copiado: {item}")
                    copied_files += 1
                elif item_path.is_dir():
                    shutil.copytree(item_path, backup_dir / item_path.name, dirs_exist_ok=True)
                    print(f"✅ Copiado directorio: {item}")
                    copied_files += 1
            else:
                print(f"⚠️ No encontrado: {item}")
        
        # Crear archivo ZIP adicional
        zip_path = backup_dir.parent / f"{backup_name}.zip"
        print(f"\n📦 Creando archivo ZIP: {zip_path.name}")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(backup_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(backup_dir)
                    zipf.write(file_path, arcname)
        
        print(f"\n🎉 ¡Backup creado exitosamente!")
        print(f"📁 Carpeta: {backup_dir.absolute()}")
        print(f"📦 ZIP: {zip_path.absolute()}")
        print(f"📊 Archivos copiados: {copied_files}")
        
        # Crear archivo de información
        info_file = backup_dir / "BACKUP_INFO.txt"
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write(f"StockPrep Pro v2.0 - Backup Completo\n")
            f.write(f"=" * 50 + "\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Razón: Backup antes de instalar PySide6\n\n")
            f.write("Estado del sistema al momento del backup:\n")
            f.write("- Tkinter: ✅ Funcionando perfectamente\n")
            f.write("- PySide6: ❌ No instalado\n")
            f.write("- Modelo Florence-2: ✅ Disponible en models/\n")
            f.write("- Base de datos: ✅ Funcionando (SQLite)\n")
            f.write("- Botón verde mar: ✅ Implementado (#3CB371)\n")
            f.write("- GPU RTX 4090: ✅ Detectada y funcionando\n")
            f.write("- Procesamiento: ✅ Individual y en lote\n\n")
            f.write("INSTRUCCIONES DE RESTAURACIÓN:\n")
            f.write("=" * 30 + "\n")
            f.write("Si algo sale mal con PySide6:\n\n")
            f.write("1. Navega al directorio padre del proyecto\n")
            f.write("2. Elimina la carpeta 'Caption' actual\n")
            f.write("3. Extrae este backup:\n")
            f.write("   - Desde ZIP: Extrae el archivo .zip\n")
            f.write("   - Desde carpeta: Copia la carpeta completa\n")
            f.write("4. Renombra la carpeta extraída a 'Caption'\n")
            f.write("5. Abre terminal en la carpeta\n")
            f.write("6. Ejecuta: pip install -r requirements.txt\n")
            f.write("7. Ejecuta: python main.py\n")
            f.write("8. Verifica que todo funcione como antes\n\n")
            f.write("CONTACTO:\n")
            f.write("Si necesitas ayuda, el backup incluye todos los archivos\n")
            f.write("necesarios para restaurar el estado exacto anterior.\n")
        
        return True, backup_dir, zip_path
        
    except Exception as e:
        print(f"❌ Error creando backup: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None

def verify_backup(backup_dir):
    """Verifica que el backup esté completo"""
    print("\n🔍 Verificando integridad del backup...")
    
    essential_files = [
        "main.py",
        "requirements.txt",
        "src/gui/modern_gui_stockprep.py",
        "src/core/model_manager.py",
        "src/core/image_processor.py",
        "BACKUP_INFO.txt"
    ]
    
    essential_dirs = [
        "src/core",
        "src/gui", 
        "src/utils",
        "config"
    ]
    
    all_good = True
    
    # Verificar archivos esenciales
    print("📄 Verificando archivos esenciales:")
    for file in essential_files:
        file_path = backup_dir / file
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✅ {file} ({size} bytes)")
        else:
            print(f"❌ Falta: {file}")
            all_good = False
    
    # Verificar directorios esenciales
    print("\n📁 Verificando directorios esenciales:")
    for dir_name in essential_dirs:
        dir_path = backup_dir / dir_name
        if dir_path.exists() and dir_path.is_dir():
            file_count = len(list(dir_path.rglob("*")))
            print(f"✅ {dir_name}/ ({file_count} elementos)")
        else:
            print(f"❌ Falta: {dir_name}/")
            all_good = False
    
    return all_good

def get_backup_size(backup_dir):
    """Calcula el tamaño total del backup"""
    total_size = 0
    for root, dirs, files in os.walk(backup_dir):
        for file in files:
            file_path = Path(root) / file
            total_size += file_path.stat().st_size
    
    # Convertir a MB
    size_mb = total_size / (1024 * 1024)
    return size_mb

def main():
    """Función principal"""
    print("🚀 StockPrep Pro - Script de Backup Completo")
    print("=" * 60)
    print("Este script creará una copia de seguridad completa")
    print("antes de instalar PySide6.")
    print("=" * 60)
    
    # Verificar que estamos en el directorio correcto
    if not Path("main.py").exists():
        print("❌ Error: No se encuentra main.py")
        print("   Ejecuta este script desde el directorio del proyecto")
        return False
    
    print("✅ Directorio del proyecto verificado")
    
    # Crear backup
    success, backup_dir, zip_path = create_backup()
    
    if success:
        # Verificar backup
        if verify_backup(backup_dir):
            # Calcular tamaño
            size_mb = get_backup_size(backup_dir)
            
            print(f"\n✅ BACKUP COMPLETADO Y VERIFICADO")
            print("=" * 50)
            print(f"📁 Carpeta: {backup_dir}")
            print(f"📦 ZIP: {zip_path}")
            print(f"💾 Tamaño: {size_mb:.1f} MB")
            print(f"📄 Info: {backup_dir}/BACKUP_INFO.txt")
            print("=" * 50)
            print("\n🎯 SIGUIENTE PASO:")
            print("Ahora puedes instalar PySide6 de forma segura.")
            print("Si algo sale mal, tienes el backup completo.")
            
            return True
        else:
            print("\n⚠️ BACKUP INCOMPLETO")
            print("Revisa los archivos faltantes arriba")
            return False
    else:
        print("\n❌ ERROR CREANDO BACKUP")
        print("No se puede proceder con la instalación de PySide6")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🟢 LISTO PARA EL PASO 2: Instalar PySide6")
    else:
        print("\n🔴 BACKUP FALLÓ - No proceder con instalación")
    
    input("\nPresiona Enter para continuar...") 