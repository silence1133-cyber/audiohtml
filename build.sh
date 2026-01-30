#!/bin/bash
# PyInstaller 빌드 스크립트
# server.py를 단일 실행 파일로 빌드합니다.

set -e

echo "=========================================="
echo "PyInstaller 빌드 시작"
echo "=========================================="

# PyInstaller 설치 확인
if ! command -v pyinstaller &> /dev/null; then
    echo "[설치] PyInstaller 설치 중..."
    pip3 install pyinstaller
fi

# 이전 빌드 삭제
echo "[정리] 이전 빌드 파일 삭제 중..."
rm -rf build dist __pycache__
rm -f server.spec

# PyInstaller로 빌드
echo "[빌드] PyInstaller 실행 중..."
pyinstaller \
    --onefile \
    --name audio-server \
    --add-data "config/config.example.yaml:config" \
    --hidden-import=dotenv \
    --hidden-import=google.generativeai \
    --hidden-import=google.ai.generativelanguage \
    --hidden-import=google.api_core \
    --hidden-import=google.auth \
    --hidden-import=pydub \
    --hidden-import=pydub.audio_segment \
    --hidden-import=fastapi \
    --hidden-import=uvicorn \
    --hidden-import=uvicorn.lifespan.on \
    --hidden-import=uvicorn.loops.auto \
    --hidden-import=uvicorn.protocols.http.auto \
    --hidden-import=uvicorn.protocols.websockets.auto \
    --hidden-import=starlette \
    --hidden-import=yaml \
    --hidden-import=multipart \
    --collect-all google.generativeai \
    --collect-all uvicorn \
    --collect-all fastapi \
    server.py

echo ""
echo "=========================================="
echo "빌드 완료!"
echo "=========================================="
echo ""
echo "실행 파일: dist/audio-server"
echo "파일 크기: $(du -h dist/audio-server | cut -f1)"
echo ""
echo "배포 준비:"
echo "1. dist/audio-server 파일 복사"
echo "2. .env 파일 준비 (GOOGLE_API_KEY 설정)"
echo "3. config/config.yaml 파일 준비"
echo "4. FFmpeg 설치 확인"
echo ""
echo "실행 방법:"
echo "  ./dist/audio-server"
echo ""
