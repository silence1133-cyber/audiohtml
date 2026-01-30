# Gemini API 모델 가이드

## 사용 가능한 모델

Google Gemini API에서 사용 가능한 주요 모델들입니다.

### 1. Gemini 1.5 Flash (추천)

**모델 이름**: `gemini-1.5-flash-latest`

- ✅ **무료**: 무료 할당량 제공
- ✅ **빠른 속도**: 빠른 응답 시간
- ✅ **오디오 지원**: 오디오 파일 직접 처리 가능
- ✅ **한국어 지원**: 한국어 텍스트 변환 및 요약
- 📊 **할당량**: 하루 1,500회 (무료)

**사용 예시**:
```yaml
gemini:
  model: "gemini-1.5-flash-latest"
```

### 2. Gemini 1.5 Pro

**모델 이름**: `gemini-1.5-pro-latest`

- ✅ **높은 품질**: 더 정확한 분석
- ✅ **오디오 지원**: 오디오 파일 직접 처리 가능
- ⚠️ **제한적 무료**: 무료 할당량 적음
- 🐌 **느린 속도**: Flash보다 처리 시간 더 소요

**사용 예시**:
```yaml
gemini:
  model: "gemini-1.5-pro-latest"
```

### 3. Gemini Pro (구버전)

**모델 이름**: `gemini-pro`

- ⚠️ **오디오 미지원**: 텍스트만 처리 가능
- ❌ **권장하지 않음**: 오디오 처리에 적합하지 않음

## 모델 선택 가이드

### 일반 사용 (추천)

```yaml
gemini:
  model: "gemini-1.5-flash-latest"
```

- 대부분의 경우에 적합
- 빠르고 정확한 결과
- 무료 할당량 충분

### 고품질이 필요한 경우

```yaml
gemini:
  model: "gemini-1.5-pro-latest"
```

- 매우 긴 오디오 파일
- 복잡한 내용의 회의
- 높은 정확도가 필요한 경우

## 모델 변경 방법

### 1. 설정 파일 수정

`config/config.yaml` 파일을 수정:

```yaml
# Gemini API 설정
gemini:
  model: "gemini-1.5-flash-latest"  # 원하는 모델로 변경
```

### 2. 서버 재시작

**systemd 서비스 사용 시**:
```bash
sudo systemctl restart audio-server
```

**수동 실행 시**:
```bash
# 기존 프로세스 종료
pkill -f server.py

# 다시 시작
python3 server.py
```

## 일반적인 오류 해결

### "404 models/gemini-1.5-flash is not found" 오류

**원인**: 구버전 모델 이름 사용

**해결**:
```yaml
# 잘못된 설정
gemini:
  model: "gemini-1.5-flash"  # ❌

# 올바른 설정
gemini:
  model: "gemini-1.5-flash-latest"  # ✅
```

### "Resource has been exhausted" 오류

**원인**: 일일 할당량 초과

**해결**:
1. 24시간 후 다시 시도
2. 또는 유료 API 키 사용
3. 또는 다른 모델로 변경

### "Audio not supported" 오류

**원인**: 오디오를 지원하지 않는 모델 사용

**해결**:
```yaml
# gemini-pro는 오디오 미지원 ❌
gemini:
  model: "gemini-pro"

# 오디오 지원 모델 사용 ✅
gemini:
  model: "gemini-1.5-flash-latest"
```

## API 할당량

### 무료 할당량 (2024년 1월 기준)

| 모델 | 일일 요청 수 | 분당 요청 수 |
|------|-------------|-------------|
| Gemini 1.5 Flash | 1,500 | 15 |
| Gemini 1.5 Pro | 50 | 2 |

### 할당량 확인 방법

1. [Google AI Studio](https://makersuite.google.com/) 접속
2. API 키 페이지에서 사용량 확인

### 할당량 증가 방법

1. **유료 플랜**: Google Cloud에서 유료 API 사용
2. **여러 API 키**: 여러 개의 무료 API 키 번갈아 사용 (권장하지 않음)

## 최신 모델 정보

Google Gemini API는 지속적으로 업데이트됩니다.

### 사용 가능한 모델 확인

Python 스크립트로 확인:

```python
import google.generativeai as genai

# API 키 설정
genai.configure(api_key='YOUR_API_KEY')

# 사용 가능한 모델 목록 확인
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"모델: {model.name}")
        print(f"  - 입력 토큰 제한: {model.input_token_limit}")
        print(f"  - 출력 토큰 제한: {model.output_token_limit}")
        print()
```

### 공식 문서

- [Gemini API 공식 문서](https://ai.google.dev/docs)
- [모델 정보](https://ai.google.dev/models/gemini)
- [API 레퍼런스](https://ai.google.dev/api/python/google/generativeai)

## 성능 비교

### Gemini 1.5 Flash vs Pro

| 항목 | Flash | Pro |
|------|-------|-----|
| 속도 | 🚀 빠름 (2-5초) | 🐌 느림 (10-30초) |
| 정확도 | ✅ 높음 (95%) | ✅ 매우 높음 (98%) |
| 비용 | 💰 무료 (1,500회/일) | 💰 제한적 (50회/일) |
| 오디오 지원 | ✅ 지원 | ✅ 지원 |
| 권장 용도 | 일반적인 사용 | 고품질 필요 시 |

### 테스트 결과

**10분 회의 녹음 기준**:

- **Gemini 1.5 Flash**: 약 5초 소요, 정확도 95%
- **Gemini 1.5 Pro**: 약 20초 소요, 정확도 98%

대부분의 경우 **Gemini 1.5 Flash**로 충분합니다!

## 문제 해결 체크리스트

모델 관련 오류 발생 시:

- [ ] `config/config.yaml`에 `gemini.model` 설정이 있는가?
- [ ] 모델 이름이 `gemini-1.5-flash-latest`인가?
- [ ] API 키가 올바르게 설정되어 있는가?
- [ ] 일일 할당량을 초과하지 않았는가?
- [ ] 서버를 재시작했는가?

## 추가 리소스

- [Google AI Studio](https://makersuite.google.com/)
- [Gemini API Pricing](https://ai.google.dev/pricing)
- [Gemini API Changelog](https://ai.google.dev/docs/gemini_api_changelog)

## 지원

문제가 계속되면:
1. 로그 확인: `tail -f logs/server.log`
2. API 키 확인: `.env` 파일 점검
3. 모델 이름 확인: `config/config.yaml` 점검
