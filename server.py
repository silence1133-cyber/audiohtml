import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from pydub import AudioSegment
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# 환경변수 로드
load_dotenv()

# Gemini API 설정
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("GOOGLE_API_KEY가 .env 파일에 설정되지 않았습니다.")

genai.configure(api_key=api_key)

# FastAPI 앱 생성
app = FastAPI(
    title="음성 텍스트 변환/요약",
    description="오디오 파일을 업로드하여 Gemini 1.5 Flash로 텍스트 변환 및 요약",
    version="1.0.0"
)

# CORS 설정 - 모든 도메인에서 접근 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드 허용
    allow_headers=["*"],  # 모든 헤더 허용
)

# 지원하는 오디오 형식
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'ogg', 'flac', 'aac', 'wma', 'webm'}


def convert_audio_to_lightweight_mp3(input_file_path: str) -> str:
    """
    다양한 형식의 오디오 파일을 경량 MP3로 변환합니다.
    비용 절감을 위해 32kbps 비트레이트를 사용합니다.
    
    Args:
        input_file_path: 입력 오디오 파일 경로
    
    Returns:
        변환된 MP3 파일 경로 (임시 파일)
    """
    print(f"[변환] 오디오 변환 시작: {input_file_path}")
    
    # 파일 확장자 확인
    input_path = Path(input_file_path)
    file_extension = input_path.suffix.lower().replace('.', '')
    
    # 임시 파일 생성
    temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
    output_file_path = temp_file.name
    temp_file.close()
    
    try:
        # 오디오 파일 로드
        audio = AudioSegment.from_file(input_file_path, format=file_extension)
        
        # 경량 MP3로 변환 (32kbps, 모노로 변환하여 용량 절감)
        audio = audio.set_channels(1)  # 모노로 변환
        audio.export(
            output_file_path, 
            format='mp3', 
            bitrate='32k',
            parameters=["-ac", "1"]  # 모노 채널 강제
        )
        
        # 파일 크기 확인
        file_size = os.path.getsize(output_file_path) / (1024 * 1024)  # MB
        print(f"[변환] 완료: {output_file_path} ({file_size:.2f}MB)")
        return output_file_path
    
    except Exception as e:
        # 변환 실패 시 임시 파일 삭제
        if os.path.exists(output_file_path):
            os.remove(output_file_path)
        print(f"[오류] 오디오 변환 중 오류 발생: {e}")
        raise


def upload_audio_to_gemini(audio_file_path: str):
    """
    오디오 파일을 Gemini에 업로드합니다.
    
    Args:
        audio_file_path: 업로드할 오디오 파일 경로
    
    Returns:
        업로드된 파일 객체
    """
    print(f"[업로드] Gemini에 파일 업로드 중...")
    
    try:
        uploaded_file = genai.upload_file(audio_file_path)
        print(f"[업로드] 완료: {uploaded_file.name}")
        return uploaded_file
    
    except Exception as e:
        # API 할당량 초과 에러 처리
        error_message = str(e).lower()
        if 'quota' in error_message or 'limit' in error_message or '429' in error_message:
            raise Exception("일일 사용량이 초과되었습니다. 내일 다시 시도해주세요.")
        print(f"[오류] 파일 업로드 중 오류 발생: {e}")
        raise


def summarize_audio_with_gemini(uploaded_file) -> dict:
    """
    Gemini 1.5 Flash 무료 모델을 사용하여 오디오 내용을 텍스트로 변환하고 요약합니다.
    
    Args:
        uploaded_file: Gemini에 업로드된 파일 객체
    
    Returns:
        {"summary": "요약본", "original_text": "원본 텍스트"} 형태의 딕셔너리
    """
    print("[분석] Gemini 1.5 Flash로 음성 분석 중...")
    
    try:
        # Gemini 1.5 Flash 무료 모델 사용
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 1단계: 원본 텍스트 추출
        print("[분석] 1단계 - 음성을 텍스트로 변환 중...")
        transcription_prompt = "이 오디오 파일의 내용을 텍스트로 정확하게 변환해줘. 말한 내용을 그대로 적어줘."
        transcription_response = model.generate_content([transcription_prompt, uploaded_file])
        original_text = transcription_response.text
        
        # 2단계: 요약 생성
        print("[분석] 2단계 - 내용 요약 생성 중...")
        summary_prompt = f"""
다음은 음성을 텍스트로 변환한 내용입니다:

{original_text}

위 내용을 다음 형식으로 요약해줘:

## 📋 주요 내용
- 핵심 주제와 내용을 정리

## 💡 핵심 포인트
- 중요한 내용이나 결정 사항

## 📌 실행 항목 (있는 경우)
- 향후 해야 할 일이나 행동 계획

명확하고 간결하게 작성해줘. 만약 회의 내용이 아니면 그에 맞게 적절히 요약해줘.
"""
        summary_response = model.generate_content(summary_prompt)
        summary = summary_response.text
        
        print("[분석] 완료!")
        return {
            "summary": summary,
            "original_text": original_text
        }
    
    except Exception as e:
        # API 할당량 초과 에러 처리
        error_message = str(e).lower()
        if 'quota' in error_message or 'limit' in error_message or '429' in error_message:
            raise Exception("일일 사용량이 초과되었습니다. 내일 다시 시도해주세요.")
        print(f"[오류] 요약 생성 중 오류 발생: {e}")
        raise


