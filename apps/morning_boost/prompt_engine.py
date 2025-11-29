# apps/morning_boost/prompt_engine.py
"""
응원 멘트(프롬프트) 생성 모듈.
백엔드에서 받아온 diary 데이터 전체를 바탕으로 맞춤형 멘트를 생성한다.
"""

from datetime import date
from typing import Optional, Dict, Any


def build_boost_prompt(
    user_id: str,
    diary: Optional[Dict[str, Any]] = None
) -> str:
    """
    아침에 들려줄 30초 분량의 응원멘트 생성 프롬프트.

    diary 예시 구조:
    {
        "emotion": "happy",
        "draw": "some-url",
        "write_diary": "...",
        "file_summation": ["카페 방문", "페스티벌 관람"],
        "ai_reply": "어제 남긴 AI 답장",
        "ai_draw_reply": "그림일기 답장"
    }

    diary가 None이면: 일반 응원 멘트 생성
    diary가 있으면: 요약키워드 / 감정 / 일기내용 / 기존 AI 답장을 모두 참고한 맞춤형 멘트 생성
    """

    today = date.today().strftime("%Y년 %m월 %d일")

    # 기본 톤 (고정)
    base_instruction = (
        "너는 따뜻하고 긍정적인 한국어 아침 응원 코치야. "
        "듣는 사람이 기운을 낼 수 있도록 30초 정도 분량으로, "
        "말투는 부드럽고 친근하게, 존댓말로 이야기해 줘."
    )

    # -------------------------------
    # 1) 일기가 없을 때 (기본 멘트)
    # -------------------------------
    if diary is None:
        content = (
            f"오늘은 {today}이고, 사용자 ID는 {user_id}야.\n"
            "전날 일기가 없지만, 사용자가 어제 하루를 열심히 보냈을 거라고 생각하고 "
            "오늘도 차분히 시작할 수 있도록 응원 멘트를 만들어줘.\n"
            "- 가볍게 웃을 수 있는 문장 1개 포함\n"
            "- 오늘 실천할 수 있는 행동 팁 1~2개\n"
        )
        return f"{base_instruction}\n\n{content}"

    # -------------------------------
    # 2) 일기가 있을 때 (맞춤형 멘트)
    # -------------------------------
    write_diary = diary.get("write_diary", "")
    emotion = diary.get("emotion")
    ai_reply = diary.get("ai_reply")
    file_summation = diary.get("file_summation") or []

    # 키워드(파일 요약) 연결
    keywords_str = ", ".join(file_summation) if file_summation else "키워드 없음"

    content = (
        f"오늘은 {today}이고, 사용자 ID는 {user_id}야.\n"
        "아래는 사용자가 어제 남긴 일기와 백엔드가 제공한 요약 정보야.\n\n"

        "【감정 분석 결과】\n"
        f"- 감정 상태: {emotion}\n\n"

        "【일기 내용】\n"
        f"{write_diary}\n\n"

        "【파일 기반 요약 키워드】\n"
        f"{keywords_str}\n\n"

        "【어제 AI가 남긴 답장】\n"
        f"{ai_reply}\n\n"

        "위 정보를 모두 참고해서,\n"
        "- 어제의 감정을 공감해 주고,\n"
        "- 오늘 하루를 가볍고 따뜻하게 시작할 수 있도록 응원해 주고,\n"
        "- 말했을 때 약 30초 분량,\n"
        "- 존댓말 + 라디오 DJ처럼 자연스럽고 부드럽게,\n"
        "- 부담스럽지 않고 현실적인 행동 팁 1~2개 포함,\n"
        "이런 조건을 모두 만족하는 한국어 아침 응원 멘트를 만들어줘."
    )

    return f"{base_instruction}\n\n{content}"
