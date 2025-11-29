# main.py

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 라우터 import
from apps.morning_boost.router import router as boost_router
from stt_diary.src.api.stt_diary_router import router as stt_diary_router

app = FastAPI(
    title="Maum-on Unified API",
)

# ============================
# 🔥 CORS 설정
# ============================

# 개발 단계: 모든 도메인 허용
# 운영 단계: 실제 백엔드/프론트 주소만 남겨도 됨
origins = [
    "*",
    # "http://13.209.35.235",
    # "http://13.209.35.235:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================
# 🔥 라우터 등록
# ============================

# morning_boost 기능
app.include_router(boost_router)

# stt_diary 기능
app.include_router(stt_diary_router)

# ============================
# 🔥 헬스 체크
# ============================
@app.get("/health")
def health():
    return {"status": "ok"}
