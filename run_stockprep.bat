@echo off
cd /d "%~dp0"
title StockPrep Pro

echo Iniciando StockPrep Pro...
echo Carpeta: %CD%

REM 1. Intentar iniciar con el entorno Conda 'florence' que tiene PyTorch CUDA y PySide6 al 100%
echo Buscando entorno Conda 'florence'...
where conda >nul 2>nul
if %errorlevel%==0 (
    echo [OK] Conda detectado. Iniciando en entorno 'florence' con GPU RTX 4090...
    conda run -n florence python main.py
    if %errorlevel%==0 goto :fin
)

echo.
echo [!] Conda no disponible o error al arrancar. Probando entornos virtuales locales...

REM 2. Fallbacks de entornos virtuales locales
if exist "venv\Scripts\python.exe" (
    call "venv\Scripts\activate.bat"
    python main.py
    goto :fin
)

if exist ".venv\Scripts\python.exe" (
    call ".venv\Scripts\activate.bat"
    python main.py
    goto :fin
)

REM 3. Fallback final al Python del sistema
echo Probando con Python del sistema...
python main.py

:fin
if errorlevel 1 (
    echo.
    echo ERROR al iniciar. Comprueba que Python, PySide6 y PyTorch esten instalados.
)
echo.
pause
