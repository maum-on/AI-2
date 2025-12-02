from fastapi import FastAPI

from apps.morning_boost.router import router as boost_router
from stt_diary.src.api.stt_diary_router import router as stt_router

app = FastAPI(title="Maum-on Unified API")

app.include_router(boost_router)
app.include_router(stt_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
