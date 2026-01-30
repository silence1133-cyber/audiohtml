# Linux 서비스 설치 가이드 (AWS Linux)

이 가이드는 AWS Linux (Amazon Linux 2, Ubuntu, CentOS 등) 환경에서 오디오 서비스를 systemd 서비스로 설치하고 관리하는 방법을 설명합니다.

## 특징

- ✅ **가상환경 불필요**: 시스템 전역에 설치되어 바로 실행
- ✅ **자동 시작**: 시스템 부팅 시 자동으로 시작
- ✅ **자동 재시작**: 오류 발생 시 자동으로 재시작
- ✅ **백그라운드 실행**: 터미널 종료해도 계속 실행
- ✅ **로그 관리**: systemd 저널 및 파일 로그 지원
- ✅ **간단한 관리**: systemctl 명령어로 쉽게 관리

## 사전 준비

### 1. 서버에 파일 업로드

```bash
# Git으로 클론 (추천)
git clone https://github.com/your-repo/audio.git
cd audio

# 또는 파일을 직접 업로드 (SCP, SFTP 등)
```

### 2. .env 파일 생성

```bash
# GOOGLE_API_KEY 설정
echo 'GOOGLE_API_KEY=your_google_api_key_here' > .env
```

## 자동 설치 (권장)

### 설치

```bash
# 실행 권한 부여
chmod +x install.sh

# 설치 스크립트 실행
sudo ./install.sh
```

설치 스크립트가 자동으로:
1. Python 3 및 pip 확인
2. FFmpeg 설치 (오디오 변환에 필요)
3. Python 패키지 설치
4. 설정 파일 생성
5. systemd 서비스 등록
6. 자동 시작 설정

### 서비스 시작

```bash
# 서비스 시작
sudo systemctl start audio-server

# 서비스 상태 확인
sudo systemctl status audio-server

# 로그 확인 (실시간)
sudo journalctl -u audio-server -f
```

### 제거

```bash
# 제거 스크립트 실행
chmod +x uninstall.sh
sudo ./uninstall.sh
```

## 수동 설치

자동 설치 스크립트를 사용하지 않고 수동으로 설치하려면:

### 1. 시스템 패키지 설치

```bash
# Amazon Linux 2 / CentOS
sudo yum update -y
sudo yum install python3 python3-pip ffmpeg -y

# Ubuntu / Debian
sudo apt-get update
sudo apt-get install python3 python3-pip ffmpeg -y
```

### 2. Python 패키지 설치

```bash
# 프로젝트 디렉토리에서
sudo pip3 install -r requirements.txt
```

### 3. 설정 파일 생성

```bash
# config.yaml 생성
cp config/config.example.yaml config/config.yaml

# 필요에 따라 설정 수정
nano config/config.yaml
```

### 4. .env 파일 생성

```bash
# GOOGLE_API_KEY 설정
echo 'GOOGLE_API_KEY=your_api_key_here' > .env
```

### 5. systemd 서비스 파일 생성

```bash
# 서비스 파일 생성
sudo nano /etc/systemd/system/audio-server.service
```

다음 내용을 입력 (경로를 실제 경로로 변경):

```ini
[Unit]
Description=Audio Text Conversion and Summary Service
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/audio
ExecStart=/usr/bin/python3 /home/ec2-user/audio/server.py
Restart=always
RestartSec=10
StandardOutput=append:/home/ec2-user/audio/logs/service.log
StandardError=append:/home/ec2-user/audio/logs/service-error.log

# 보안 설정
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

**주의**: 다음 항목을 실제 환경에 맞게 수정하세요:
- `User`: 실행할 사용자 (예: ec2-user, ubuntu)
- `WorkingDirectory`: 프로젝트 절대 경로
- `ExecStart`: Python 경로와 server.py 절대 경로

### 6. 서비스 활성화 및 시작

```bash
# systemd 재로드
sudo systemctl daemon-reload

# 서비스 활성화 (부팅 시 자동 시작)
sudo systemctl enable audio-server

# 서비스 시작
sudo systemctl start audio-server

# 서비스 상태 확인
sudo systemctl status audio-server
```

## 서비스 관리 명령어

### 기본 명령어

```bash
# 서비스 시작
sudo systemctl start audio-server

# 서비스 중지
sudo systemctl stop audio-server

# 서비스 재시작
sudo systemctl restart audio-server

# 서비스 상태 확인
sudo systemctl status audio-server

# 서비스 활성화 (부팅 시 자동 시작)
sudo systemctl enable audio-server

# 서비스 비활성화 (부팅 시 자동 시작 해제)
sudo systemctl disable audio-server
```

### 로그 확인

```bash
# 실시간 로그 확인 (systemd 저널)
sudo journalctl -u audio-server -f

# 최근 100줄 로그 확인
sudo journalctl -u audio-server -n 100

# 오늘 로그만 확인
sudo journalctl -u audio-server --since today

# 파일 로그 확인
tail -f logs/service.log
tail -f logs/server.log
```

## 설정 변경

### 포트 또는 HTTPS 설정 변경

```bash
# 설정 파일 수정
nano config/config.yaml

# 서비스 재시작
sudo systemctl restart audio-server
```

### 환경 변수 변경

```bash
# .env 파일 수정
nano .env

