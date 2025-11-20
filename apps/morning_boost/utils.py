"""
공용 유틸 함수들.
"""

from pathlib import Path
import yaml

# maum/ 기준
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "configs"
DATA_DIR = PROJECT_ROOT / "data" / "morning_boost"


def load_config(name: str = "morning_boost.yaml") -> dict:
    """
    configs/morning_boost.yaml 을 읽어서 dict 로 반환.
    없어도 에러 안 나게 비어있는 dict 반환.
    """
    cfg_path = CONFIG_DIR / name
    if not cfg_path.exists():
        return {}
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_data_dir() -> Path:
    """
    mp3 파일 저장 디렉토리 반환 (없으면 생성)
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR
