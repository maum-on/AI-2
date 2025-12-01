"""
morning_boost FastAPI 앱 엔트리 포인트.

엔드포인트:
- GET /health        : 서버 상태 체크
- GET /ping-openai   : OpenAI TTS 호출 여부 체크
- GET /boost         : 최신 일기 기반 응원 멘트 TTS 생성
"""

import os
from uuid import uuid4
from typing import Optional, Dict, Any

import httpx
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles  # ★ 정적 파일 서빙용

from apps.morning_boost.prompt_engine import build_boost_prompt
from apps.morning_boost.tts_engine import generate_tts_to_file, ping_openai
from apps.morning_boost.utils import get_data_dir, load_config

BACKEND_URL = os.getenv("BACKEND_URL", "http://13.209.35.235:8080")


def fetch_latest_diary(user_id: str) -> Optional[Dict[str, Any]]:
    """
    백엔드(Spring Boot)의 최신 일기 조회 API 호출.

    기대 응답 형식 (예시):
    {
        "code": 200,
        "message": "9월 16일 정보 조회 성공",
        "data": {
            "emotion": "happy",
            "draw": "그림 url",
            "write_diary": "오늘의 일기를 작성했습니다. 오늘은 이런 저런 일을 했습니다.",
            "file_summation": [
                "느좋 카페 방문",
                "페스티벌 관람",
                "성적 A+"
            ],
            "ai_reply": "대충 ai 답장",
            "ai_draw_reply": "그림 일기 ai 답장"
        }
    }

    :return:
        - 성공 시: data 블록(dict)을 그대로 반환
        - 실패 시: None
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

        data = body.get("data") or {}
        # file_summation이 null/undefined일 수도 있으니 안전하게 처리
        if data.get("file_summation") is None:
            data["file_summation"] = []

        return data

    except Exception as e:
        print("[fetch_latest_diary ERROR]", repr(e))
        return None


def create_app() -> FastAPI:
    app = FastAPI(title="morning_boost")

    cfg = load_config()  # 지금은 안 쓰지만 나중에 시간/옵션 config 용

    # ==============================
    # 🔹 정적 파일 서빙 설정
    # /app/data/morning_boost 에 저장되는 mp3를
    # /static/morning_boost/파일명.mp3 로 외부에서 접근 가능하게 만든다.
    # ==============================
    audio_dir = get_data_dir()  # 예: /app/data/morning_boost
    app.mount(
        "/static/morning_boost",
        StaticFiles(directory=str(audio_dir)),
        name="morning_boost_static",
    )

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
        1) 백엔드에서 최신 일기/요약 정보 가져오기
        2) 해당 정보를 기반으로 프롬프트 생성
        3) TTS 로 mp3 생성
        """
        diary_data = fetch_latest_diary(user_id)

        prompt = build_boost_prompt(
            user_id=user_id,
            diary=diary_data,  # None 일 수도 있음
        )

        out_dir = get_data_dir()
        file_name = f"{user_id}_{uuid4().hex}.mp3"
        out_path = out_dir / file_name

        generate_tts_to_file(prompt, out_path)

        # 정적 파일 URL (/static/morning_boost/파일명.mp3)
        audio_url = f"/static/morning_boost/{file_name}"

        return JSONResponse(
            {
                "version": "mb-v2",
                "status": "ok",
                "user_id": user_id,
                "diary_used": diary_data is not None,
                # 프론트/백엔드는 이 URL을 서버 주소랑 합쳐서 쓰면 됨
                # 예: http://15.134.86.188:8080/static/morning_boost/...
                "audio_url": audio_url,
                # 내부 디버깅용(원하면 제거 가능)
                "audio_path": str(out_path),
                "diary_meta": {
                    "has_diary": diary_data is not None,
                    "emotion": diary_data.get("emotion") if diary_data else None,
                },
            }
        )

    return app


# python으로 직접 실행할 때
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "apps.morning_boost.main:create_app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        factory=True,
    )
