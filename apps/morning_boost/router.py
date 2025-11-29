from uuid import uuid4
from typing import Optional, Dict, Any

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from .prompt_engine import build_boost_prompt
from .tts_engine import generate_tts_to_file, ping_openai
from .utils import get_data_dir
from .main import fetch_latest_diary  # 기존 함수 재사용

router = APIRouter(
    prefix="/boost",
    tags=["morning_boost"],
)


@router.get("/health")
async def health():
    return {"boost": "ok"}


@router.get("/ping-openai")
async def ping():
    return {"ok": ping_openai()}


@router.get("")
async def boost(
    user_id: str = Query(..., description="사용자 ID"),
):
    """
    1) 백엔드에서 최신 일기/요약 정보 가져오기
    2) 해당 정보를 기반으로 프롬프트 생성
    3) TTS로 mp3 생성 후 경로와 메타데이터 반환
    """
    # fetch_latest_diary는 백엔드 JSON에서 body["data"]만 꺼내서 반환하도록 구현되어 있다고 가정
    diary_data: Optional[Dict[str, Any]] = fetch_latest_diary(user_id)

    # 프롬프트 생성 (일기 없으면 diary_data가 None)
    prompt = build_boost_prompt(
        user_id=user_id,
        diary=diary_data,
    )

    # 출력 파일 경로 생성
    out_dir = get_data_dir()
    file_name = f"{user_id}_{uuid4().hex}.mp3"
    out_path = out_dir / file_name

    # TTS 실행
    generate_tts_to_file(prompt, out_path)

    # 새 응답 포맷
    return JSONResponse(
        {
            "version": "mb-v2",
            "status": "ok",
            "user_id": user_id,
            "diary_used": diary_data is not None,
            "audio_path": str(out_path),
            "diary_meta": {
                "has_diary": diary_data is not None,
                "emotion": diary_data.get("emotion") if diary_data else None,
            },
        }
    )
