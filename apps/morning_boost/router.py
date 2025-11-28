from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from uuid import uuid4
from pathlib import Path

from .prompt_engine import build_boost_prompt
from .tts_engine import generate_tts_to_file, ping_openai
from .utils import get_data_dir
from .main import fetch_latest_diary   # 기존 코드 그대로 재사용

router = APIRouter(
    prefix="/boost",
    tags=["morning_boost"]
)

@router.get("/health")
def health():
    return {"boost": "ok"}

@router.get("/ping-openai")
def ping():
    return {"ok": ping_openai()}

@router.get("")
def boost(user_id: str = Query(...)):
    diary = fetch_latest_diary(user_id)
    prompt = build_boost_prompt(user_id, diary)

    out_dir = get_data_dir()
    file_name = f"{user_id}_{uuid4().hex}.mp3"
    out_path = out_dir / file_name

    generate_tts_to_file(prompt, out_path)
    return JSONResponse({"audio_file": str(out_path)})
