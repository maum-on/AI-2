# src/services/stt_diary_service.py
import io
from typing import Dict

from stt_diary.src.core.openai_client import client


def stt_and_write_diary(audio_bytes: bytes, filename: str = "audio.wav") -> Dict[str, str]:
    """
    1) 음성을 텍스트로 변환(STT)
    2) 그 텍스트를 바탕으로 GPT가 자연스러운 일기 작성
    """

    # 1. STT (Whisper / gpt-4o-mini-transcribe)
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = filename  # openai 라이브러리에서 필요로 함

    stt_res = client.audio.transcriptions.create(
        model="gpt-4o-mini-transcribe",  # 또는 "whisper-1"
        file=audio_file,
        # language="ko",  # 한국어 고정하고 싶으면 주석 해제
    )
    transcript = stt_res.text  # 사용자가 말한 내용

    # 2. 일기 생성
    system_prompt = (
        "너는 한국어 일기 작성 도우미야. "
        "사용자가 말한 내용을 자연스럽고 정돈된 한 편의 일기로 정리해줘. "
        "1인칭 시점, 오늘 하루를 돌아보는 느낌으로, 과한 꾸밈말은 피하고 일상적인 말투로 써줘."
    )

    user_prompt = (
        "다음은 사용자가 음성으로 말한 내용을 문자로 옮긴 결과야.\n"
        "이 내용을 바탕으로 자연스러운 한국어 일기를 한 편 써줘.\n\n"
        f"[음성 인식 결과]\n{transcript}"
    )

    resp = client.responses.create(
        model="gpt-4.1-mini",   # 너가 쓰는 기본 모델로 바꿔도 됨
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    diary_text = resp.output[0].content[0].text

    return {
        "transcript": transcript,
        "diary": diary_text,
    }
