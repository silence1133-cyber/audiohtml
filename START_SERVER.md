# 🚀 서버 시작 가이드 - 음성 텍스트 변환/요약 서비스

## 1. 환경 설정

### 가상환경 활성화
```bash
cd /home/ec2-user/audio-tool
source venv/bin/activate
```

### 필요한 라이브러리 설치
```bash
pip install -r requirements.txt
```

### API Key 설정
`.env` 파일을 열고 Google Gemini API Key를 입력하세요:
```bash
nano .env
```

```env
GOOGLE_API_KEY=실제_API_키_입력
```

## 2. 서버 실행

### 방법 1: Python으로 직접 실행
```bash
python server.py
```

### 방법 2: Uvicorn으로 실행
```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

### 방법 3: 백그라운드로 실행 (권장)
```bash
nohup python server.py > server.log 2>&1 &
```

서버 로그 확인:
```bash
tail -f server.log
```

프로세스 확인:
```bash
ps aux | grep server.py
```

프로세스 종료:
```bash
pkill -f server.py
```

## 3. 서버 접속 확인

### 로컬에서 테스트
```bash
curl http://localhost:8000/health
```

### 외부에서 접속 (AWS 보안 그룹 설정 필요)
```
http://your-server-ip:8000
```

### API 문서 확인
```
http://your-server-ip:8000/docs
```

## 4. AWS 보안 그룹 설정

AWS EC2 인스턴스의 보안 그룹에서 포트 8000을 열어야 합니다:

1. AWS Console > EC2 > 보안 그룹
2. 인바운드 규칙 편집
3. 규칙 추가:
   - 유형: 사용자 지정 TCP
   - 포트 범위: 8000
   - 소스: 0.0.0.0/0 (모든 IP 허용) 또는 특정 IP

## 5. API 사용 예시

### curl로 테스트
```bash
curl -X POST "http://localhost:8000/summarize" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/audio.mp3"
```

### JavaScript (fetch)로 테스트
```javascript
const formData = new FormData();
formData.append('file', audioFile);

fetch('http://your-server-ip:8000/summarize', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => {
  console.log('요약:', data.summary);
  console.log('원본 텍스트:', data.original_text);
})
.catch(error => console.error('Error:', error));
```

## 6. 문제 해결

### ffmpeg 설치 확인
```bash
ffmpeg -version
```

설치되지 않았다면:
```bash
sudo yum install ffmpeg -y
```

### 포트가 이미 사용 중인 경우
```bash
# 포트 사용 중인 프로세스 확인
lsof -i :8000

# 프로세스 종료
kill -9 <PID>
```

### API 키 오류
`.env` 파일의 API 키가 올바르게 설정되어 있는지 확인하세요.

## 7. 서비스 자동 실행 (systemd)

영구적으로 서비스를 실행하려면 systemd 서비스로 등록하세요:

### 서비스 파일 생성
```bash
sudo nano /etc/systemd/system/audio-summary.service
```

```ini
[Unit]
Description=Audio Text Conversion and Summary Service
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/audio-tool
Environment="PATH=/home/ec2-user/audio-tool/venv/bin"
ExecStart=/home/ec2-user/audio-tool/venv/bin/python /home/ec2-user/audio-tool/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 서비스 시작
```bash
sudo systemctl daemon-reload
sudo systemctl start audio-summary
sudo systemctl enable audio-summary
sudo systemctl status audio-summary
```

### 서비스 관리
```bash
# 서비스 상태 확인
sudo systemctl status audio-summary

# 서비스 중지
sudo systemctl stop audio-summary

# 서비스 재시작
sudo systemctl restart audio-summary

# 로그 확인
sudo journalctl -u audio-summary -f
```

---

**서버 주소**: http://0.0.0.0:8000  
**API 문서**: http://0.0.0.0:8000/docs  
**지원 형식**: mp3, wav, m4a, ogg, flac, aac, wma, webm
