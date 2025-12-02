
# apps/morning_boost/s3_client.py

import os
from pathlib import Path
from typing import Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError


AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_S3_PUBLIC_BASE = os.getenv("AWS_S3_PUBLIC_BASE")  # 선택


if not AWS_S3_BUCKET:
    raise RuntimeError("AWS_S3_BUCKET 환경변수가 설정되어 있지 않습니다.")


# 세션 & 클라이언트 생성
_session = boto3.session.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)
_s3 = _session.client("s3")


def upload_audio_to_s3(local_path: Path, user_id: str) -> str:
    """
    로컬 mp3 파일을 S3 버킷에 업로드하고, 외부에서 접근 가능한 URL을 반환.

    key 예시: morning_boost/{user_id}/파일명.mp3
    """
    if not local_path.exists():
        raise FileNotFoundError(local_path)

    key = f"morning_boost/{user_id}/{local_path.name}"

    try:
        _s3.upload_file(
            str(local_path),
            AWS_S3_BUCKET,
            key,
            ExtraArgs={"ContentType": "audio/mpeg"},
        )
    except (BotoCoreError, ClientError) as e:
        raise RuntimeError(f"S3 업로드 실패: {e}") from e

    # 1) CloudFront나 자체 도메인이 있으면 그걸 우선 사용
    if AWS_S3_PUBLIC_BASE:
        base = AWS_S3_PUBLIC_BASE.rstrip("/")
        return f"{base}/{key}"

    # 2) 없으면 기본 S3 퍼블릭 URL 사용 (버킷이 public-read여야 함)
    return f"https://{AWS_S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{key}"
