@echo off
cd /d "%~dp0"
call venv\Scripts\activate.bat 2>nul
python scripts\\gallery_backend_check.py
pause
