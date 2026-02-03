import os
import sys
import tempfile
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
import google.generativeai as genai
from pydub import AudioSegment
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import yaml
import httpx

# 환경변수 로드
load_dotenv()


# 설정 파일 로드 함수
def load_config(config_path: str = "config/config.yaml") -> dict:
    """
    YAML 설정 파일을 로드합니다.
    
    Args:
        config_path: 설정 파일 경로
    
    Returns:
        설정 딕셔너리
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config
    except FileNotFoundError:
        print(f"[오류] 설정 파일을 찾을 수 없습니다: {config_path}")
        print(f"[안내] config.example.yaml을 참고하여 {config_path} 파일을 생성하세요.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"[오류] 설정 파일 파싱 중 오류 발생: {e}")
        sys.exit(1)


# 로깅 설정 함수
def setup_logging(config: dict):
    """
    로깅 시스템을 설정합니다.
    
    Args:
        config: 설정 딕셔너리
    """
    log_config = config.get('logging', {})
    # log_dir와 log_path 둘 다 지원 (하위 호환성)
    log_dir = log_config.get('log_dir') or log_config.get('log_path', 'logs')
    log_file = log_config.get('log_file', 'server.log')
    log_level = log_config.get('log_level', 'INFO')
    max_bytes = log_config.get('max_bytes', 10485760)  # 10MB
    backup_count = log_config.get('backup_count', 5)
    
    # 로그 디렉토리 생성
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, log_file)
    
    # 로거 설정
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # 기존 핸들러 제거
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 파일 핸들러 (로테이션 지원)
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    logging.info(f"로깅 시스템 초기화 완료 (파일: {log_file_path}, 레벨: {log_level})")


# 설정 로드
config = load_config()

# 로깅 설정
setup_logging(config)

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

# CORS 설정 - 설정 파일에서 읽어오기
cors_config = config.get('cors', {})
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config.get('allow_origins', ["*"]),
    allow_credentials=cors_config.get('allow_credentials', True),
    allow_methods=cors_config.get('allow_methods', ["*"]),
    allow_headers=cors_config.get('allow_headers', ["*"]),
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
    logging.info(f"[변환] 오디오 변환 시작: {input_file_path}")
    
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
        logging.info(f"[변환] 완료: {output_file_path} ({file_size:.2f}MB)")
        return output_file_path
    
    except Exception as e:
        # 변환 실패 시 임시 파일 삭제
        if os.path.exists(output_file_path):
            os.remove(output_file_path)
        logging.error(f"[오류] 오디오 변환 중 오류 발생: {e}")
        raise


def upload_audio_to_gemini(audio_file_path: str):
    """
    오디오 파일을 Gemini에 업로드합니다.
    
    Args:
        audio_file_path: 업로드할 오디오 파일 경로
    
    Returns:
        업로드된 파일 객체
    """
    logging.info(f"[업로드] Gemini에 파일 업로드 중...")
    
    try:
        uploaded_file = genai.upload_file(audio_file_path)
        logging.info(f"[업로드] 완료: {uploaded_file.name}")
        return uploaded_file
    
    except Exception as e:
        # API 할당량 초과 에러 처리
        error_message = str(e).lower()
        if 'quota' in error_message or 'limit' in error_message or '429' in error_message:
            raise Exception("일일 사용량이 초과되었습니다. 내일 다시 시도해주세요.")
        logging.error(f"[오류] 파일 업로드 중 오류 발생: {e}")
        raise


def summarize_audio_with_gemini(uploaded_file) -> dict:
    """
    Gemini 1.5 Flash 무료 모델을 사용하여 오디오 내용을 텍스트로 변환하고 요약합니다.
    
    Args:
        uploaded_file: Gemini에 업로드된 파일 객체
    
    Returns:
        {"summary": "요약본", "original_text": "원본 텍스트"} 형태의 딕셔너리
    """
    # 설정에서 모델 이름 가져오기
    gemini_config = config.get('gemini', {})
    model_name = gemini_config.get('model', 'gemini-1.5-flash-latest')
    
    logging.info(f"[분석] Gemini ({model_name})로 음성 분석 중...")
    
    try:
        # Gemini 모델 사용
        model = genai.GenerativeModel(model_name)
        
        # 1단계: 원본 텍스트 추출
        logging.info("[분석] 1단계 - 음성을 텍스트로 변환 중...")
        transcription_prompt = "이 오디오 파일의 내용을 텍스트로 정확하게 변환해줘. 말한 내용을 그대로 적어줘."
        transcription_response = model.generate_content([transcription_prompt, uploaded_file])
        original_text = transcription_response.text
        
        # 2단계: 요약 생성
        logging.info("[분석] 2단계 - 내용 요약 생성 중...")
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
        
        logging.info("[분석] 완료!")
        return {
            "summary": summary,
            "original_text": original_text
        }
    
    except Exception as e:
        # API 할당량 초과 에러 처리
        error_message = str(e).lower()
        if 'quota' in error_message or 'limit' in error_message or '429' in error_message:
            raise Exception("일일 사용량이 초과되었습니다. 내일 다시 시도해주세요.")
        logging.error(f"[오류] 요약 생성 중 오류 발생: {e}")
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
        logging.error(f"[오류] 처리 중 오류 발생: {e}")
        raise
    
    finally:
        # 처리 완료 후 변환된 MP3 파일 삭제 (개인정보 보호)
        if mp3_file_path and os.path.exists(mp3_file_path):
            try:
                os.remove(mp3_file_path)
                logging.info(f"[삭제] 임시 파일 삭제 완료: {mp3_file_path}")
            except Exception as e:
                logging.error(f"[오류] 임시 파일 삭제 실패: {e}")


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
            "/seoulapi": "GET - 서울시 지하철 수유실 정보 API 프록시",
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


@app.get("/seoulapi")
async def seoul_api_proxy():
    """
    서울시 지하철 수유실 정보 API 프록시
    실제 서울시 API를 호출하여 결과를 반환합니다.
    """
    try:
        # 환경변수에서 서울시 API 키 가져오기
        seoul_api_key = os.getenv('SEOUL_API_KEY')
        if not seoul_api_key:
            logging.warning("[서울API] SEOUL_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
            raise HTTPException(
                status_code=500,
                detail="서울시 API 키가 설정되지 않았습니다. 관리자에게 문의하세요."
            )
        
        # 서울시 지하철 수유실 정보 API URL
        # 참고: http://openapi.seoul.go.kr:8088/{KEY}/json/getFcNrsrm/{START_INDEX}/{END_INDEX}/
        api_url = f"http://openapi.seoul.go.kr:8088/{seoul_api_key}/json/getFcNrsrm/1/1000/"
        
        logging.info(f"[서울API] 서울시 API 호출 중: {api_url.replace(seoul_api_key, '***KEY***')}")
        
        # 비동기 HTTP 클라이언트로 서울시 API 호출
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(api_url)
            
            # 응답 상태 코드 확인
            if response.status_code != 200:
                logging.error(f"[서울API] HTTP 오류: {response.status_code}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"서울시 API 호출 실패 (HTTP {response.status_code})"
                )
            
            # JSON 응답 파싱
            data = response.json()
            
            # 서울시 API 응답 구조 확인 및 변환
            # 서울시 API: { "nurseryInfo": { "row": [...], "list_total_count": N } }
            # 변환 목표: { "response": { "body": { "items": { "item": [...] }, "totalCount": N } } }
            
            if 'nurseryInfo' in data:
                nursery_info = data['nurseryInfo']
                rows = nursery_info.get('row', [])
                total_count = nursery_info.get('list_total_count', len(rows))
                
                # 응답 데이터 로깅
                logging.info(f"[서울API] 성공: {total_count}건의 데이터 수신")
                
                # index.html이 기대하는 형식으로 변환
                transformed_data = {
                    "response": {
                        "body": {
                            "items": {
                                "item": rows
                            },
                            "totalCount": total_count
                        }
                    }
                }
                
                return JSONResponse(content=transformed_data)
            else:
                logging.warning(f"[서울API] 예상치 못한 응답 구조: {list(data.keys())}")
                # 원본 데이터 그대로 반환
                return JSONResponse(content=data)
    
    except httpx.TimeoutException:
        logging.error("[서울API] 요청 타임아웃")
        raise HTTPException(
            status_code=504,
            detail="서울시 API 응답 시간 초과"
        )
    except httpx.RequestError as e:
        logging.error(f"[서울API] 네트워크 오류: {e}")
        raise HTTPException(
            status_code=502,
            detail=f"서울시 API 연결 실패: {str(e)}"
        )
    except Exception as e:
        logging.error(f"[서울API] 오류 발생: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"서버 오류: {str(e)}"
        )


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
        logging.info("="*60)
        logging.info(f"[요청] 새로운 요약 요청")
        logging.info(f"[파일] {file.filename} ({file_size:.2f}MB)")
        logging.info("="*60)
        
        # 오디오 처리 및 요약 생성
        result = process_audio_file(uploaded_file_path)
        
        logging.info("="*60)
        logging.info(f"[완료] 요약 생성 완료")
        logging.info("="*60)
        
        # 성공 응답
        return JSONResponse(content={
            "summary": result["summary"],
            "original_text": result["original_text"]
        })
    
    except Exception as e:
        error_message = str(e)
        logging.error(f"[오류] {error_message}")
        
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
                logging.info(f"[삭제] 업로드 파일 삭제 완료: {uploaded_file_path}")
            except Exception as e:
                logging.error(f"[오류] 업로드 파일 삭제 실패: {e}")


if __name__ == "__main__":
    # 서버 설정 가져오기
    server_config = config.get('server', {})
    host = server_config.get('host', '0.0.0.0')
    port = server_config.get('port', 8000)
    
    # HTTPS 설정 가져오기
    https_config = config.get('https', {})
    https_enabled = https_config.get('enabled', False)
    
    # 프로토콜 결정
    protocol = "https" if https_enabled else "http"
    
    logging.info("=" * 70)
    logging.info("🚀 음성 텍스트 변환/요약 서비스 시작 (Powered by Gemini 1.5 Flash)")
    logging.info("=" * 70)
    logging.info(f"서버 주소: {protocol}://{host}:{port}")
    logging.info(f"API 문서: {protocol}://{host}:{port}/docs")
    logging.info("지원 형식: mp3, wav, m4a, ogg, flac, aac, wma, webm")
    logging.info("주의: 무료 API 사용으로 하루 1,500회 제한이 있습니다.")
    
    if https_enabled:
        cert_file = https_config.get('cert_file')
        key_file = https_config.get('key_file')
        
        # 인증서 파일 존재 확인
        if not os.path.exists(cert_file):
            logging.error(f"SSL 인증서 파일을 찾을 수 없습니다: {cert_file}")
            logging.error("config/config.yaml에서 올바른 인증서 경로를 설정하거나 HTTPS를 비활성화하세요.")
            sys.exit(1)
        
        if not os.path.exists(key_file):
            logging.error(f"SSL 키 파일을 찾을 수 없습니다: {key_file}")
            logging.error("config/config.yaml에서 올바른 키 파일 경로를 설정하거나 HTTPS를 비활성화하세요.")
            sys.exit(1)
        
        logging.info(f"HTTPS 활성화됨 (인증서: {cert_file})")
        logging.info("=" * 70)
        
        # HTTPS로 서버 시작
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            ssl_keyfile=key_file,
            ssl_certfile=cert_file
        )
    else:
        logging.info("HTTPS 비활성화됨 (HTTP 모드)")
        logging.info("=" * 70)
        
        # HTTP로 서버 시작
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info"
        )