# 서비스 재시작
sudo systemctl restart audio-server
```

## 보안 설정 (프로덕션 환경)

### 1. 방화벽 설정

```bash
# 특정 포트 열기 (예: 8000번 포트)
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

# 또는 iptables 사용
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
sudo service iptables save
```

### 2. HTTPS 설정

```bash
# SSL 인증서 생성 (Let's Encrypt)
sudo yum install certbot -y  # Amazon Linux 2

# 인증서 발급
sudo certbot certonly --standalone -d yourdomain.com

# config.yaml에서 HTTPS 활성화
nano config/config.yaml
```

config.yaml 예시:
```yaml
server:
  port: 443
  host: "0.0.0.0"

https:
  enabled: true
  cert_file: "/etc/letsencrypt/live/yourdomain.com/fullchain.pem"
  key_file: "/etc/letsencrypt/live/yourdomain.com/privkey.pem"
```

### 3. 파일 권한 설정

```bash
# 프로젝트 디렉토리 권한
chmod 755 /home/ec2-user/audio
chmod 600 /home/ec2-user/audio/.env
chmod 600 /home/ec2-user/audio/config/config.yaml

# SSL 키 파일 권한 (사용 시)
sudo chmod 600 /path/to/key.pem
```

## 서비스 테스트

### 로컬 테스트

```bash
# 서비스가 실행 중인지 확인
sudo systemctl status audio-server

# API 엔드포인트 테스트
curl http://localhost:8000/health
```

### 외부에서 접속 테스트

```bash
# 서버 IP로 테스트
curl http://your-server-ip:8000/health

# 파일 업로드 테스트
curl -X POST http://your-server-ip:8000/summarize \
  -F "file=@test_audio.mp3"
```

## 문제 해결

### 서비스가 시작되지 않음

```bash
# 상세 로그 확인
sudo journalctl -u audio-server -n 50 --no-pager

# 설정 파일 확인
sudo systemctl cat audio-server

# Python 경로 확인
which python3

# 서비스 파일의 ExecStart 경로가 맞는지 확인
```

### 포트가 이미 사용 중

```bash
# 포트 사용 확인
sudo netstat -tulpn | grep :8000

# 프로세스 종료
sudo kill -9 [PID]

# 또는 config.yaml에서 다른 포트로 변경
```

### Python 패키지 오류

```bash
# 패키지 재설치
sudo pip3 install -r requirements.txt --force-reinstall

# 특정 패키지 설치 확인
pip3 list | grep fastapi
```

### API 키 오류

```bash
# .env 파일 확인
cat .env

# GOOGLE_API_KEY가 올바르게 설정되었는지 확인
# 서비스 재시작
sudo systemctl restart audio-server
```

### 로그 파일 권한 오류

```bash
# logs 디렉토리 권한 확인
ls -la logs/

# 권한 수정
sudo chown -R ec2-user:ec2-user logs/
chmod 755 logs/
```

## AWS EC2 특화 설정

### 1. 보안 그룹 설정

AWS 콘솔에서:
1. EC2 → 인스턴스 → 보안 그룹
2. 인바운드 규칙 편집
3. 규칙 추가:
   - 유형: 사용자 지정 TCP
   - 포트: 8000 (또는 설정한 포트)
   - 소스: 0.0.0.0/0 (모든 IP) 또는 특정 IP

### 2. Elastic IP 할당 (선택사항)

고정 IP가 필요한 경우 Elastic IP를 할당하세요.

### 3. 자동 백업 (선택사항)

```bash
# 백업 스크립트 생성
cat > /home/ec2-user/backup.sh <<'EOF'
#!/bin/bash
tar -czf /home/ec2-user/audio-backup-$(date +%Y%m%d).tar.gz \
  /home/ec2-user/audio/config \
  /home/ec2-user/audio/.env
EOF

chmod +x /home/ec2-user/backup.sh

# cron으로 정기 백업 (매일 새벽 2시)
crontab -e
# 추가: 0 2 * * * /home/ec2-user/backup.sh
```

## 모니터링

### CPU 및 메모리 사용량 확인

```bash
# 프로세스 리소스 확인
top -p $(pgrep -f "python3.*server.py")

# 또는 htop 사용
htop
```

### 서비스 재시작 횟수 확인

```bash
# 서비스 통계
systemctl show audio-server | grep NRestarts
```

## 성능 최적화

### Uvicorn Workers 설정

`server.py`의 마지막 부분을 수정:

```python
uvicorn.run(
    app,
    host=host,
    port=port,
    workers=4,  # CPU 코어 수에 맞게 조정
    log_level="info"
)
```

또는 서비스 파일에서:

```ini
ExecStart=/usr/bin/python3 /home/ec2-user/audio/server.py
# 대신
ExecStart=/usr/local/bin/uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
```

## 추가 리소스

- [systemd 공식 문서](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [AWS EC2 사용 설명서](https://docs.aws.amazon.com/ec2/)
- [Let's Encrypt 문서](https://letsencrypt.org/docs/)

## 지원

문제가 발생하면 다음을 확인하세요:
1. `sudo journalctl -u audio-server -n 100`로 로그 확인
2. `logs/` 폴더의 로그 파일 확인
3. 설정 파일이 올바른지 확인
