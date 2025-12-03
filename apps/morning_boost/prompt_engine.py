# apps/morning_boost/prompt_engine.py
"""
응원 멘트(프롬프트) 생성 + 최종 멘트 생성 모듈.
백엔드에서 받아온 diary 데이터 전체를 바탕으로 맞춤형 멘트를 생성한다.
"""

from datetime import date
from typing import Optional, Dict, Any

from openai import OpenAI

client = OpenAI()


def build_boost_prompt(
    user_id: str,  # 기존 인터페이스 유지를 위해 남겨두지만 프롬프트에서는 사용하지 않는다.
    diary: Optional[Dict[str, Any]] = None
) -> str:
    """
    아침에 들려줄 30초 분량의 응원멘트 생성을 위한 "프롬프트" 텍스트를 만든다.
    이 텍스트는 LLM에 그대로 input으로 들어간다.

    ⚠️ 규칙:
    - 사용자 이름, 닉네임, ID를 부르지 않는다.
    - 'OO님', '사용자님', '~님' 등의 호칭도 사용하지 않는다.
    """

    today = date.today().strftime("%Y년 %m월 %d일")

    # 기본 톤 (고정)
    base_instruction = (
        "너는 따뜻하고 긍정적인 한국어 아침 응원 코치야. "
        "듣는 사람이 기운을 낼 수 있도록 30초 정도 분량으로, "
        "말투는 부드럽고 친근하게, 존댓말로 이야기해 줘. "
        "절대 사용자 이름이나 닉네임, ID를 말하지 말고, "
        "'OO님', '사용자님', '~님' 같은 호칭도 사용하지 마. "
        "상대를 특정하지 않고 자연스럽게 말을 건네듯 이야기해."
    )

    # -------------------------------
    # 1) 일기가 없을 때 (기본 멘트)
    # -------------------------------
    if diary is None:
        content = (
            f"오늘은 {today}이야.\n"
            "전날 일기가 없지만, 어제 하루를 나름대로 열심히 보냈을 거라고 생각하고 "
            "오늘도 차분히 시작할 수 있도록 아침 응원 멘트를 만들어줘.\n"
            "- 가볍게 웃을 수 있는 문장 1개 포함\n"
            "- 오늘 바로 실천해볼 수 있는 현실적인 행동 팁 1~2개 포함\n"
            "- 특정 이름이나 호칭 없이 일반적인 형태로 말해줘\n"
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
        f"오늘은 {today}이야.\n"
        "아래는 어제 사용자가 남긴 일기와 백엔드가 제공한 요약 정보야.\n\n"

        "【감정 분석 결과】\n"
        f"- 감정 상태: {emotion}\n\n"

        "【일기 내용】\n"
        f"{write_diary}\n\n"

        "【파일 기반 요약 키워드】\n"
        f"{keywords_str}\n\n"

        "【어제 AI가 남긴 답장】\n"
        f"{ai_reply}\n\n"

        "위 정보를 모두 참고해서,\n"
        "- 어제의 감정을 먼저 공감해 주고,\n"
        "- 오늘 하루를 가볍고 따뜻하게 시작할 수 있도록 응원해 주고,\n"
        "- 말했을 때 약 30초 분량,\n"
        "- 라디오 DJ처럼 자연스럽고 부드럽게 존댓말로 이야기하고,\n"
        "- 부담스럽지 않고 현실적인 행동 팁 1~2개를 포함해 줘.\n"
        "- 절대 사용자 이름, 닉네임, ID, '~님', '사용자님' 등 호칭을 사용하지 말고,\n"
        "  특정 사람을 지칭하지 않는 자연스러운 응원 멘트로 작성해 줘.\n"
    )

    return f"{base_instruction}\n\n{content}"


def build_boost_message(
    user_id: str,
    diary: Optional[Dict[str, Any]] = None,
    model: str = "gpt-4o-mini",
) -> str:
    """
    위에서 만든 프롬프트를 실제 LLM에 던져서
    '최종으로 읽을 한 편의 응원 멘트 텍스트'를 생성한다.
    이 반환값을 그대로 TTS에 넣는다.
    """
    prompt = build_boost_prompt(user_id=user_id, diary=diary)

    # responses API 사용
    response = client.responses.create(
        model=model,
        input=prompt,
    )

    # 최신 SDK에서 제공하는 편의 프로퍼티
    text = response.output_text
    return text.strip()
