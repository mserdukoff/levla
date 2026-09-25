"""Passage MP3s on local disk (Compose volume or container filesystem)."""

from __future__ import annotations

from app.core.config import settings


def exists(passage_id: str) -> bool:
    return (settings.audio_path / f"{passage_id}.mp3").is_file()


def put_mp3(passage_id: str, data: bytes) -> None:
    dest = settings.audio_path
    dest.mkdir(parents=True, exist_ok=True)
    (dest / f"{passage_id}.mp3").write_bytes(data)


def get_mp3(passage_id: str) -> bytes | None:
    path = settings.audio_path / f"{passage_id}.mp3"
    if not path.is_file():
        return None
    return path.read_bytes()
