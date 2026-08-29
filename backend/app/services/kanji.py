from __future__ import annotations

import json
import re
from functools import lru_cache

from app.core.config import settings
from app.models.schemas import KanjiPart

_KATAKANA_START = 0x30A1
_KATAKANA_END = 0x30F6
_KATA_TO_HIRA = 0x60

_KANJI = re.compile(r"[\u4e00-\u9faf]")
_KANA = re.compile(r"[\u3040-\u30ff]")

_DAKUTEN = str.maketrans(
    "かきくけこさしすせそたちつてとはひふへほ",
    "がぎぐげござじずぜぞだぢづでどばびぶべぼ",
)
_HANDAKU = str.maketrans("はひふへほ", "ぱぴぷぺぽ")
_SOKUON_END = {"く", "き", "ち", "つ"}


def _kata_to_hira(text: str) -> str:
    out = []
    for ch in text:
        cp = ord(ch)
        if _KATAKANA_START <= cp <= _KATAKANA_END:
            out.append(chr(cp - _KATA_TO_HIRA))
        else:
            out.append(ch)
    return "".join(out)


@lru_cache(maxsize=1)
def kanji_dict() -> dict[str, dict]:
    path = settings.data_dir / "kanji" / "ja.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _clean_reading(raw: str) -> str:
    stem = raw.replace("-", "").split(".")[0]
    return _kata_to_hira(stem)


def _variants(reading: str) -> list[str]:
    out = [reading]
    voiced = reading.translate(_DAKUTEN)
    if voiced != reading:
        out.append(voiced)
    handaku = reading.translate(_HANDAKU)
    if handaku != reading:
        out.append(handaku)
    if reading.endswith(tuple(_SOKUON_END)) and len(reading) >= 2:
        out.append(reading[:-1] + "っ")
    return out


def _candidates(char: str) -> list[str]:
    info = kanji_dict().get(char) or {}
    cands: list[str] = []
    seen: set[str] = set()
    for raw in list(info.get("on") or []) + list(info.get("kun") or []):
        base = _clean_reading(raw)
        if not base:
            continue
        for v in _variants(base):
            if v not in seen:
                seen.add(v)
                cands.append(v)
    cands.sort(key=len, reverse=True)
    return cands


def _standalone_meaning(char: str) -> str:
    info = kanji_dict().get(char) or {}
    meanings = [str(m).strip() for m in (info.get("meanings") or []) if m]
    return ", ".join(m.lower() for m in meanings[:3])


def _on_kun(char: str) -> tuple[list[str], list[str]]:
    info = kanji_dict().get(char) or {}
    on = [_clean_reading(r) for r in (info.get("on") or []) if r]
    kun = [_clean_reading(r) for r in (info.get("kun") or []) if r]
    return on, kun


def breakdown(surface: str, word_reading: str | None) -> list[KanjiPart]:
    """Align each kanji in *surface* to a slice of the word reading."""
    if not _KANJI.search(surface):
        return []
    remaining = _kata_to_hira(word_reading or "")
    parts: list[KanjiPart] = []

    for ch in surface:
        if _KANJI.match(ch):
            matched = None
            for cand in _candidates(ch):
                if remaining.startswith(cand):
                    matched = cand
                    remaining = remaining[len(cand) :]
                    break
            on, kun = _on_kun(ch)
            parts.append(
                KanjiPart(
                    char=ch,
                    reading=matched,
                    on=on,
                    kun=kun,
                    meaning=_standalone_meaning(ch),
                )
            )
        elif _KANA.match(ch):
            hira = _kata_to_hira(ch)
            if remaining.startswith(hira):
                remaining = remaining[len(hira) :]
    return parts
