from __future__ import annotations

import json
import re
from functools import lru_cache

from app.core.config import settings
from app.models.schemas import KanjiPart

_KATAKANA_START = 0x30A1
_KATAKANA_END = 0x30F6
_HIRAGANA_START = 0x3041
_HIRAGANA_END = 0x3096
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


def _hira_to_kata(text: str) -> str:
    out = []
    for ch in text:
        cp = ord(ch)
        if _HIRAGANA_START <= cp <= _HIRAGANA_END:
            out.append(chr(cp + _KATA_TO_HIRA))
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


def _int_or_none(value: object) -> int | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return None


def _part(char: str, matched: str | None) -> KanjiPart:
    info = kanji_dict().get(char) or {}
    on = [_hira_to_kata(str(r)) for r in (info.get("on") or []) if r]
    kun = [str(r) for r in (info.get("kun") or []) if r]
    meanings = [str(m).strip() for m in (info.get("meanings") or []) if m]
    meaning = ", ".join(m.lower() for m in meanings)
    parts = [str(p) for p in (info.get("parts") or []) if p and p != char]
    nanori = [str(n) for n in (info.get("nanori") or []) if n]
    radical = str(info["radical"]) if info.get("radical") else None
    radical_name = str(info["radical_name"]) if info.get("radical_name") else None
    return KanjiPart(
        char=char,
        reading=matched,
        on=on,
        kun=kun,
        meaning=meaning,
        strokes=_int_or_none(info.get("strokes")),
        jlpt=_int_or_none(info.get("jlpt")),
        grade=_int_or_none(info.get("grade")),
        freq=_int_or_none(info.get("freq")),
        radical=radical,
        radical_name=radical_name,
        parts=parts,
        nanori=nanori,
    )


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
            parts.append(_part(ch, matched))
        elif _KANA.match(ch):
            hira = _kata_to_hira(ch)
            if remaining.startswith(hira):
                remaining = remaining[len(hira) :]
    return parts
