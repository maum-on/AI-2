from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from .service import stt_and_write_diary

router = APIRouter(
    prefix="/diary",
    tags=["stt_diary"]
)

class STTDiaryResponse(BaseModel):
    transcript: str
    diary: str

@router.post("/stt", response_model=STTDiaryResponse)
async def create_diary(audio: UploadFile = File(...)):
    if not audio.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="Audio file required")

    audio_bytes = await audio.read()
    result = stt_and_write_diary(audio_bytes, audio.filename or "audio.wav")
    return STTDiaryResponse(**result)
