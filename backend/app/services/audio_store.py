"""Passage MP3s: local disk in development, S3 when S3_AUDIO_BUCKET is set."""

from __future__ import annotations

import logging
from functools import lru_cache

from app.core.config import settings

logger = logging.getLogger(__name__)


def _key(passage_id: str) -> str:
    prefix = settings.s3_audio_prefix.strip("/")
    name = f"{passage_id}.mp3"
    return f"{prefix}/{name}" if prefix else name


def uses_s3() -> bool:
    return bool(settings.s3_audio_bucket)


@lru_cache(maxsize=1)
def _s3():
    import boto3

    kwargs = {}
    if settings.aws_region:
        kwargs["region_name"] = settings.aws_region
    return boto3.client("s3", **kwargs)


def exists(passage_id: str) -> bool:
    if uses_s3():
        try:
            _s3().head_object(Bucket=settings.s3_audio_bucket, Key=_key(passage_id))
            return True
        except Exception:
            return False
    return (settings.audio_path / f"{passage_id}.mp3").is_file()


def put_mp3(passage_id: str, data: bytes) -> None:
    if uses_s3():
        _s3().put_object(
            Bucket=settings.s3_audio_bucket,
            Key=_key(passage_id),
            Body=data,
            ContentType="audio/mpeg",
        )
        return
    dest = settings.audio_path
    dest.mkdir(parents=True, exist_ok=True)
    (dest / f"{passage_id}.mp3").write_bytes(data)


def get_mp3(passage_id: str) -> bytes | None:
    if uses_s3():
        try:
            obj = _s3().get_object(
                Bucket=settings.s3_audio_bucket, Key=_key(passage_id)
            )
            return obj["Body"].read()
        except Exception:
            logger.exception("S3 get failed for %s", passage_id)
            return None
    path = settings.audio_path / f"{passage_id}.mp3"
    if not path.is_file():
        return None
    return path.read_bytes()
