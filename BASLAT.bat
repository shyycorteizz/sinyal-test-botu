@echo off
chcp 65001 >nul
cd /d %~dp0
set PYTHONIOENCODING=utf-8
title Sinyal Test Botu - dinleniyor
if not exist .venv (echo Once kurulum.bat calistir. & pause & exit /b 1)
call .venv\Scripts\activate.bat
:dongu
python listener.py
if %errorlevel%==3 (pause & exit /b 1)
echo.
echo Bot durdu. 15 saniye sonra yeniden baslatiliyor... (kapatmak icin pencereyi kapat)
timeout /t 15 >nul
goto dongu
