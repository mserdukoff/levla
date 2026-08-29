from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.core.config import settings

LEVEL_ORDER = {"A1": 0, "A2": 1, "B1": 2, "B2": 3, "C1": 4, "C2": 5}
SUPPORTED = ("ru", "ja")


def _lang(language: str) -> str:
    return language if language in SUPPORTED else "ru"


@lru_cache(maxsize=4)
def grammar_rules(language: str = "ru") -> dict:
    path = settings.data_dir / "grammar" / f"{_lang(language)}_cefr.json"
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=4)
def vocab_bands(language: str = "ru") -> dict[str, str]:
    path = settings.data_dir / "vocab" / f"{_lang(language)}_cefr.json"
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=4)
def gloss_lexicon(language: str = "ru") -> dict[str, str]:
    path = settings.data_dir / "gloss" / f"{_lang(language)}_en.json"
    return json.loads(path.read_text(encoding="utf-8"))


def level_rank(level: str) -> int:
    return LEVEL_ORDER.get(level, 99)


def lemmas_at_or_below(level: str, language: str = "ru") -> list[str]:
    cap = level_rank(level)
    return [
        lemma
        for lemma, band in vocab_bands(language).items()
        if level_rank(band) <= cap
    ]


def data_paths(language: str = "ru") -> dict[str, Path]:
    d = settings.data_dir
    code = _lang(language)
    return {
        "grammar": d / "grammar" / f"{code}_cefr.json",
        "vocab": d / "vocab" / f"{code}_cefr.json",
        "gloss": d / "gloss" / f"{code}_en.json",
    }
