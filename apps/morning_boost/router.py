# apps/morning_boost/router.py

from uuid import uuid4
from typing import List, Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .prompt_engine import build_boost_prompt
from .tts_engine import generate_tts_to_file, ping_openai
from .utils import get_data_dir

router = APIRouter(
    prefix="/boost",
    tags=["morning_boost"],
)

# ---------- Pydantic 모델 ----------

class DiaryData(BaseModel):
    emotion: Optional[str] = None
    draw: Optional[str] = None
    write_diary: str
    file_summation: List[str] = []
    ai_reply: Optional[str] = None
    ai_draw_reply: Optional[str] = None

class BoostRequest(BaseModel):
    user_id: Optional[str] = None
    code: int
    message: str
    data: DiaryData


# ---------- 기존 건강 체크 ----------

@router.get("/health")
async def health():
    return {"boost": "ok"}

@router.get("/ping-openai")
async def ping():
    return {"ok": ping_openai()}


# ---------- 네가 원하는 JSON body 버전 ----------

@router.post("/from-json")
async def boost_from_json(req: BoostRequest):
    """
    1) 클라이언트/백엔드에서 이미 만든 일기 요약 JSON을 그대로 받는다.
    2) 해당 정보를 기반으로 프롬프트 생성
    3) TTS로 mp3 생성 후 경로와 메타데이터 반환
    """
    user_id = req.user_id or "anonymous"
    diary = req.data.model_dump()  # dict로 변환

    prompt = build_boost_prompt(
        user_id=user_id,
        diary=diary,
    )

    out_dir = get_data_dir()
    file_name = f"{user_id}_{uuid4().hex}.mp3"
    out_path = out_dir / file_name

    generate_tts_to_file(prompt, out_path)

    return JSONResponse(
        {
            "version": "mb-v2-json",
            "status": "ok",
            "user_id": user_id,
            "diary_used": True,
            "audio_path": str(out_path),
            "diary_meta": {
                "has_diary": True,
                "emotion": diary.get("emotion"),
            },
        }
    )
