"""
morning_boost 패키지 엔트리 포인트.
uvicorn 에서 `apps.morning_boost:app` 으로 쓸 수 있게 해 둔다.
"""

from .main import create_app

app = create_app()
