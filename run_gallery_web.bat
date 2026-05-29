@echo off
cd /d "%~dp0"
title StockPrep Web Gallery

echo Iniciando galeria web local...
echo URL: http://127.0.0.1:8000
echo.

start "" cmd /c "timeout /t 1 /nobreak >nul && start "" http://127.0.0.1:8000/"

python scripts\web_gallery.py --port 8000

echo.
pause
