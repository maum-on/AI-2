# apps/morning_boost/prompt_engine.py
"""
응원 멘트(프롬프트) 생성 모듈.
나중에 '어제 일기'를 받아서 좀 더 맞춤형 문장을 만들도록 확장할 수 있다.
"""

from datetime import date


def build_boost_prompt(user_id: str, diary_text: str | None = None) -> str:
    """
    아침에 들려줄 30초 정도 분량의 응원 멘트 프롬프트를 만든다.
    diary_text 가 없으면 일반적인 응원멘트, 있으면 그 내용을 반영한다.
    """
    today = date.today().strftime("%Y년 %m월 %d일")

    base_instruction = (
        "너는 따뜻하고 긍정적인 한국어 응원 코치야. "
        "듣는 사람이 기운을 낼 수 있도록 30초 정도 분량으로, "
        "말투는 부드럽고 친근하게, 존댓말로 이야기해 줘."
    )

    if not diary_text:
        content = (
            f"오늘은 {today}이고, 사용자의 ID는 {user_id}야. "
            "사용자가 어제 하루를 열심히 보냈다고 생각하고, "
            "오늘 하루도 잘 보낼 수 있도록 격려해 줘. "
            "구체적인 행동 한두 개 정도도 제안해 줘."
        )
    else:
        content = (
            f"오늘은 {today}이고, 사용자의 ID는 {user_id}야. "
            "아래는 사용자가 어제 쓴 일기야.\n"
            f"---\n{diary_text}\n---\n"
            "이 일기를 바탕으로 사용자의 감정을 공감해 주고, "
            "내일을 준비할 수 있도록 짧은 응원 멘트를 만들어 줘."
        )

    return f"{base_instruction}\n\n{content}"