def process_audio_file(input_file_path: str) -> dict:
    """
    오디오 파일을 처리하여 텍스트 변환 및 요약을 생성합니다.
    처리가 완료되면 변환된 파일을 자동으로 삭제합니다 (개인정보 보호).
    
    Args:
        input_file_path: 입력 오디오 파일 경로
    
    Returns:
        {"summary": "요약본", "original_text": "원본 텍스트"} 형태의 딕셔너리
    """
    mp3_file_path = None
    
    try:
        # 1. 오디오 파일을 경량 MP3로 변환
        mp3_file_path = convert_audio_to_lightweight_mp3(input_file_path)
        
        # 2. Gemini에 파일 업로드
        uploaded_file = upload_audio_to_gemini(mp3_file_path)
        
        # 3. Gemini로 요약 생성
        result = summarize_audio_with_gemini(uploaded_file)
        
        return result
    
    except Exception as e:
        print(f"[오류] 처리 중 오류 발생: {e}")
        raise
    
    finally:
        # 처리 완료 후 변환된 MP3 파일 삭제 (개인정보 보호)
        if mp3_file_path and os.path.exists(mp3_file_path):
            try:
                os.remove(mp3_file_path)
                print(f"[삭제] 임시 파일 삭제 완료: {mp3_file_path}")
            except Exception as e:
                print(f"[오류] 임시 파일 삭제 실패: {e}")


# API 엔드포인트
@app.get("/")
async def root():
    """서비스 정보"""
    return {
        "service": "음성 텍스트 변환/요약",
        "version": "1.0.0",
        "powered_by": "Gemini 1.5 Flash",
        "endpoints": {
            "/summarize": "POST - 오디오 파일 업로드 및 텍스트 변환/요약",
            "/health": "GET - 서버 상태 확인"
        }
    }


@app.get("/health")
async def health():
    """서버 상태 확인"""
    return {
        "status": "ok",
        "message": "서버가 정상적으로 작동 중입니다."
    }


@app.post("/summarize")
async def summarize(file: UploadFile = File(...)):
    """
    오디오 파일을 업로드하여 텍스트 변환 및 요약 생성
    
    Args:
        file: 오디오 파일 (mp3, wav, m4a, ogg, flac, aac, wma, webm)
    
    Returns:
        JSON: {"summary": "요약본", "original_text": "원본 텍스트"}
    """
    uploaded_file_path = None
    
    try:
        # 파일 확장자 확인
        file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"지원하지 않는 파일 형식입니다. 지원 형식: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # 임시 파일로 저장
        temp_file = tempfile.NamedTemporaryFile(suffix=f'.{file_extension}', delete=False)
        uploaded_file_path = temp_file.name
        
        # 파일 저장
        with open(uploaded_file_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        # 파일 크기 확인
        file_size = os.path.getsize(uploaded_file_path) / (1024 * 1024)  # MB
        print(f"\n{'='*60}")
        print(f"[요청] 새로운 요약 요청")
        print(f"[파일] {file.filename} ({file_size:.2f}MB)")
        print(f"{'='*60}")
        
        # 오디오 처리 및 요약 생성
        result = process_audio_file(uploaded_file_path)
        
        print(f"{'='*60}")
        print(f"[완료] 요약 생성 완료")
        print(f"{'='*60}\n")
        
        # 성공 응답
        return JSONResponse(content={
            "summary": result["summary"],
            "original_text": result["original_text"]
        })
    
    except Exception as e:
        error_message = str(e)
        print(f"[오류] {error_message}")
        
        # 사용자 친화적인 에러 메시지
        if "일일 사용량이 초과" in error_message:
            raise HTTPException(
                status_code=429,
                detail="일일 사용량이 초과되었습니다. 내일 다시 시도해주세요."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"처리 중 오류가 발생했습니다: {error_message}"
            )
    
    finally:
        # 업로드된 원본 파일 삭제 (개인정보 보호)
        if uploaded_file_path and os.path.exists(uploaded_file_path):
            try:
                os.remove(uploaded_file_path)
                print(f"[삭제] 업로드 파일 삭제 완료: {uploaded_file_path}")
            except Exception as e:
                print(f"[오류] 업로드 파일 삭제 실패: {e}")


if __name__ == "__main__":
    print("=" * 70)
    print("🚀 음성 텍스트 변환/요약 서비스 시작 (Powered by Gemini 1.5 Flash)")
    print("=" * 70)
    print("서버 주소: http://0.0.0.0:8000")
    print("API 문서: http://0.0.0.0:8000/docs")
    print("지원 형식: mp3, wav, m4a, ogg, flac, aac, wma, webm")
    print("주의: 무료 API 사용으로 하루 1,500회 제한이 있습니다.")
    print("=" * 70)
    
    # Uvicorn으로 서버 시작
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
