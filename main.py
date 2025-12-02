from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from apps.morning_boost.router import router as boost_router
from stt_diary.src.api.stt_diary_router import router as stt_router

# ===== 기반 경로 설정 =====
BASE_DIR = Path(__file__).resolve().parent

# data/morning_boost 폴더 (없으면 생성)
MORNING_BOOST_DIR = BASE_DIR / "data" / "morning_boost"
MORNING_BOOST_DIR.mkdir(parents=True, exist_ok=True)

# ===== FastAPI 앱 생성 =====
app = FastAPI(title="Maum-on Unified API")

# 라우터 등록
app.include_router(boost_router)
app.include_router(stt_router)

# ===== 정적 파일 서빙 =====
# /static/morning_boost/파일명.mp3 로 접근 가능
app.mount(
    "/static/morning_boost",
    StaticFiles(directory=str(MORNING_BOOST_DIR)),
    name="morning_boost_static",
)

# 헬스체크 엔드포인트
@app.get("/health")
async def health():
    return {"status": "ok"}