@echo off
setlocal
cd /d "%~dp0"
echo [1/5] 프로젝트 폴더: %cd%

if not exist .venv (
    echo [2/5] 가상환경을 생성합니다...
    py -m venv .venv
    if errorlevel 1 goto error
) else (
    echo [2/5] 기존 가상환경을 사용합니다.
)

call .venv\Scripts\activate.bat
if errorlevel 1 goto error

echo [3/5] 필요한 패키지를 설치합니다...
python -m pip install --upgrade pip
if errorlevel 1 goto error
pip install -r requirements.txt
if errorlevel 1 goto error

echo [4/5] 데이터베이스를 준비합니다...
python manage.py migrate
if errorlevel 1 goto error

echo [5/5] 서버를 실행합니다. 브라우저에서 http://localhost:8000 으로 접속하세요.
start "" http://localhost:8000
python manage.py runserver 0.0.0.0:8000
goto end

:error
echo.
echo 실행 중 오류가 발생했습니다. 위에 나온 오류 메시지를 복사해서 공유해주세요.
pause
exit /b 1

:end
echo.
echo 서버가 종료되었습니다.
pause
