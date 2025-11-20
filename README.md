# 🌞 Morning Boost — AI 아침 응원 멘트 생성기

AI 기반 아침 응원 멘트 자동 생성 서비스
전날 사용자의 일기 내용을 읽고, 아침마다 밝고 경쾌한 톤으로 하루를 응원하는 멘트를 만들어줍니다.

## 🚀 주요 기능

### 기능	설명

| 기능                | 설명                                              |
| ----------------- | ----------------------------------------------- |
| `/boost`          | 전날 일기를 기반으로 아침 응원 멘트 생성<br>→ TTS 음성(mp3) 파일로 저장 |
| `/boost?dryrun=1` | 텍스트 멘트만 미리보기                                    |
| `/health`         | 서버 상태 및 모델 정보 확인                                |
| `/ping-openai`    | OpenAI API 연결 테스트                               |


## ⚙️ 실행 방법

### 1️⃣ 환경 설정
#### 가상환경 생성
```bash
python -m venv .venv
.venv\Scripts\activate
```

#### 필수 라이브러리 설치
```bash
pip install -r requirements.txt
```

#### 환경 변수 (.env)

프로젝트 루트에 .env 파일 생성:
```bash
OPENAI_API_KEY=sk-...             # 🔑 본인의 OpenAI Secret Key
OPENAI_MODEL=gpt-4o-mini-tts
TTS_VOICE=alloy
TTS_FORMAT=mp3

# 백엔드(Spring Boot) API 엔드포인트
BACKEND_URL=
```
#### PyCharm 환경변수 적용 (중요!)
PyCharm은 .env 파일을 자동으로 읽지 않음 → 반드시 설정 필요

✔ 방법

Run → Edit Configurations

1. 실행 구성 선택 (예: main)

2. 아래쪽 Environment variables 섹션

3. “.env 파일 경로” 버튼 클릭

4. 이 경로 입력:
```bash
C:\Users\...\.env
```
5. OK → Run 실행

이제 OPENAI_API_KEY, BACKEND_URL 등이 정상적으로 로드

### 2️⃣ 데이터 준비

아래 경로에 어제 날짜 형식의 일기 파일을 추가합니다.
```bash
data/diaries/test_user_2025-10-31.txt
```

예시:
```text
어제는 친구와 산책하며 기분을 전환했다. 오늘은 더 활기차게 보내고 싶다!
```

### 3️⃣ 서버 실행
```bash
uvicorn apps.morning_boost.main:app --reload --port 8010
```

### 4️⃣ API 테스트
#### ✅ 1. 텍스트 생성 (dryrun)
```arduino
http://127.0.0.1:8010/boost?user_id=test_user&dryrun=1
```
> → GPT가 생성한 응원 멘트 텍스트 반환

#### ✅ 2. 음성 생성 (TTS)
```arduino
http://127.0.0.1:8010/boost?user_id=test_user
```
> → outputs/audio/ 폴더에 mp3 파일로 저장됨

#### ✅ 3. 상태 확인
```arduino
http://127.0.0.1:8010/health
```

## 📁 프로젝트 구조

```bash
morning_boost/
│
├─ apps/
│  └─ morning_boost/
│     ├─ main.py              # FastAPI 서버
│     ├─ prompt_engine.py     # 프롬프트 생성
│     ├─ tts_engine.py        # TTS 생성 로직
│     └─ utils.py             # 백엔드 연동, 파일 경로 등
│
├─ data/
│  └─ morning_boost/          # 생성된 mp3 저장
│
├─ configs/
│  └─ morning_boost.yaml      # 설정 파일 (선택)
│
├─ .env                       # 환경 변수 파일
├─ .gitignore
├─ requirements.txt
└─ README.md

```

## 💡 기술 스택

| 구분              | 사용 기술                            |
| --------------- | -------------------------------- |
| Backend         | **FastAPI**                      |
| AI / LLM        | **OpenAI GPT-4o-mini**           |
| Text-to-Speech  | **OpenAI TTS (gpt-4o-mini-tts)** |
| Scheduling (선택) | APScheduler                      |
| Config          | python-dotenv                    |
| HTTP Client     | httpx                            |


## 📬 향후 개선 아이디어

- 🎧 효과음(인트로 "뾰로롱~") 및 배경음 추가

- 🕖 APScheduler를 이용한 매일 아침 자동 실행

- 📱 사용자별 프리셋 스타일 (cheer / calm / coach)

- 🌤 웹 대시보드 or 모바일 클라이언트 연결

## 🧠 예시 결과

**입력 (전날 일기)**

>어제는 친구와 산책하며 기분을 전환했다. 오늘은 더 활기차게 보내고 싶다!

**출력 (응원 멘트)**

>좋은 아침이에요! 어제는 스스로를 돌보는 시간으로 에너지를 충전했네요.
그 여유와 활기가 오늘 하루에도 이어지길 바라요 ☀️
가볍게 스트레칭하면서, 상쾌한 하루를 시작해봐요!

**TTS 결과**

>outputs/audio/test_user_morning_boost_YYYYMMDD_HHMMSS.mp3

음성 파일은 data/morning_boost/ 아래 mp3로 생성됩니다.
