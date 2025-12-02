from fastapi import FastAPI

from apps.morning_boost.router import router as boost_router
from stt_diary.src.api.stt_diary_router import router as stt_router
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Maum-on Unified API")

app.include_router(boost_router)
app.include_router(stt_router)

# data/morning_boost 폴더를 /static/morning_boost URL로 접근 가능하게 해줌
app.mount(
    "/static/morning_boost",
    StaticFiles(directory="apps/data/morning_boost"),
    name="morning_boost_static"
)

@app.get("/health")
def health():
    return {"status": "ok"}
