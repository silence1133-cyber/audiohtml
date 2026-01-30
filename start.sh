#!/bin/bash

# 음성 텍스트 변환 서버 시작 스크립트
# 사용법: ./start.sh

# 스크립트가 있는 디렉토리로 이동
cd "$(dirname "$0")"

echo "========================================"
echo "음성 텍스트 변환 서버 시작 중..."
echo "========================================"

# .env 파일 확인
if [ ! -f .env ]; then
    echo "오류: .env 파일을 찾을 수 없습니다."
    echo ".env 파일을 생성하고 GOOGLE_API_KEY를 설정하세요."
    exit 1
fi

# config.yaml 파일 확인
if [ ! -f config/config.yaml ]; then
    echo "오류: config/config.yaml 파일을 찾을 수 없습니다."
    echo "config.example.yaml을 config.yaml로 복사하세요."
    exit 1
fi

# Python 버전 확인
if ! command -v python3 &> /dev/null; then
    echo "오류: Python3가 설치되어 있지 않습니다."
    exit 1
fi

echo "Python 버전: $(python3 --version)"

# 패키지 설치 확인 (선택사항)
echo "필요한 패키지 확인 중..."
python3 -c "import fastapi, uvicorn, yaml" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "경고: 일부 패키지가 설치되어 있지 않습니다."
    echo "다음 명령으로 설치하세요: pip3 install -r requirements.txt"
    read -p "계속하시겠습니까? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "========================================"
echo "서버 시작 중..."
echo "종료하려면 Ctrl+C를 누르세요"
echo "========================================"

# 서버 시작
python3 server.py
