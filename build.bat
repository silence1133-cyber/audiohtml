@echo off
REM PyInstaller 빌드 스크립트 (Windows)
REM server.py를 단일 실행 파일로 빌드합니다.

echo ==========================================
echo PyInstaller 빌드 시작
echo ==========================================
echo.

REM PyInstaller 설치 확인
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [설치] PyInstaller 설치 중...
    pip install pyinstaller
)

REM 이전 빌드 삭제
echo [정리] 이전 빌드 파일 삭제 중...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__
if exist server.spec del /q server.spec

REM PyInstaller로 빌드
echo [빌드] PyInstaller 실행 중...
pyinstaller ^
    --onefile ^
    --name audio-server ^
    --add-data "config/config.example.yaml;config" ^
    --hidden-import=dotenv ^
    --hidden-import=google.generativeai ^
    --hidden-import=google.ai.generativelanguage ^
    --hidden-import=google.api_core ^
    --hidden-import=google.auth ^
    --hidden-import=pydub ^
    --hidden-import=pydub.audio_segment ^
    --hidden-import=fastapi ^
    --hidden-import=uvicorn ^
    --hidden-import=uvicorn.lifespan.on ^
    --hidden-import=uvicorn.loops.auto ^
    --hidden-import=uvicorn.protocols.http.auto ^
    --hidden-import=uvicorn.protocols.websockets.auto ^
    --hidden-import=starlette ^
    --hidden-import=yaml ^
    --hidden-import=multipart ^
    --collect-all google.generativeai ^
    --collect-all uvicorn ^
    --collect-all fastapi ^
    server.py

echo.
echo ==========================================
echo 빌드 완료!
echo ==========================================
echo.
echo 실행 파일: dist\audio-server.exe
echo.
echo 배포 준비:
echo 1. dist\audio-server.exe 파일 복사
echo 2. .env 파일 준비 (GOOGLE_API_KEY 설정)
echo 3. config\config.yaml 파일 준비
echo 4. FFmpeg 설치 확인
echo.
echo 실행 방법:
echo   dist\audio-server.exe
echo.
pause
