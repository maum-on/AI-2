# main.py
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from src.api.stt_diary_router import router as stt_diary_router

app = FastAPI(
    title="Maum-on STT Diary API",
)

# 라우터 등록
app.include_router(stt_diary_router)


@app.get("/health")
def health():
    return {"status": "ok"}
