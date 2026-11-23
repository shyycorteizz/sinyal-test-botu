@echo off
chcp 65001 >nul
cd /d %~dp0
set PYTHONIOENCODING=utf-8
call .venv\Scripts\activate.bat
python evaluate.py --ac
pause
