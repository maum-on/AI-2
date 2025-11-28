# src/api/stt_diary_router.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from stt_diary.src.services.stt_diary_service import stt_and_write_diary

router = APIRouter(
    prefix="/diary/stt",   # POST /diary/stt
    tags=["stt-diary"],
)


class STTDiaryResponse(BaseModel):
    transcript: str
    diary: str


@router.post("", response_model=STTDiaryResponse)
async def create_diary_from_voice(
    audio: UploadFile = File(..., description="녹음한 음성 파일 (wav/mp3/m4a 등)")
):
    # 파일 타입 체크
    if not audio.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="audio 파일을 업로드해주세요.")

    audio_bytes = await audio.read()

    try:
        result = stt_and_write_diary(audio_bytes, filename=audio.filename or "audio.wav")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT/일기 생성 중 오류: {e}")

    return STTDiaryResponse(**result)
