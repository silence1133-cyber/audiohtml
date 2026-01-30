# 📝 블로그 배포 가이드

## HTML 페이지 설정

### 1. API 서버 주소 설정

`index.html` 파일에서 다음 부분을 수정하세요:

```javascript
// 실제 배포 시 여기에 실제 서버 주소를 입력하세요
const API_URL = window.location.origin.includes('localhost') 
    ? 'http://localhost:8000' 
    : 'http://your-server-ip:8000';  // ← 실제 서버 IP로 변경
```

**예시:**
```javascript
const API_URL = window.location.origin.includes('localhost') 
    ? 'http://localhost:8000' 
    : 'http://13.124.45.67:8000';  // AWS EC2 Public IP
```

또는 도메인을 사용하는 경우:
```javascript
const API_URL = 'https://api.yourdomain.com';
```

### 2. HTTPS 사용 시 주의사항

만약 블로그가 HTTPS를 사용한다면, 백엔드 API도 HTTPS를 사용해야 합니다.
(Mixed Content 보안 정책 때문)

**해결 방법:**
1. Nginx 리버스 프록시 + Let's Encrypt SSL 인증서 사용
2. AWS API Gateway + Lambda 사용
3. Cloudflare 사용

## 배포 방법

### 방법 1: 블로그에 직접 삽입
1. `index.html` 파일 내용을 복사
2. 블로그의 HTML 편집 모드에서 붙여넣기
3. API_URL 부분을 실제 서버 주소로 수정

### 방법 2: iframe으로 삽입
```html
<iframe 
    src="https://your-domain.com/audio-tool.html" 
    width="100%" 
    height="800px" 
    frameborder="0">
</iframe>
```

### 방법 3: 별도 페이지로 호스팅
1. `index.html`을 웹 서버에 업로드
2. 블로그에서 해당 페이지로 링크 연결

## AWS EC2 서버 설정

### 1. 백그라운드로 서버 실행
```bash
cd /home/ec2-user/audio-tool
source venv/bin/activate
nohup python server.py > server.log 2>&1 &
```

### 2. 서버 상태 확인
```bash
# 프로세스 확인
ps aux | grep server.py

# 로그 확인
tail -f server.log
```

### 3. 서버 중지
```bash
pkill -f server.py
```

### 4. 보안 그룹 설정
AWS Console에서:
1. EC2 > 보안 그룹 > 인바운드 규칙 편집
2. 규칙 추가:
   - 유형: 사용자 지정 TCP
   - 포트: 8000
   - 소스: 0.0.0.0/0 (모든 IP) 또는 특정 IP

### 5. 자동 시작 설정 (systemd)
서버 재부팅 시 자동으로 시작되도록 설정:

```bash
sudo nano /etc/systemd/system/audio-summary.service
```

```ini
[Unit]
Description=Audio Summary Service
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

서비스 시작:
```bash
sudo systemctl daemon-reload
sudo systemctl start audio-summary
sudo systemctl enable audio-summary
sudo systemctl status audio-summary
```

## 디자인 커스터마이징

### 배경색 변경
현재 블랙 계열로 설정되어 있습니다:

```css
background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
```

다른 색상으로 변경하려면:
```css
/* 블루 계열 */
background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);

/* 그린 계열 */
background: linear-gradient(135deg, #134e5e 0%, #71b280 100%);

/* 레드 계열 */
background: linear-gradient(135deg, #c31432 0%, #240b36 100%);
```

### 버튼 색상 변경
```css
.btn {
    background: linear-gradient(135deg, #2d2d2d 0%, #1a1a1a 100%);
}

.btn:hover {
    background: linear-gradient(135deg, #3d3d3d 0%, #2a2a2a 100%);
}
```

## 보안 권장사항

### 1. API 서버 주소 보호
- HTML 파일에 서버 주소가 하드코딩되어 있으므로, 소스 코드를 보면 주소를 알 수 있습니다
- 이는 공개 API이므로 문제가 없지만, 추가 보안이 필요하다면:
  - API Key 인증 추가
  - Rate Limiting 설정
  - IP 화이트리스트 적용

### 2. CORS 설정
현재 모든 도메인에서 접근 가능합니다.
특정 도메인만 허용하려면 `server.py` 수정:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-blog.com"],  # 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Rate Limiting 추가
과도한 요청 방지:

```bash
pip install slowapi
```

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/summarize")
@limiter.limit("10/hour")  # 시간당 10회 제한
async def summarize(request: Request, file: UploadFile = File(...)):
    # ...
```

## 문제 해결

### Q: "서버에 연결할 수 없습니다" 오류
**A:** 
1. 서버가 실행 중인지 확인: `ps aux | grep server.py`
2. 보안 그룹에서 포트 8000이 열려있는지 확인
3. 방화벽 확인: `sudo firewall-cmd --list-all`

### Q: CORS 오류 발생
**A:** 
1. 서버의 CORS 설정 확인
2. 브라우저 콘솔에서 정확한 오류 메시지 확인
3. HTTP/HTTPS 프로토콜이 일치하는지 확인

### Q: 파일 업로드 후 응답이 없음
**A:**
1. 서버 로그 확인: `tail -f server.log`
2. 파일 크기가 너무 큰지 확인 (최대 100MB)
3. ffmpeg가 설치되어 있는지 확인: `ffmpeg -version`

### Q: "일일 사용량이 초과되었습니다" 오류
**A:**
Gemini API 무료 할당량(1,500회/일)을 초과했습니다. 내일 다시 시도하세요.

## 모니터링

### 로그 모니터링
```bash
# 실시간 로그 확인
tail -f server.log

# 에러만 필터링
grep ERROR server.log

# 최근 100줄 확인
tail -n 100 server.log
```

### 서버 상태 확인
```bash
# API 상태 확인
curl http://localhost:8000/health

# 서비스 상태 확인 (systemd 사용 시)
sudo systemctl status audio-summary
```

---

**서비스 명칭**: 음성 텍스트 변환/요약  
**기술 스택**: FastAPI + Gemini 1.5 Flash  
**디자인**: 블랙 계열 그라데이션
