# apps/morning_boost/router.py

from uuid import uuid4
from typing import List, Optional, Dict, Any

import json
from fastapi import APIRouter, Query, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .prompt_engine import build_boost_prompt
from .tts_engine import generate_tts_to_file, ping_openai
from .utils import get_data_dir
from .main import fetch_latest_diary  # user_id 방식에서 사용
from .s3_client import upload_audio_to_s3  # ★ 추가


router = APIRouter(
    prefix="/boost",
    tags=["morning_boost"],
)

# ============================
# Pydantic 모델 (JSON 검증용)
# ============================

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


# ============================
# Health / Ping
# ============================

@router.get("/health")
async def health():
    return {"boost": "ok"}


@router.get("/ping-openai")
async def ping():
    return {"ok": ping_openai()}


# ============================
# 1) 기존: user_id 로 백엔드에서 일기 가져오는 버전
# ============================

@router.get("")
async def boost(
    user_id: str = Query(..., description="사용자 ID"),
):
    """
    1) 백엔드에서 최신 일기/요약 정보 가져오기
    2) 해당 정보를 기반으로 프롬프트 생성
    3) TTS로 mp3 생성 후 S3 업로드
    """
    diary_data: Optional[Dict[str, Any]] = fetch_latest_diary(user_id)
    prompt = build_boost_prompt(user_id=user_id, diary=diary_data)

    out_dir = get_data_dir()
    file_name = f"{user_id}_{uuid4().hex}.mp3"
    out_path = out_dir / file_name

    # 1) 로컬에 TTS 생성
    generate_tts_to_file(prompt, out_path)

    # 2) S3로 업로드 → 외부에서 접근 가능한 URL 받기
    audio_url = upload_audio_to_s3(out_path, user_id=user_id)

    # (선택) 로컬 파일 삭제하고 싶으면 아래 주석 해제
    # try:
    #     out_path.unlink()
    # except OSError:
    #     pass

    return JSONResponse(
        {
            "version": "mb-v2",
            "status": "ok",
            "user_id": user_id,
            "diary_used": diary_data is not None,
            "audio_url": audio_url,          # 🔹 프론트/백은 이 URL로 재생
            "diary_meta": {
                "has_diary": diary_data is not None,
                "emotion": diary_data.get("emotion") if diary_data else None,
            },
        }
    )


# ============================
# 2) JSON Body로 직접 보내는 버전
# ============================

@router.post("/from-json")
async def boost_from_json(req: BoostRequest):
    """
    클라이언트/백엔드에서 이미 만든 일기 요약 JSON을 Body로 직접 보내는 버전.
    """
    user_id = req.user_id or "anonymous"
    diary = req.data.model_dump()

    prompt = build_boost_prompt(user_id=user_id, diary=diary)

    out_dir = get_data_dir()
    file_name = f"{user_id}_{uuid4().hex}.mp3"
    out_path = out_dir / file_name

    generate_tts_to_file(prompt, out_path)
    audio_url = upload_audio_to_s3(out_path, user_id=user_id)

    return JSONResponse(
        {
            "version": "mb-v2-json",
            "status": "ok",
            "user_id": user_id,
            "diary_used": True,
            "audio_url": audio_url,
            "diary_meta": {
                "has_diary": True,
                "emotion": diary.get("emotion"),
            },
        }
    )


# ============================
# 3) JSON 파일 업로드 버전
# ============================

@router.post("/from-json-file")
async def boost_from_json_file(file: UploadFile = File(..., description="일기 요약 JSON 파일")):
    """
    JSON 파일(.json)을 업로드해서 처리하는 버전.
    """
    # 1) 파일 타입 기본 체크
    if file.content_type not in ("application/json", "text/json", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="JSON 파일을 업로드해주세요.")

    # 2) 파일 내용 읽기
    raw_bytes = await file.read()
    try:
        payload = json.loads(raw_bytes.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="JSON 파싱에 실패했습니다.")

    # 3) Pydantic으로 검증
    try:
        req = BoostRequest(**payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"요청 JSON 형식이 올바르지 않습니다: {e}")

    user_id = req.user_id or "anonymous"
    diary = req.data.model_dump()

    # 4) 프롬프트 생성 + TTS
    prompt = build_boost_prompt(user_id=user_id, diary=diary)

    out_dir = get_data_dir()
    file_name = f"{user_id}_{uuid4().hex}.mp3"
    out_path = out_dir / file_name

    generate_tts_to_file(prompt, out_path)
    audio_url = upload_audio_to_s3(out_path, user_id=user_id)

    # 5) 응답
    return JSONResponse(
        {
            "version": "mb-v2-json-file",
            "status": "ok",
            "user_id": user_id,
            "diary_used": True,
            "audio_url": audio_url,
            "diary_meta": {
                "has_diary": True,
                "emotion": diary.get("emotion"),
            },
            "uploaded_filename": file.filename,
        }
    )
