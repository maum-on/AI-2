# apps/morning_boost/router.py

from uuid import uuid4
from typing import List, Optional, Dict, Any
import json

from fastapi import APIRouter, Query, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .prompt_engine import build_boost_prompt
from .tts_engine import generate_tts_to_file, ping_openai
from .utils import get_data_dir
from .main import fetch_latest_diary  # user_id 방식에서 사용


router = APIRouter(
    prefix="/boost",
    tags=["morning_boost"],
)

# ============================
# 감정 매핑 (한글 → 영어 코드)
# ============================

EMOTION_KO_TO_EN: Dict[str, str] = {
    "행복": "happy",
    "기쁨": "happy",
    "즐거움": "happy",

    "슬픔": "sad",
    "우울": "sad",

    "분노": "angry",
    "화남": "angry",
    "화남/분노": "angry",

    "부끄러움": "shy",
    "쑥스러움": "shy",

    "공허": "empty",
    "허무": "empty",
}


def normalize_emotion_for_header(emotion: Optional[str]) -> Optional[str]:
    """
    HTTP 헤더에 넣기 위해 감정 문자열을 정제.
    - 한글 감정은 영어 코드로 매핑
    - 여전히 non-ascii 이면 헤더에 넣지 않음
    """
    if not emotion:
        return None

    emotion_str = str(emotion)
    emotion_en = EMOTION_KO_TO_EN.get(emotion_str, emotion_str)

    # 헤더는 실제로 ascii(latin-1)만 안전하므로 non-ascii면 스킵
    if emotion_en.isascii():
        return emotion_en
    return None


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
    # JSON에 user_id가 없어도 되도록 default=None + extra="ignore"
    user_id: Optional[str] = None
    code: int
    message: str
    data: DiaryData

    class Config:
        extra = "ignore"  # 혹시 다른 필드가 들어와도 무시


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
# 1) user_id로 일기 가져오는 버전
#    ➜ mp3 바이너리 직접 응답
# ============================

@router.get("")
async def boost(
    user_id: str = Query(..., description="사용자 ID"),
):
    """
    1) 백엔드에서 최신 일기/요약 정보 가져오기
    2) 프롬프트 생성
    3) TTS로 mp3 생성
    4) mp3 바이너리 직접 응답 + 메타데이터는 헤더에
    """
    diary_data: Optional[Dict[str, Any]] = fetch_latest_diary(user_id)
    prompt = build_boost_prompt(user_id=user_id, diary=diary_data)

    out_dir = get_data_dir()
    file_name = f"{user_id}_{uuid4().hex}.mp3"
    out_path = out_dir / file_name

    # TTS 생성
    generate_tts_to_file(prompt, out_path)

    emotion = diary_data.get("emotion") if diary_data else None
    emotion_header = normalize_emotion_for_header(emotion)

    # 파일 직접 응답
    resp = FileResponse(
        path=str(out_path),
        media_type="audio/mpeg",
        filename=file_name,
    )

    # 메타데이터를 헤더에 전달
    resp.headers["X-User-Id"] = user_id
    resp.headers["X-Diary-Used"] = "true" if diary_data is not None else "false"
    if emotion_header:
        resp.headers["X-Emotion"] = emotion_header

    return resp


# ============================
# 2) JSON Body로 직접 보내는 버전
#    ➜ mp3 바이너리 직접 응답
# ============================

@router.post("/from-json")
async def boost_from_json(req: BoostRequest):
    """
    클라이언트/백엔드에서 만든 일기 요약 JSON을 Body로 직접 보내는 버전.
    mp3 바이너리를 그대로 응답하고,
    감정 정보 등은 헤더에 담아준다.
    """
    user_id = req.user_id or "anonymous"
    diary = req.data.model_dump()

    prompt = build_boost_prompt(user_id=user_id, diary=diary)

    out_dir = get_data_dir()
    file_name = f"{user_id}_{uuid4().hex}.mp3"
    out_path = out_dir / file_name

    generate_tts_to_file(prompt, out_path)

    emotion = diary.get("emotion")
    emotion_header = normalize_emotion_for_header(emotion)

    resp = FileResponse(
        path=str(out_path),
        media_type="audio/mpeg",
        filename=file_name,
    )

    resp.headers["X-User-Id"] = user_id
    resp.headers["X-Diary-Used"] = "true"
    if emotion_header:
        resp.headers["X-Emotion"] = emotion_header

    return resp


# ============================
# 3) JSON 파일 업로드 버전
#    ➜ mp3 바이너리 직접 응답
# ============================

@router.post("/from-json-file")
async def boost_from_json_file(file: UploadFile = File(..., description="일기 요약 JSON 파일")):
    """
    JSON 파일(.json)을 업로드해서 처리하는 버전.
    mp3 바이너리를 바로 응답하고, 메타데이터는 헤더에 담는다.
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

    prompt = build_boost_prompt(user_id=user_id, diary=diary)

    out_dir = get_data_dir()
    file_name = f"{user_id}_{uuid4().hex}.mp3"
    out_path = out_dir / file_name

    generate_tts_to_file(prompt, out_path)

    emotion = diary.get("emotion")
    emotion_header = normalize_emotion_for_header(emotion)

    resp = FileResponse(
        path=str(out_path),
        media_type="audio/mpeg",
        filename=file_name,
    )

    resp.headers["X-User-Id"] = user_id
    resp.headers["X-Diary-Used"] = "true"
    resp.headers["X-Uploaded-Filename"] = file.filename or ""
    if emotion_header:
        resp.headers["X-Emotion"] = emotion_header

    return resp
