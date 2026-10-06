@echo off
title JMJ Enterprise
echo ==========================================
echo        JMJ ENTERPRISE - INDIA STORE
echo ==========================================
echo.
echo Checking Python...
python --version
if errorlevel 1 (
    echo.
    echo Python is not installed or is not in PATH.
    echo Please install Python from https://www.python.org/downloads/windows/
    pause
    exit /b 1
)
echo.
echo Installing required packages...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo Could not install the required packages.
    pause
    exit /b 1
)
echo.
echo Creating a secure local session key...
for /f "delims=" %%K in ('python -c "import secrets; print(secrets.token_hex(32))"') do set "SECRET_KEY=%%K"
set "COOKIE_SECURE=0"
if not defined ADMIN_PASSWORD set "ADMIN_PASSWORD=JMJ-Admin-Change-This"
echo.
echo Starting JMJ Enterprise...
echo Open http://127.0.0.1:5000 in your browser.
echo Press CTRL+C in this window to stop the website.
echo.
python app.py
pause
