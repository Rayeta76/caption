# -*- mode: python ; coding: utf-8 -*-
"""
Archivo de especificación para PyInstaller - StockPrep Pro v2.0
Genera un ejecutable único con todas las dependencias incluidas
"""

import sys
import os
from pathlib import Path

# Rutas importantes
project_root = Path.cwd()
src_path = project_root / "src"
models_path = project_root / "models"

# Datos adicionales a incluir
datas = []

# Incluir modelos si existen
if models_path.exists():
    datas.append((str(models_path), "models"))

# Incluir archivos de configuración
config_files = [
    "requirements.txt",
    "README_STOCKPREP_PRO.md",
    "STOCKPREP_PRO_DOCS.md"
]

for config_file in config_files:
    if (project_root / config_file).exists():
        datas.append((str(project_root / config_file), "."))

# Módulos ocultos necesarios
hiddenimports = [
    # Core de la aplicación
    'src.core.model_manager',
    'src.core.image_processor', 
    'src.core.sqlite_database',
    'src.core.batch_engine',
    
    # GUI
    'src.gui.main_window',
    'src.gui.modern_gui_win11',
    
    # I/O
    'src.io.output_handler',
    'src.io.output_handler_v2',
    
    # Utils
    'src.utils.keyword_extractor',
    
    # Dependencias de PyTorch
    'torch',
    'torch.nn',
    'torch.nn.functional',
    'torch.utils',
    'torch.utils.data',
    'torchvision',
    'torchvision.transforms',
    
    # Transformers y dependencias
    'transformers',
    'transformers.models',
    'transformers.models.florence2',
    'transformers.tokenization_utils',
    'transformers.tokenization_utils_base',
    'transformers.utils',
    'transformers.utils.hub',
    'transformers.trainer_utils',
    'transformers.modeling_utils',
    'transformers.configuration_utils',
    'transformers.generation',
    'transformers.generation.utils',
    
    # Safetensors
    'safetensors',
    'safetensors.torch',
    
    # PIL/Pillow
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'PIL.ImageOps',
    'PIL.ImageEnhance',
    
    # Tkinter (fallback GUI)
    'tkinter',
    'tkinter.ttk',
    'tkinter.filedialog',
    'tkinter.messagebox',
    
    # PySide6 (GUI moderna)
    'PySide6',
    'PySide6.QtWidgets',
    'PySide6.QtCore',
    'PySide6.QtGui',
    
    # YAKE para keywords
    'yake',
    
    # Numpy y dependencias científicas
    'numpy',
    'numpy.core',
    'numpy.core._methods',
    'numpy.lib',
    'numpy.lib.format',
    
    # Requests para descargas
    'requests',
    'requests.adapters',
    'requests.auth',
    'requests.cookies',
    'requests.models',
    'requests.sessions',
    'requests.utils',
    'urllib3',
    
    # Regex y procesamiento de texto
    're',
    'regex',
    'unicodedata',
    'string',
    
    # JSON y serialización
    'json',
    'pickle',
    'csv',
    'xml',
    'xml.etree',
    'xml.etree.ElementTree',
    
    # Base de datos
    'sqlite3',
    
    # Sistema y paths
    'pathlib',
    'os',
    'sys',
    'platform',
    'subprocess',
    
    # Logging
    'logging',
    'logging.handlers',
    
    # Fecha y tiempo
    'datetime',
    'time',
    
    # Threading
    'threading',
    'concurrent',
    'concurrent.futures',
    
    # Typing
    'typing',
    'typing_extensions',
    
    # Matemáticas
    'math',
    'random',
    
    # Compresión
    'gzip',
    'zipfile',
    
    # Codificación
    'base64',
    'codecs',
    
    # Redes
    'socket',
    'ssl',
    'certifi',
    
    # Hugging Face Hub
    'huggingface_hub',
    'huggingface_hub.utils',
    'huggingface_hub.constants',
    
    # Tokenizers
    'tokenizers',
    
    # Otros
    'tqdm',
    'packaging',
    'packaging.version',
    'filelock',
    'psutil'
]

# Configuración del análisis
a = Analysis(
    ['main.py'],
    pathex=[str(project_root), str(src_path)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Excluir módulos innecesarios para reducir tamaño
        'matplotlib',
        'scipy',
        'pandas',
        'jupyter',
        'notebook',
        'IPython',
        'pytest',
        'setuptools',
        'pip',
        'wheel',
        'distutils',
        
        # Excluir otros backends de GUI
        'PyQt5',
        'PyQt6',
        'wx',
        'kivy',
        
        # Excluir módulos de desarrollo
        'pdb',
        'pydoc',
        'doctest',
        'unittest',
        
        # Excluir módulos de red innecesarios
        'ftplib',
        'smtplib',
        'poplib',
        'imaplib',
        'telnetlib',
        
        # Excluir compiladores
        'distutils.msvccompiler',
        'distutils.unixccompiler',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Configuración del PYZ
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Configuración del ejecutable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='StockPrep_Pro_v2',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Comprimir con UPX si está disponible
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin ventana de consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Aquí puedes agregar un icono .ico
    version_file=None,  # Aquí puedes agregar información de versión
)

# Configuración adicional para Windows
if sys.platform == "win32":
    exe.name = 'StockPrep_Pro_v2.exe'
    # Agregar información de versión para Windows
    exe.version_info = {
        'filevers': (2, 0, 0, 0),
        'prodvers': (2, 0, 0, 0),
        'mask': 0x3f,
        'flags': 0x0,
        'OS': 0x40004,
        'fileType': 0x1,
        'subtype': 0x0,
        'date': (0, 0),
        'CompanyName': 'StockPrep Pro',
        'FileDescription': 'StockPrep Pro - Procesador de Imágenes con IA',
        'FileVersion': '2.0.0.0',
        'InternalName': 'StockPrep_Pro_v2',
        'LegalCopyright': 'Copyright © 2024',
        'OriginalFilename': 'StockPrep_Pro_v2.exe',
        'ProductName': 'StockPrep Pro',
        'ProductVersion': '2.0.0.0',
    }

# Configuración para Linux
elif sys.platform.startswith("linux"):
    exe.name = 'StockPrep_Pro_v2'

# Configuración para macOS
elif sys.platform == "darwin":
    exe.name = 'StockPrep_Pro_v2'
    
    # Crear bundle para macOS
    app = BUNDLE(
        exe,
        name='StockPrep_Pro_v2.app',
        icon=None,  # Agregar icono .icns aquí
        bundle_identifier='com.stockprep.pro.v2',
        info_plist={
            'NSPrincipalClass': 'NSApplication',
            'NSAppleScriptEnabled': False,
            'CFBundleDocumentTypes': [
                {
                    'CFBundleTypeName': 'Image',
                    'CFBundleTypeRole': 'Viewer',
                    'LSItemContentTypes': [
                        'public.image',
                        'public.jpeg',
                        'public.png'
                    ]
                }
            ]
        },
    ) 