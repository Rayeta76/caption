@echo off
cd /d "%~dp0"
title StockPrep Pro

echo Iniciando StockPrep Pro...
echo Carpeta: %CD%

REM 1. Intentar iniciar con el entorno Conda 'florence' que tiene PyTorch CUDA y PySide6 al 100%
echo Buscando entorno Conda 'florence'...

REM Intentar con comando directo si está en el PATH
where conda >nul 2>nul
if %errorlevel%==0 (
    echo [OK] Conda detectado en el PATH. Iniciando en entorno 'florence' con GPU RTX 4090...
    conda run -n florence python main.py
    if %errorlevel%==0 goto :fin
)

REM Intentar en rutas de instalación habituales de Windows
set "CONDA_PATH="
if exist "%SystemDrive%\ProgramData\anaconda3\condabin\conda.bat" set "CONDA_PATH=%SystemDrive%\ProgramData\anaconda3\condabin\conda.bat"
if not defined CONDA_PATH if exist "%USERPROFILE%\anaconda3\condabin\conda.bat" set "CONDA_PATH=%USERPROFILE%\anaconda3\condabin\conda.bat"
if not defined CONDA_PATH if exist "%USERPROFILE%\miniconda3\condabin\conda.bat" set "CONDA_PATH=%USERPROFILE%\miniconda3\condabin\conda.bat"
if not defined CONDA_PATH if exist "%SystemDrive%\ProgramData\miniconda3\condabin\conda.bat" set "CONDA_PATH=%SystemDrive%\ProgramData\miniconda3\condabin\conda.bat"

if defined CONDA_PATH (
    echo [OK] Conda localizado en: "%CONDA_PATH%"
    echo Iniciando en entorno 'florence' con GPU RTX 4090...
    call "%CONDA_PATH%" run -n florence python main.py
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
