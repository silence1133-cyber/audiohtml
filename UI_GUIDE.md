# 🎨 새로운 UI 가이드

## 개요

TailwindCSS를 사용한 심플하고 모던한 디자인으로 완전히 새롭게 제작되었습니다.

## 주요 특징

### 1. 디자인 ✨
- **TailwindCSS CDN** 사용
- **Inter 폰트** 적용 (Google Fonts)
- **다크 그라데이션 배경** (Gray-900 → Gray-800)
- **화이트 메인 카드** (깔끔한 대비)
- **그라데이션 결과 박스** (Blue 계열, Gray 계열)

### 2. 레이아웃 📐
```
┌─────────────────────────────────────┐
│     🎙️ 음성 텍스트 변환/요약        │
│   Powered by Gemini 1.5 Flash      │
├─────────────────────────────────────┤
│  ┌───────────────────────────────┐  │
│  │                               │  │
│  │       📁 파일 업로드 영역      │  │
│  │    (드래그 앤 드롭 지원)       │  │
│  │                               │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │  선택된 파일: test.mp3 (2.5MB) │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │        요약하기 버튼           │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │    ⏳ AI가 음성을 분석 중...   │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │  📝 요약 결과         [복사]   │  │
│  │  ... 내용 ...                 │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌───────────────────────────────┐  │
│  │  📄 변환된 텍스트     [복사]   │  │
│  │  ... 내용 ...                 │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
     하루 1,500회 제한이 있습니다
```

### 3. 색상 팔레트 🎨

#### 배경
```css
background: linear-gradient(to bottom right, #111827, #1f2937, #111827)
/* Gray-900 → Gray-800 → Gray-900 */
```

#### 메인 카드
```css
background: white
shadow: 2xl (큰 그림자)
border-radius: 1rem
```

#### 업로드 영역
```css
border: 3px dashed gray-300
hover: border-gray-400, bg-gray-50
drag-over: border-gray-800, bg-gray-900
```

#### 버튼
```css
background: gray-900
hover: gray-800
disabled: gray-300
```

#### 결과 박스
```css
/* 요약 결과 */
background: linear-gradient(to bottom right, blue-50, indigo-50)

/* 변환된 텍스트 */
background: linear-gradient(to bottom right, gray-50, gray-100)
```

### 4. 기능 설명 ⚙️

#### 파일 업로드
- **클릭**: 업로드 영역 클릭 → 파일 선택 대화상자
- **드래그 앤 드롭**: 파일을 드래그하여 업로드 영역에 드롭
- **지원 형식**: MP3, WAV, M4A, OGG, FLAC, AAC, WMA, WEBM

#### 로딩 상태
- 흰색 스피너 애니메이션
- "AI가 음성을 분석 중입니다..." 메시지
- "잠시만 기다려주세요" 서브 메시지

#### 결과 표시
- **요약 결과**: 파란색 그라데이션 박스
- **변환된 텍스트**: 회색 그라데이션 박스
- 각 박스마다 **복사 버튼** 제공

#### 에러 처리
- 빨간색 배경 (red-50)
- 빨간색 테두리 (red-200)
- "오류 발생" 헤더 + 상세 메시지

### 5. 반응형 디자인 📱

```css
/* 모바일 */
padding: 1rem (16px)

/* 태블릿/데스크톱 */
max-width: 56rem (896px)
padding: 2rem (32px)
```

모든 요소가 자동으로 화면 크기에 맞춰 조정됩니다.

## 코드 구조

### HTML 구조
```html
<body> (다크 그라데이션 배경)
  └─ <div> (최대 너비 컨테이너)
      ├─ 헤더 (타이틀 + 서브타이틀)
      ├─ 메인 카드 (화이트 배경)
      │   ├─ 파일 업로드 영역
      │   ├─ 선택된 파일 정보
      │   ├─ 요약하기 버튼
      │   ├─ 로딩 스피너
      │   ├─ 에러 메시지
      │   └─ 결과 영역
      │       ├─ 요약 결과
      │       └─ 변환된 텍스트
      └─ 푸터 (사용 제한 안내)
```

