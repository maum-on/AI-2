# scripts/jobs/morning_cron.py
"""
매일 정해진 시간마다 morning_boost API를 자동으로 호출하는 스케줄러
"""

import requests
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apps.morning_boost.utils import load_config

cfg = load_config()

scheduler = BlockingScheduler()

def run_boost():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] Running scheduled morning boost")

    # 나중에 user 목록 불러오게 바꿔도 됨
    user_id = "test_user"

    try:
        res = requests.get(
            "http://127.0.0.1:8010/boost",
            params={"user_id": user_id, "dryrun": 1},
            timeout=10,
        )
        print("[BOOST RESULT]", res.json())
    except Exception as e:
        print("[BOOST ERROR]", e)


scheduler.add_job(
    run_boost,
    "cron",
    hour=cfg["schedule"]["hour"],
    minute=cfg["schedule"]["minute"],
)

if __name__ == "__main__":
    print("⏰ Morning boost cron scheduler is started...")
    scheduler.start()
