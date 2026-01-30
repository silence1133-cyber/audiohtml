# 설정 파일 가이드

이 폴더는 서버 설정 파일을 관리합니다.

## 설정 파일 생성

1. `config.example.yaml` 파일을 `config.yaml`로 복사합니다:

```bash
# Windows (PowerShell)
Copy-Item config.example.yaml config.yaml

# Linux/Mac
cp config.example.yaml config.yaml
```

2. `config.yaml` 파일을 수정하여 원하는 설정을 적용합니다.

## 설정 항목 설명

### 서버 설정 (server)

- `port`: 서버가 사용할 포트 번호 (기본값: 8000)
- `host`: 서버 호스트 주소 (기본값: "0.0.0.0" - 모든 인터페이스에서 접근 가능)

### HTTPS 설정 (https)

- `enabled`: HTTPS 사용 여부 (true/false)
- `cert_file`: SSL 인증서 파일 경로
- `key_file`: SSL 개인 키 파일 경로

**HTTPS를 사용하려면:**

1. SSL 인증서와 키 파일을 생성하거나 준비합니다 (아래 "SSL 인증서 생성" 참고)
2. `enabled`를 `true`로 설정
3. `cert_file`과 `key_file` 경로를 올바르게 설정

### 로그 설정 (logging)

- `log_dir`: 로그 파일이 저장될 디렉토리 경로
- `log_level`: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `log_file`: 로그 파일 이름
- `max_bytes`: 로그 파일 최대 크기 (바이트 단위, 기본값: 10MB)
- `backup_count`: 백업 로그 파일 개수 (로그 로테이션)

### CORS 설정 (cors)

- `allow_origins`: 허용할 도메인 목록 (["*"]는 모든 도메인 허용)
- `allow_credentials`: 인증 정보 허용 여부
- `allow_methods`: 허용할 HTTP 메소드
- `allow_headers`: 허용할 HTTP 헤더

## SSL 인증서 생성

### 개발/테스트용 자체 서명 인증서 (Self-Signed Certificate)

**주의**: 자체 서명 인증서는 개발/테스트 환경에서만 사용하세요. 프로덕션 환경에서는 공인 인증서를 사용해야 합니다.

#### Windows (PowerShell)

```powershell
# certs 폴더 생성
mkdir certs

# OpenSSL이 설치되어 있는 경우
openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem -days 365 -nodes

# 또는 PowerShell의 New-SelfSignedCertificate 사용
$cert = New-SelfSignedCertificate -DnsName "localhost" -CertStoreLocation "cert:\LocalMachine\My" -NotAfter (Get-Date).AddYears(1)
$password = ConvertTo-SecureString -String "your_password" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath "certs\cert.pfx" -Password $password

# PFX를 PEM으로 변환 (OpenSSL 필요)
openssl pkcs12 -in certs/cert.pfx -out certs/cert.pem -clcerts -nokeys -passin pass:your_password
openssl pkcs12 -in certs/cert.pfx -out certs/key.pem -nocerts -nodes -passin pass:your_password
```

#### Linux/Mac

```bash
# certs 폴더 생성
mkdir certs

# OpenSSL로 자체 서명 인증서 생성
openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem -days 365 -nodes

# 대화형 프롬프트에서 정보 입력 (또는 -subj 옵션으로 한 번에 설정)
openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem -days 365 -nodes \
  -subj "/C=KR/ST=Seoul/L=Seoul/O=MyCompany/OU=IT/CN=localhost"
```

### 프로덕션용 공인 인증서

프로덕션 환경에서는 다음 중 하나를 사용하세요:

1. **Let's Encrypt** (무료): [certbot](https://certbot.eff.org/) 사용
2. **유료 SSL 인증서**: 신뢰할 수 있는 인증 기관(CA)에서 구매

#### Let's Encrypt 사용 예시 (Linux)

```bash
# Certbot 설치
sudo apt-get update
sudo apt-get install certbot

# 인증서 발급 (standalone 모드)
sudo certbot certonly --standalone -d yourdomain.com

# 발급된 인증서 경로
# cert_file: /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# key_file: /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

## 보안 주의사항

1. **config.yaml 파일 보호**
   - 이 파일은 `.gitignore`에 포함되어 있으므로 Git에 커밋되지 않습니다
   - 민감한 정보가 포함될 수 있으므로 공개하지 마세요

2. **SSL 키 파일 보호**
   - SSL 개인 키 파일(key.pem)은 절대 공유하거나 공개하지 마세요
   - `certs/` 폴더는 `.gitignore`에 포함되어 있습니다

3. **프로덕션 환경**
   - 자체 서명 인증서 대신 공인 인증서를 사용하세요
   - 적절한 파일 권한 설정 (키 파일은 읽기 전용으로)
   - 정기적으로 인증서를 갱신하세요

## 예시

### HTTP 모드 (기본)

```yaml
server:
  port: 8000
  host: "0.0.0.0"

https:
  enabled: false
```

### HTTPS 모드

```yaml
server:
  port: 443  # HTTPS 표준 포트
  host: "0.0.0.0"

https:
  enabled: true
  cert_file: "certs/cert.pem"
  key_file: "certs/key.pem"
```

### 특정 도메인만 허용하는 CORS 설정

```yaml
cors:
  allow_origins:
    - "https://myapp.com"
    - "https://www.myapp.com"
  allow_credentials: true
  allow_methods:
    - "GET"
    - "POST"
  allow_headers:
    - "Content-Type"
    - "Authorization"
```

## 문제 해결

### "SSL 인증서 파일을 찾을 수 없습니다" 오류

- `cert_file`과 `key_file` 경로가 올바른지 확인하세요
- 파일이 실제로 존재하는지 확인하세요
- 상대 경로 대신 절대 경로를 사용해보세요

### HTTPS 연결 시 "안전하지 않음" 경고

- 자체 서명 인증서를 사용하는 경우 정상입니다
- 브라우저에서 예외를 추가하거나 공인 인증서를 사용하세요

### 포트가 이미 사용 중

- 다른 포트 번호로 변경하세요
- 또는 기존 프로세스를 종료하세요

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID [프로세스ID] /F

# Linux/Mac
lsof -i :8000
kill [프로세스ID]
```
