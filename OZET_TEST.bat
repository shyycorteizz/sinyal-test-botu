@echo off
chcp 65001 >nul
cd /d %~dp0
set PYTHONIOENCODING=utf-8
if not exist .venv (echo Once kurulum.bat calistir. ^& pause ^& exit /b 1)
call .venv\Scripts\activate.bat
if not exist ozet.txt type nul > ozet.txt
echo Not Defteri acilacak: kanalin HAFTALIK OZET mesajini kopyala, yapistir, kaydet ve kapat.
notepad ozet.txt
python ozet_aktar.py ozet.txt
python evaluate.py --ac
pause
