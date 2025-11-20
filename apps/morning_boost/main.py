"""
morning_boost FastAPI 앱 엔트리 포인트.

엔드포인트:
- GET /health        : 서버 상태 체크
- GET /ping-openai   : OpenAI TTS 호출 여부 체크
- GET /boost         : 최신 일기 기반 응원 멘트 TTS 생성
"""

import os
from uuid import uuid4
from pathlib import Path
from typing import Optional

import httpx
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

from apps.morning_boost.prompt_engine import build_boost_prompt
from apps.morning_boost.tts_engine import generate_tts_to_file, ping_openai
from apps.morning_boost.utils import get_data_dir, load_config

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")


def fetch_latest_diary(user_id: str) -> Optional[str]:
    """
    백엔드(Spring Boot)의 최신 일기 조회 API 호출.
    기대 응답 형식:
    {
      "code": 200,
      "message": "일기 조회 성공",
      "data": {
        "write_diary": "..."
      }
    }
    """
    try:
        resp = httpx.get(
            f"{BACKEND_URL}/api/diary/latest",
            params={"user_id": user_id},
            timeout=5,
        )
        if resp.status_code != 200:
            print("[fetch_latest_diary] status_code:", resp.status_code)
            return None

        body = resp.json()
        if body.get("code") != 200:
            print("[fetch_latest_diary] response code:", body.get("code"))
            return None

        return body.get("data", {}).get("write_diary")
    except Exception as e:
        print("[fetch_latest_diary ERROR]", repr(e))
        return None


def create_app() -> FastAPI:
    app = FastAPI(title="morning_boost")

    cfg = load_config()  # 지금은 안 쓰지만 나중에 시간/옵션 config 용

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.get("/ping-openai")
    async def ping():
        ok = ping_openai()
        return {"ok": ok}

    @app.get("/boost")
    async def boost(
        user_id: str = Query(..., description="사용자 ID"),
    ):
        """
        1) 백엔드에서 최신 일기 가져오기
        2) 일기 기반 프롬프트 생성
        3) TTS 로 mp3 생성
        """
        diary_text = fetch_latest_diary(user_id)
        prompt = build_boost_prompt(user_id=user_id, diary_text=diary_text)

        out_dir = get_data_dir()
        file_name = f"{user_id}_{uuid4().hex}.mp3"
        out_path = out_dir / file_name

        generate_tts_to_file(prompt, out_path)

        return JSONResponse(
            {
                "status": "ok",
                "user_id": user_id,
                "diary_used": diary_text is not None,
                "audio_path": str(out_path),
            }
        )

    return app


# python으로 직접 실행할 때
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "apps.morning_boost.main:create_app",
        host="0.0.0.0",
        port=8010,
        reload=True,
        factory=True,
    )
