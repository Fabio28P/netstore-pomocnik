@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel% equ 0 (
  py -3 app.py
) else (
  python app.py
)
if errorlevel 1 (
  echo.
  echo Wymagany Python 3.10 lub nowszy. Zainstaluj go z python.org.
  echo Podczas instalacji zaznacz Add Python to PATH.
)
pause
