@echo off
setlocal
cd /d "%~dp0"
echo [1/5] Project folder: %cd%

if not exist .venv (
    echo [2/5] Creating virtual environment...
    py -m venv .venv
    if errorlevel 1 goto error
) else (
    echo [2/5] Using existing virtual environment.
)

call .venv\Scripts\activate.bat
if errorlevel 1 goto error

echo [3/5] Installing required packages...
python -m pip install --upgrade pip
if errorlevel 1 goto error
pip install -r requirements.txt
if errorlevel 1 goto error

echo [4/5] Preparing database...
python manage.py migrate
if errorlevel 1 goto error

echo [5/5] Starting server. Open http://localhost:8000 in your browser.
start "" http://localhost:8000
python manage.py runserver 0.0.0.0:8000
goto end

:error
echo.
echo An error occurred. Please copy the error messages above and share them.
pause
exit /b 1

:end
echo.
echo Server stopped.
pause
