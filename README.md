# 🎙️ 음성 텍스트 변환/요약 서비스

Google Gemini 1.5 Flash 무료 API를 사용하여 음성 파일을 텍스트로 변환하고 자동으로 요약해주는 서비스입니다.

## ✨ 주요 기능

- 📁 다양한 오디오 형식 지원 (m4a, wav, mp3, ogg, flac 등)
- 🔄 자동 오디오 변환 (경량 MP3 32kbps)
- 🤖 AI 기반 음성-텍스트 변환 및 요약
  - 음성을 정확한 텍스트로 변환
  - 주요 내용 자동 요약
  - 핵심 포인트 추출
  - 실행 항목 정리 (있는 경우)
- 🔒 개인정보 보호 (처리 후 파일 자동 삭제)
- 💰 완전 무료 (Google Gemini 1.5 Flash 무료 API 사용)
- 🚀 Linux 서비스로 자동 시작/관리 지원
- 🔐 HTTPS/SSL 지원
- 📊 로깅 시스템 내장

## 📚 문서

- **[SERVICE_GUIDE.md](SERVICE_GUIDE.md)** - Linux 서비스 설치 가이드 (AWS Linux)
- **[CONFIG_GUIDE.md](CONFIG_GUIDE.md)** - 설정 시스템 가이드 (포트, HTTPS, 로그)
- **[config/README.md](config/README.md)** - 상세 설정 및 SSL 인증서 가이드

## 📋 사전 요구사항

### 1. Python 설치
Python 3.8 이상이 필요합니다.

```bash
python --version
```

### 2. ffmpeg 설치
오디오 변환을 위해 ffmpeg가 필요합니다.

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Amazon Linux/CentOS:**
```bash
sudo yum install ffmpeg
```

**Windows:**
[ffmpeg 공식 사이트](https://ffmpeg.org/download.html)에서 다운로드

### 3. Google Gemini API Key 발급
1. [Google AI Studio](https://makersuite.google.com/app/apikey) 접속
2. "Create API Key" 클릭
3. 발급받은 API Key 복사

## 🚀 설치 및 사용 방법

### 방법 1: AWS Linux 서비스로 설치 (추천)

가상환경 없이 systemd 서비스로 설치하여 자동 시작/관리가 가능합니다.

#### 빠른 설치

```bash
# 1. 프로젝트 다운로드
git clone <repository-url>
cd <project-directory>

# 2. API Key 설정
echo 'GOOGLE_API_KEY=your_api_key_here' > .env

# 3. 설정 파일 생성
cp config/config.example.yaml config/config.yaml

# 4. 자동 설치 스크립트 실행
chmod +x install.sh
sudo ./install.sh

# 5. 서비스 시작
sudo systemctl start audio-server
```

#### 서비스 관리

```bash
# 시작
sudo systemctl start audio-server

# 중지
sudo systemctl stop audio-server

# 상태 확인
sudo systemctl status audio-server

# 로그 확인
sudo journalctl -u audio-server -f
```

**자세한 내용**: [SERVICE_GUIDE.md](SERVICE_GUIDE.md) 참고

---

### 방법 2: 수동 실행 (개발/테스트용)

#### 1. 프로젝트 다운로드
```bash
git clone <repository-url>
cd <project-directory>
```

#### 2. 가상환경 생성 및 활성화
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Linux/macOS)
source venv/bin/activate

# 가상환경 활성화 (Windows)
venv\Scripts\activate
```

#### 3. 필요한 라이브러리 설치
```bash
pip install -r requirements.txt
```

#### 4. API Key 설정
`.env` 파일을 생성하고 발급받은 API Key를 입력합니다:

```env
GOOGLE_API_KEY=여기에_발급받은_API_KEY_입력
```

#### 5. 설정 파일 생성
```bash
cp config/config.example.yaml config/config.yaml
```

#### 6. 프로그램 실행

**CLI 모드 (단일 파일 처리):**
```bash
python main.py
```

**서버 모드 (API 서버):**
```bash
python server.py
```

서버 접속: http://localhost:8000

#### 7. 오디오 파일 경로 입력 (CLI 모드)
프롬프트가 나타나면 회의 녹음 파일의 경로를 입력합니다:

```
오디오 파일 경로를 입력하세요: /path/to/meeting.m4a
```

#### 8. 결과 확인
- 화면에 요약 결과가 출력됩니다
- 동일한 폴더에 `.txt` 파일로 저장됩니다

## 📊 사용 제한

- **무료 API 할당량**: 하루 1,500회
- **파일 크기**: 제한 없음 (단, 처리 시간이 오래 걸릴 수 있음)
- **비용 절감**: 32kbps 모노 MP3로 변환하여 전송량 최소화

## 🔐 개인정보 보호

이 서비스는 개인정보를 철저히 보호합니다:

1. 업로드된 오디오는 변환 후 즉시 삭제됩니다
2. 변환된 MP3 파일도 처리 완료 후 자동 삭제됩니다
3. 서버에 어떠한 파일도 남지 않습니다

## ⚠️ 문제 해결

### "일일 사용량이 초과되었습니다" 오류
- Gemini API의 일일 무료 할당량(1,500회)을 초과했습니다
- 내일 다시 시도하거나, 유료 API Key를 사용하세요

### "ffmpeg를 찾을 수 없습니다" 오류
- ffmpeg가 설치되어 있는지 확인하세요
- 설치 후 터미널을 재시작하세요

### "GOOGLE_API_KEY가 설정되지 않았습니다" 오류
- `.env` 파일에 API Key가 올바르게 입력되었는지 확인하세요
- 파일 이름이 정확히 `.env`인지 확인하세요

## 📝 라이선스

이 프로젝트는 개인 및 상업적 용도로 자유롭게 사용 가능합니다.

## 🤝 기여

버그 리포트나 기능 제안은 언제든 환영합니다!

---

**Made with ❤️ for everyone who needs meeting summaries**
