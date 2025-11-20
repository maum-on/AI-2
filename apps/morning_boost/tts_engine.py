import os
from pathlib import Path
from typing import Optional
import traceback

from dotenv import load_dotenv
from openai import OpenAI

# .env 파일 로드
BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini-tts")
OPENAI_VOICE = os.getenv("TTS_VOICE", "alloy")

client = OpenAI(api_key=OPENAI_API_KEY)


def ensure_output_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def generate_tts_to_file(
    text: str,
    output_path: Path,
    format: str = "mp3",
) -> Path:

    ensure_output_dir(output_path)

    with client.audio.speech.with_streaming_response.create(
        model=OPENAI_MODEL,
        voice=OPENAI_VOICE,
        input=text,
        response_format=format,   # ← 최신 SDK에서 필수
    ) as resp:
        resp.stream_to_file(output_path)

    return output_path


def ping_openai() -> bool:
    tmp_path = Path("tmp_ping_tts.mp3")
    try:
        generate_tts_to_file("테스트입니다.", tmp_path)
        tmp_path.unlink(missing_ok=True)
        return True
    except Exception as e:
        print("[PING ERROR]", repr(e))
        traceback.print_exc()
        return False
