#!/bin/bash
# 오디오 서비스 제거 스크립트

set -e

SERVICE_NAME="audio-server"

echo "=========================================="
echo "오디오 서비스 제거"
echo "=========================================="
echo ""

# 서비스 중지
echo "[작업] 서비스 중지 중..."
sudo systemctl stop ${SERVICE_NAME}.service 2>/dev/null || true

# 서비스 비활성화
echo "[작업] 서비스 비활성화 중..."
sudo systemctl disable ${SERVICE_NAME}.service 2>/dev/null || true

# 서비스 파일 삭제
echo "[작업] 서비스 파일 삭제 중..."
sudo rm -f /etc/systemd/system/${SERVICE_NAME}.service

# systemd 재로드
echo "[작업] systemd 재로드 중..."
sudo systemctl daemon-reload

echo ""
echo "=========================================="
echo "제거가 완료되었습니다!"
echo "=========================================="
echo ""
echo "참고: Python 패키지와 프로젝트 파일은 삭제되지 않았습니다."
echo "      필요시 수동으로 삭제하세요."
echo ""