### JavaScript 함수
```javascript
// 이벤트 핸들러
- uploadArea.click → fileInput.click()
- fileInput.change → handleFileSelect()
- uploadArea.dragover → drag-over 클래스 추가
- uploadArea.drop → handleFileSelect()
- uploadBtn.click → API 요청

// 헬퍼 함수
- handleFileSelect() : 파일 검증 및 UI 업데이트
- showLoading() : 로딩 표시
- hideLoading() : 로딩 숨김
- showResult() : 결과 표시
- hideResult() : 결과 숨김
- showError() : 에러 표시
- hideError() : 에러 숨김
- copyToClipboard() : 클립보드 복사
```

## 커스터마이징 가이드

### 배경색 변경
```html
<!-- 현재 (다크 그라데이션) -->
<body class="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">

<!-- 블루 계열 -->
<body class="bg-gradient-to-br from-blue-900 via-blue-800 to-blue-900">

<!-- 퍼플 계열 -->
<body class="bg-gradient-to-br from-purple-900 via-purple-800 to-purple-900">
```

### 버튼 색상 변경
```html
<!-- 현재 (블랙) -->
<button class="bg-gray-900 hover:bg-gray-800">

<!-- 블루 -->
<button class="bg-blue-600 hover:bg-blue-700">

<!-- 그린 -->
<button class="bg-green-600 hover:bg-green-700">
```

### 결과 박스 색상 변경
```html
<!-- 요약 결과 (현재: 블루) -->
<div class="bg-gradient-to-br from-blue-50 to-indigo-50">

<!-- 그린 -->
<div class="bg-gradient-to-br from-green-50 to-emerald-50">

<!-- 퍼플 -->
<div class="bg-gradient-to-br from-purple-50 to-pink-50">
```

## API 설정

### 로컬 개발
```javascript
const API_URL = 'http://localhost:8000';
```

### 프로덕션 배포
```javascript
const API_URL = 'http://13.124.45.67:8000';  // 실제 서버 IP
```

또는 도메인 사용:
```javascript
const API_URL = 'https://api.yourdomain.com';
```

## 브라우저 호환성

- ✅ Chrome/Edge (최신)
- ✅ Firefox (최신)
- ✅ Safari (최신)
- ✅ 모바일 브라우저

필요한 기능:
- Fetch API
- FormData
- Async/Await
- Clipboard API

## 성능 최적화

### CDN 사용
- TailwindCSS: CDN에서 로드 (빠른 로딩)
- Inter 폰트: Google Fonts (캐시 활용)

### 최소 의존성
- 외부 라이브러리 없음
- 순수 JavaScript (Vanilla JS)
- 가벼운 HTML/CSS

### 번들 크기
```
HTML: ~6KB
TailwindCSS CDN: ~3MB (첫 로드 후 캐시)
Inter 폰트: ~100KB (첫 로드 후 캐시)
```

## 접근성 (Accessibility)

- ✅ 시맨틱 HTML 태그 사용
- ✅ 키보드 내비게이션 지원
- ✅ 스크린 리더 호환
- ✅ 명확한 에러 메시지
- ✅ 적절한 색상 대비

## 테스트 체크리스트

- [ ] 파일 업로드 (클릭)
- [ ] 파일 업로드 (드래그 앤 드롭)
- [ ] 잘못된 파일 형식 업로드
- [ ] 요약 버튼 클릭
- [ ] 로딩 상태 표시
- [ ] 성공 시 결과 표시
- [ ] 실패 시 에러 표시
- [ ] 복사 버튼 동작
- [ ] 모바일 반응형
- [ ] 다크 모드 호환

## 배포 전 체크리스트

### HTML 파일
- [ ] API_URL을 실제 서버 주소로 변경 (130번째 줄)
- [ ] 타이틀 및 메타 태그 확인
- [ ] 지원 파일 형식 확인

### 서버
- [ ] CORS 설정 확인 (모든 도메인 허용)
- [ ] 포트 8000 오픈
- [ ] Gemini API Key 설정
- [ ] ffmpeg 설치 확인

### 테스트
- [ ] 로컬 환경에서 테스트
- [ ] 실제 서버에서 테스트
- [ ] 다양한 브라우저에서 테스트
- [ ] 모바일에서 테스트

---

**심플하고 모던한 UI가 완성되었습니다!** 🎉

**주요 개선사항:**
- ✅ TailwindCSS 사용으로 코드 간소화
- ✅ 깔끔한 다크 그라데이션 배경
- ✅ 직관적인 드래그 앤 드롭
- ✅ 명확한 로딩 및 에러 표시
- ✅ 아름다운 그라데이션 결과 박스
- ✅ 완벽한 반응형 디자인
