# 설정 시스템 가이드

## 개요

이 프로젝트는 YAML 기반의 설정 파일 시스템을 사용합니다. 설정 파일을 통해 서버 포트, HTTPS, 로그, CORS 등을 관리할 수 있습니다.

## 주요 변경사항

### 1. 설정 파일 시스템 추가

- **config/config.yaml**: 실제 서버 설정 파일
- **config/config.example.yaml**: 설정 파일 예시 (템플릿)
- **config/README.md**: 상세한 설정 가이드

### 2. HTTPS 지원 추가

서버가 이제 HTTPS를 지원합니다:

- SSL/TLS 인증서를 사용하여 안전한 통신 가능
- 개발용 자체 서명 인증서 생성 가이드 제공
- 프로덕션용 Let's Encrypt 인증서 사용 가이드 제공

### 3. 로깅 시스템 개선

기존 `print` 문을 `logging` 모듈로 전환:

- 로그 파일 자동 생성 (`logs/` 폴더)
- 로그 로테이션 지원 (파일 크기 제한 및 백업)
- 로그 레벨 설정 가능 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- 콘솔과 파일 동시 출력

### 4. 의존성 추가

- **pyyaml**: YAML 설정 파일 파싱

## 빠른 시작

### 1단계: 설정 파일 생성

```powershell
# config.example.yaml을 config.yaml로 복사
Copy-Item config\config.example.yaml config\config.yaml
```

### 2단계: 설정 수정 (선택사항)

`config/config.yaml` 파일을 열어 원하는 설정을 변경합니다.

### 3단계: 의존성 설치

```bash
pip install -r requirements.txt
```

### 4단계: 서버 실행

```bash
python server.py
```

## 설정 예시

### HTTP 모드 (기본)

```yaml
server:
  port: 8000
  host: "0.0.0.0"

https:
  enabled: false

logging:
  log_dir: "logs"
  log_level: "INFO"
  log_file: "server.log"

cors:
  allow_origins:
    - "*"
```

### HTTPS 모드 (SSL 인증서 필요)

```yaml
server:
  port: 443
  host: "0.0.0.0"

https:
  enabled: true
  cert_file: "certs/cert.pem"
  key_file: "certs/key.pem"

logging:
  log_dir: "logs"
  log_level: "INFO"
  log_file: "server.log"

cors:
  allow_origins:
    - "https://yourdomain.com"
```

## SSL 인증서 생성 (개발용)

### Windows에서 OpenSSL 사용

```powershell
# certs 폴더 생성
mkdir certs

# 자체 서명 인증서 생성
openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem -days 365 -nodes
```

### Linux/Mac에서

```bash
# certs 폴더 생성
mkdir certs

# 자체 서명 인증서 생성 (대화형 없이)
openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem -days 365 -nodes \
  -subj "/C=KR/ST=Seoul/L=Seoul/O=MyCompany/OU=IT/CN=localhost"
```

## 로그 확인

로그는 `logs/` 폴더에 저장됩니다:

```bash
# 최신 로그 확인 (Windows)
Get-Content logs\server.log -Tail 50

# 최신 로그 확인 (Linux/Mac)
tail -f logs/server.log
```

## API 사용 예시

### HTTP 모드

```bash
curl -X POST http://localhost:8000/summarize \
  -F "file=@audio.mp3"
```

### HTTPS 모드 (자체 서명 인증서)

```bash
# -k 옵션으로 인증서 검증 스킵 (개발용만!)
curl -k -X POST https://localhost:443/summarize \
  -F "file=@audio.mp3"
```

## 디렉토리 구조

```
audio/
├── config/
│   ├── config.yaml          # 실제 설정 파일 (Git 무시됨)
│   ├── config.example.yaml  # 설정 예시 파일
│   └── README.md           # 설정 상세 가이드
├── logs/
│   └── server.log          # 서버 로그 파일
├── certs/                  # SSL 인증서 (Git 무시됨)
│   ├── cert.pem
│   └── key.pem
├── server.py               # 메인 서버 파일
├── requirements.txt        # Python 의존성
└── .gitignore             # Git 무시 파일 목록
```

## 보안 권장사항

1. **프로덕션 환경**
   - 자체 서명 인증서 대신 Let's Encrypt나 유료 인증서 사용
   - `allow_origins`에 특정 도메인만 지정
   - 로그 레벨을 WARNING 이상으로 설정

2. **파일 권한**
   - SSL 키 파일 권한 제한: `chmod 600 certs/key.pem`
   - 설정 파일 권한 제한: `chmod 600 config/config.yaml`

3. **버전 관리**
   - `config.yaml`과 `certs/` 폴더는 Git에 포함되지 않음
   - 민감한 정보가 포함된 파일은 공유하지 마세요

## 문제 해결

### "설정 파일을 찾을 수 없습니다" 오류

```bash
# config.example.yaml을 config.yaml로 복사
Copy-Item config\config.example.yaml config\config.yaml
```

### "SSL 인증서 파일을 찾을 수 없습니다" 오류

- `https.enabled`를 `false`로 설정하거나
- SSL 인증서를 생성하고 올바른 경로를 설정

### 포트 충돌 오류

```yaml
# config.yaml에서 다른 포트로 변경
server:
  port: 8080  # 또는 다른 사용 가능한 포트
```

## 추가 리소스

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Uvicorn 공식 문서](https://www.uvicorn.org/)
- [Let's Encrypt](https://letsencrypt.org/)
- [OpenSSL](https://www.openssl.org/)

## 지원

문제가 발생하거나 질문이 있으면 이슈를 등록해주세요.
