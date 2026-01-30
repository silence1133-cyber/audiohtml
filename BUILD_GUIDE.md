# PyInstaller 빌드 가이드

이 가이드는 `server.py`를 PyInstaller를 사용하여 단일 실행 파일로 빌드하는 방법을 설명합니다.

## 개요

PyInstaller를 사용하면 Python 스크립트를 독립 실행 파일로 변환할 수 있습니다. 이렇게 하면:
- Python이 설치되지 않은 시스템에서도 실행 가능
- 가상환경 없이 실행 가능
- 배포가 간편함

## 사전 준비

### 1. 빌드 환경 준비

**Linux:**
```bash
# Python 3 및 pip 설치
sudo yum install python3 python3-pip -y  # Amazon Linux 2
# 또는
sudo apt-get install python3 python3-pip -y  # Ubuntu

# PyInstaller 설치
pip3 install pyinstaller
```

**Windows:**
```bash
# PyInstaller 설치
pip install pyinstaller
```

### 2. 의존성 패키지 설치

```bash
# 모든 필요한 패키지 설치
pip3 install -r requirements.txt
```

## 빌드 방법

### 방법 1: 자동 빌드 스크립트 사용 (권장)

#### Linux

```bash
# 실행 권한 부여
chmod +x build.sh

# 빌드 실행
./build.sh
```

#### Windows

```bash
# 빌드 실행
build.bat
```

### 방법 2: 수동 빌드

#### Linux/Mac

```bash
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
```

#### Windows

```bash
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
```

## PyInstaller 옵션 설명

- `--onefile`: 단일 실행 파일로 빌드
- `--name audio-server`: 출력 파일 이름 지정
- `--add-data`: 추가 데이터 파일 포함 (설정 예시 파일)
- `--hidden-import`: 자동으로 감지되지 않는 모듈 명시
- `--collect-all`: 패키지의 모든 하위 모듈과 데이터 포함

## 빌드 결과

빌드가 완료되면:

**Linux:**
- 실행 파일: `dist/audio-server`
- 파일 크기: 약 100-150MB

**Windows:**
- 실행 파일: `dist\audio-server.exe`
- 파일 크기: 약 100-150MB

## 배포 준비

빌드된 실행 파일을 배포하려면 다음 파일들이 필요합니다:

```
배포 폴더/
├── audio-server          # 빌드된 실행 파일
├── .env                  # API 키 설정
├── config/
│   └── config.yaml       # 서버 설정 파일
└── logs/                 # 로그 폴더 (자동 생성됨)
```

### 1. 실행 파일 복사

```bash
# Linux
cp dist/audio-server /path/to/deploy/

# Windows
copy dist\audio-server.exe C:\path\to\deploy\
```

### 2. 설정 파일 준비

```bash
# 배포 폴더에서
mkdir -p config
cp config/config.example.yaml config/config.yaml

# config.yaml 수정
nano config/config.yaml
```

### 3. .env 파일 생성

```bash
# 배포 폴더에서
echo 'GOOGLE_API_KEY=your_api_key_here' > .env
```

### 4. FFmpeg 설치 확인

배포 대상 시스템에 FFmpeg가 설치되어 있어야 합니다.

```bash
# Linux
sudo yum install ffmpeg -y  # Amazon Linux 2
# 또는
sudo apt-get install ffmpeg -y  # Ubuntu

# 설치 확인
ffmpeg -version
```

## 실행 방법

### Linux

```bash
# 실행 권한 부여
chmod +x audio-server

# 실행
./audio-server
```

### Windows

```bash
# 실행
audio-server.exe
```

### 백그라운드 실행 (Linux)

```bash
# nohup으로 백그라운드 실행
nohup ./audio-server > server.log 2>&1 &

# 프로세스 확인
ps aux | grep audio-server

# 종료
pkill -f audio-server
```

## systemd 서비스로 등록 (Linux)

빌드된 실행 파일을 systemd 서비스로 등록할 수 있습니다.

### 서비스 파일 생성

```bash
sudo nano /etc/systemd/system/audio-server.service
```

다음 내용 입력:

```ini
[Unit]
Description=Audio Text Conversion Service (PyInstaller Build)
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/audio-deploy
ExecStart=/home/ec2-user/audio-deploy/audio-server
Restart=always
RestartSec=10
StandardOutput=append:/home/ec2-user/audio-deploy/logs/service.log
StandardError=append:/home/ec2-user/audio-deploy/logs/service-error.log

[Install]
WantedBy=multi-user.target
```

