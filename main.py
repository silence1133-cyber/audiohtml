import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai
from pydub import AudioSegment

# 환경변수 로드
load_dotenv()

# Gemini API 설정
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("GOOGLE_API_KEY가 .env 파일에 설정되지 않았습니다.")

genai.configure(api_key=api_key)


def convert_audio_to_lightweight_mp3(input_file_path: str) -> str:
    """
    다양한 형식의 오디오 파일을 경량 MP3로 변환합니다.
    비용 절감을 위해 32kbps 비트레이트를 사용합니다.
    
    Args:
        input_file_path: 입력 오디오 파일 경로
    
    Returns:
        변환된 MP3 파일 경로 (임시 파일)
    """
    print(f"오디오 변환 시작: {input_file_path}")
    
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
        print(f"오디오 변환 완료: {output_file_path} ({file_size:.2f}MB)")
        return output_file_path
    
    except Exception as e:
        # 변환 실패 시 임시 파일 삭제
        if os.path.exists(output_file_path):
            os.remove(output_file_path)
        print(f"오디오 변환 중 오류 발생: {e}")
        raise


def upload_audio_to_gemini(audio_file_path: str) -> any:
    """
    오디오 파일을 Gemini에 업로드합니다.
    
    Args:
        audio_file_path: 업로드할 오디오 파일 경로
    
    Returns:
        업로드된 파일 객체
    """
    print(f"Gemini에 파일 업로드 중...")
    
    try:
        uploaded_file = genai.upload_file(audio_file_path)
        print(f"파일 업로드 완료: {uploaded_file.name}")
        return uploaded_file
    
    except Exception as e:
        # API 할당량 초과 에러 처리
        error_message = str(e).lower()
        if 'quota' in error_message or 'limit' in error_message or '429' in error_message:
            raise Exception("일일 사용량이 초과되었습니다. 내일 다시 시도해주세요.")
        print(f"파일 업로드 중 오류 발생: {e}")
        raise


def summarize_audio_with_gemini(uploaded_file: any) -> str:
    """
    Gemini 1.5 Flash 무료 모델을 사용하여 오디오 내용을 요약합니다.
    
    Args:
        uploaded_file: Gemini에 업로드된 파일 객체
    
    Returns:
        요약된 텍스트
    """
    print("Gemini 1.5 Flash로 회의록 요약 생성 중...")
    
    try:
        # Gemini 1.5 Flash 무료 모델 사용
        # Gemini 1.5 Flash Latest 모델 사용 (최신 API 버전)
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        # 프롬프트 작성
        prompt = "이 회의 녹음 파일을 분석해서, 주요 안건, 결정 사항, 향후 행동 계획(Action Item)으로 요약해줘."
        
        # 요약 생성
        response = model.generate_content([prompt, uploaded_file])
        
        print("요약 생성 완료!")
        return response.text
    
    except Exception as e:
        # API 할당량 초과 에러 처리
        error_message = str(e).lower()
        if 'quota' in error_message or 'limit' in error_message or '429' in error_message:
            raise Exception("일일 사용량이 초과되었습니다. 내일 다시 시도해주세요.")
        print(f"요약 생성 중 오류 발생: {e}")
        raise


def process_audio_file(input_file_path: str) -> str:
    """
    오디오 파일을 처리하여 회의록 요약을 생성합니다.
    처리가 완료되면 변환된 파일을 자동으로 삭제합니다 (개인정보 보호).
    
    Args:
        input_file_path: 입력 오디오 파일 경로
    
    Returns:
        회의록 요약 텍스트
    """
    mp3_file_path = None
    
    try:
        # 1. 오디오 파일을 경량 MP3로 변환
        mp3_file_path = convert_audio_to_lightweight_mp3(input_file_path)
        
        # 2. Gemini에 파일 업로드
        uploaded_file = upload_audio_to_gemini(mp3_file_path)
        
        # 3. Gemini로 요약 생성
        summary = summarize_audio_with_gemini(uploaded_file)
        
        return summary
    
    except Exception as e:
        print(f"\n처리 중 오류 발생: {e}")
        raise
    
    finally:
        # 처리 완료 후 변환된 MP3 파일 삭제 (개인정보 보호)
        if mp3_file_path and os.path.exists(mp3_file_path):
            try:
                os.remove(mp3_file_path)
                print(f"임시 파일 삭제 완료: {mp3_file_path}")
            except Exception as e:
                print(f"임시 파일 삭제 실패: {e}")


def main():
    """
    메인 함수
    """
    print("=" * 70)
    print("AI 회의록 요약 서비스 (Powered by Gemini 1.5 Flash)")
    print("=" * 70)
    print("지원 형식: m4a, wav, mp3, ogg, flac 등")
    print("주의: 무료 API 사용으로 하루 1,500회 제한이 있습니다.")
    print("=" * 70)
    
    # 오디오 파일 경로 입력 받기
    audio_file = input("\n오디오 파일 경로를 입력하세요: ").strip()
    
    # 파일 존재 여부 확인
    if not os.path.exists(audio_file):
        print(f"\n❌ 오류: 파일을 찾을 수 없습니다 - {audio_file}")
        return
    
    # 파일 크기 확인
    file_size = os.path.getsize(audio_file) / (1024 * 1024)  # MB
    print(f"\n📁 원본 파일 크기: {file_size:.2f}MB")
    print("\n⏳ 처리 시작...\n")
    
    try:
        # 오디오 처리 및 요약 생성
        summary = process_audio_file(audio_file)
        
        # 결과 출력
        print("\n" + "=" * 70)
        print("📝 회의록 요약 결과")
        print("=" * 70)
        print(summary)
        print("=" * 70)
        
        # 결과를 파일로 저장
        output_file = Path(audio_file).with_suffix('.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"\n✅ 요약본이 저장되었습니다: {output_file}")
        print("✅ 처리가 완료되었습니다. 업로드된 파일은 자동으로 삭제되었습니다.")
    
    except Exception as e:
        print(f"\n❌ 오류: {e}")
        print("\n💡 문제가 지속되면 다음을 확인해주세요:")
        print("   1. .env 파일에 GOOGLE_API_KEY가 올바르게 설정되어 있는지")
        print("   2. ffmpeg가 시스템에 설치되어 있는지")
        print("   3. 일일 사용량 제한(1,500회)에 도달하지 않았는지")


if __name__ == "__main__":
    main()
