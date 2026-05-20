@echo off
cd /d "%~dp0"
title StockPrep Pro

echo Iniciando StockPrep Pro...
echo Carpeta: %CD%

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

python main.py

:fin
if errorlevel 1 (
    echo.
    echo ERROR al iniciar. Comprueba que Python y PySide6 esten instalados:
    echo   pip install PySide6 Pillow
)
echo.
pause
