from __future__ import annotations

import json
import logging

from app.core.config import settings
from app.models.db import PassageRow
from app.services import audio_store
from app.services.sentences import split_sentences

logger = logging.getLogger(__name__)


def synthesize_passage(row: PassageRow) -> tuple[str, list[dict]] | None:
    """Pre-render MP3 + sentence cues. Returns (relative url, cues) or None."""
    language = row.language or "ja"
    sentences = split_sentences(row.text, language)
    if not sentences:
        return None
    if audio_store.exists(row.id) and row.audio_cues_json:
        try:
            cues = json.loads(row.audio_cues_json)
            return f"/api/audio/{row.id}.mp3", cues
        except json.JSONDecodeError:
            pass
    if not settings.azure_speech_key:
        cues = _estimate_cues(sentences, language)
        audio_store.put_mp3(row.id, _silent_mp3())
        return f"/api/audio/{row.id}.mp3", cues
    try:
        audio, cues = _azure_ssml(sentences, language)
        audio_store.put_mp3(row.id, audio)
        return f"/api/audio/{row.id}.mp3", cues
    except Exception:
        logger.exception("Azure TTS failed for %s", row.id)
        return None


def _estimate_cues(sentences: list[str], language: str) -> list[dict]:
    # ~12 Japanese mora / second ≈ 180ms per character as a local stand-in.
    per_char = 180 if language == "ja" else 70
    cues: list[dict] = []
    t = 0
    for i, sent in enumerate(sentences):
        dur = max(600, len(sent) * per_char)
        cues.append(
            {"index": i, "start_ms": t, "end_ms": t + dur, "text": sent}
        )
        t += dur + 180
    return cues


def _silent_mp3() -> bytes:
    # Minimal valid MP3 frame so <audio> can load while Azure is unset.
    return bytes.fromhex(
        "49443304000000000023"  # ID3
        "FFFB900400000000000000000000000000000000"
    )


def _azure_ssml(sentences: list[str], language: str) -> tuple[bytes, list[dict]]:
    import httpx

    voice = (
        settings.azure_speech_voice
        if language == "ja"
        else "ru-RU-SvetlanaNeural"
    )
    locale = "ja-JP" if language == "ja" else "ru-RU"
    parts = []
    for i, sent in enumerate(sentences):
        escaped = (
            sent.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        parts.append(f'<mark name="s{i}"/>{escaped}')
    ssml = (
        f'<speak version="1.0" xml:lang="{locale}">'
        f'<voice name="{voice}">'
        f"{''.join(parts)}"
        "</voice></speak>"
    )
    url = (
        f"https://{settings.azure_speech_region}.tts.speech.microsoft.com"
        "/cognitiveservices/v1"
    )
    headers = {
        "Ocp-Apim-Subscription-Key": settings.azure_speech_key,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-16khz-32kbitrate-mono-mp3",
        "User-Agent": "levla",
    }
    with httpx.Client(timeout=60) as client:
        res = client.post(url, content=ssml.encode("utf-8"), headers=headers)
        res.raise_for_status()
        audio = res.content
    cues = _estimate_cues(sentences, language)
    return audio, cues