**주의**: 경로를 실제 배포 경로로 수정하세요.

### 서비스 활성화

```bash
# systemd 재로드
sudo systemctl daemon-reload

# 서비스 활성화
sudo systemctl enable audio-server

# 서비스 시작
sudo systemctl start audio-server

# 상태 확인
sudo systemctl status audio-server
```

## 문제 해결

### "ModuleNotFoundError" 오류

특정 모듈이 누락된 경우 `--hidden-import` 옵션에 해당 모듈을 추가합니다.

```bash
# 예: requests 모듈 추가
pyinstaller --hidden-import=requests ... server.py
```

### "FileNotFoundError: config.yaml" 오류

설정 파일이 없는 경우:

```bash
# config.example.yaml을 config.yaml로 복사
cp config/config.example.yaml config/config.yaml
```

### "ImportError: cannot import name" 오류

패키지 전체를 수집해야 하는 경우:

```bash
# 예: google.generativeai 패키지 전체 수집
pyinstaller --collect-all google.generativeai ... server.py
```

### 실행 파일 크기가 너무 큼

불필요한 모듈을 제외하려면:

```bash
pyinstaller --onefile --exclude-module matplotlib --exclude-module numpy ...
```

### Linux에서 "Permission denied" 오류

```bash
chmod +x dist/audio-server
```

### FFmpeg 관련 오류

FFmpeg가 설치되어 있는지 확인:

```bash
# 설치 확인
which ffmpeg
ffmpeg -version

# 없으면 설치
sudo yum install ffmpeg -y
```

### .env 파일 읽기 오류

`.env` 파일이 실행 파일과 같은 디렉토리에 있는지 확인:

```bash
ls -la
# .env 파일이 있어야 함
```

## 성능 최적화

### 빌드 시간 단축

```bash
# UPX 압축 비활성화 (빌드 속도 향상, 파일 크기 증가)
pyinstaller --noupx --onefile ... server.py
```

### 실행 파일 크기 최적화

```bash
# UPX 압축 활성화 (파일 크기 감소, 빌드 시간 증가)
# UPX 설치
sudo yum install upx -y  # Amazon Linux 2
# 또는
sudo apt-get install upx -y  # Ubuntu

# 압축 적용된 빌드
pyinstaller --onefile ... server.py
```

## 크로스 플랫폼 빌드 주의사항

PyInstaller는 크로스 플랫폼 빌드를 지원하지 않습니다:
- **Linux 실행 파일**: Linux에서 빌드 필요
- **Windows 실행 파일**: Windows에서 빌드 필요
- **macOS 실행 파일**: macOS에서 빌드 필요

따라서 각 플랫폼에서 별도로 빌드해야 합니다.

## 보안 고려사항

1. **API 키 보호**
   - `.env` 파일을 실행 파일에 포함하지 마세요
   - 배포 시 별도로 관리하세요

2. **SSL 인증서**
   - 인증서 파일을 실행 파일에 포함하지 마세요
   - 외부 파일로 관리하고 config.yaml에서 경로 지정

3. **로그 파일**
   - 민감한 정보가 로그에 기록되지 않도록 주의

## 고급 옵션

### .spec 파일 사용

더 복잡한 빌드 설정이 필요한 경우 `.spec` 파일을 생성하여 사용:

```bash
# .spec 파일 생성
pyi-makespec --onefile server.py

# .spec 파일 수정
nano server.spec

# .spec 파일로 빌드
pyinstaller server.spec
```

### 디버그 모드

빌드 문제를 디버깅하려면:

```bash
# 디버그 정보 출력
pyinstaller --debug=all --onefile ... server.py

# 콘솔 창 표시 (Windows)
pyinstaller --console --onefile ... server.py
```

## 추가 리소스

- [PyInstaller 공식 문서](https://pyinstaller.org/en/stable/)
- [PyInstaller GitHub](https://github.com/pyinstaller/pyinstaller)
- [일반적인 문제 해결](https://github.com/pyinstaller/pyinstaller/wiki/If-Things-Go-Wrong)

## 지원

빌드 중 문제가 발생하면:
1. `build` 폴더의 `warn-*.txt` 파일 확인
2. `--debug=all` 옵션으로 상세 로그 확인
3. 누락된 모듈을 `--hidden-import`로 추가
