#!/bin/bash
# 오디오 서비스 설치 스크립트
# AWS Linux (Amazon Linux 2, Ubuntu, CentOS 등) 환경용

set -e  # 에러 발생 시 중단

echo "=========================================="
echo "오디오 텍스트 변환/요약 서비스 설치"
echo "=========================================="

# 현재 디렉토리
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="audio-server"
SERVICE_USER="${SUDO_USER:-$USER}"

echo ""
echo "설치 디렉토리: $INSTALL_DIR"
echo "서비스 이름: $SERVICE_NAME"
echo "실행 사용자: $SERVICE_USER"
echo ""

# Python 3 설치 확인
if ! command -v python3 &> /dev/null; then
    echo "[오류] Python 3가 설치되어 있지 않습니다."
    echo "다음 명령어로 설치하세요:"
    echo "  Amazon Linux 2: sudo yum install python3 python3-pip -y"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip -y"
    exit 1
fi

PYTHON_PATH=$(which python3)
echo "[확인] Python 3 경로: $PYTHON_PATH"

# pip 설치 확인
if ! command -v pip3 &> /dev/null; then
    echo "[설치] pip3 설치 중..."
    sudo yum install python3-pip -y || sudo apt-get install python3-pip -y
fi

# FFmpeg 설치 (오디오 변환에 필요)
echo ""
echo "[확인] FFmpeg 설치 확인..."
if ! command -v ffmpeg &> /dev/null; then
    echo "[설치] FFmpeg 설치 중..."
    if command -v yum &> /dev/null; then
        # Amazon Linux 2 / CentOS
        sudo yum install epel-release -y
        sudo yum install ffmpeg -y
    elif command -v apt-get &> /dev/null; then
        # Ubuntu / Debian
        sudo apt-get update
        sudo apt-get install ffmpeg -y
    fi
else
    echo "[확인] FFmpeg가 이미 설치되어 있습니다."
fi

# Python 패키지 설치
echo ""
echo "[설치] Python 패키지 설치 중..."
sudo pip3 install -r "$INSTALL_DIR/requirements.txt"

# 설정 파일 생성
echo ""
echo "[설정] 설정 파일 확인..."
if [ ! -f "$INSTALL_DIR/config/config.yaml" ]; then
    echo "[생성] config.yaml 생성 중..."
    cp "$INSTALL_DIR/config/config.example.yaml" "$INSTALL_DIR/config/config.yaml"
    echo "[완료] config/config.yaml 파일이 생성되었습니다."
    echo "       필요에 따라 설정을 수정하세요."
else
    echo "[확인] config.yaml이 이미 존재합니다."
fi

# .env 파일 확인
echo ""
echo "[설정] .env 파일 확인..."
if [ ! -f "$INSTALL_DIR/.env" ]; then
    echo "[경고] .env 파일이 없습니다."
    echo "       GOOGLE_API_KEY를 설정하기 위해 .env 파일을 생성하세요:"
    echo "       echo 'GOOGLE_API_KEY=your_api_key_here' > .env"
else
    echo "[확인] .env 파일이 존재합니다."
fi

# logs 디렉토리 생성
echo ""
echo "[설정] logs 디렉토리 생성..."
mkdir -p "$INSTALL_DIR/logs"
chmod 755 "$INSTALL_DIR/logs"

# systemd 서비스 파일 생성
echo ""
echo "[설치] systemd 서비스 등록 중..."

sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=Audio Text Conversion and Summary Service
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$PATH"
ExecStart=$PYTHON_PATH $INSTALL_DIR/server.py
Restart=always
RestartSec=10
StandardOutput=append:$INSTALL_DIR/logs/service.log
StandardError=append:$INSTALL_DIR/logs/service-error.log

# 보안 설정
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# systemd 서비스 활성화
echo ""
echo "[설정] 서비스 활성화 중..."
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}.service

echo ""
echo "=========================================="
echo "설치가 완료되었습니다!"
echo "=========================================="
echo ""
echo "서비스 관리 명령어:"
echo "  시작:    sudo systemctl start $SERVICE_NAME"
echo "  중지:    sudo systemctl stop $SERVICE_NAME"
echo "  재시작:  sudo systemctl restart $SERVICE_NAME"
echo "  상태:    sudo systemctl status $SERVICE_NAME"
echo "  로그:    sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "설정 파일: $INSTALL_DIR/config/config.yaml"
echo "로그 파일: $INSTALL_DIR/logs/"
echo ""
echo "서비스를 시작하려면 다음 명령어를 실행하세요:"
echo "  sudo systemctl start $SERVICE_NAME"
echo ""
