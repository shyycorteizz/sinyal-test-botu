@echo off
chcp 65001 >nul
cd /d %~dp0
echo ================================================
echo   Sinyal Test Botu - Kurulum
echo ================================================
where python >nul 2>nul || (echo [HATA] Python bulunamadi. python.org'dan kur, "Add to PATH" isaretle. & pause & exit /b 1)
if not exist .venv (
  echo Sanal ortam olusturuluyor...
  python -m venv .venv || (echo [HATA] venv olusturulamadi & pause & exit /b 1)
)
call .venv\Scripts\activate.bat
echo Kutuphaneler kuruluyor...
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q || (echo [HATA] Kutuphaneler kurulamadi & pause & exit /b 1)
if not exist .env (
  copy .env.example .env >nul
  echo.
  echo .env dosyasi olusturuldu. Simdi Not Defteri'nde acilacak:
  echo API_ID, API_HASH ve kanal adini doldur, kaydet, kapat.
  notepad .env
)
echo Testler calistiriliyor...
python tests\test_hepsi.py || (echo [UYARI] Bir test basarisiz oldu, bana ekran goruntusu at. & pause & exit /b 1)
echo.
echo ================================================
echo   Kurulum tamam!  Simdi BASLAT.bat'a cift tikla.
echo ================================================
pause
