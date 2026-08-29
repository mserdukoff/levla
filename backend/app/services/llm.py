from __future__ import annotations

import json
import logging
import random
import re

from openai import OpenAI

from app.core.config import settings
from app.services.data import grammar_rules, lemmas_at_or_below

logger = logging.getLogger(__name__)

GENRE_HINTS = {
    "daily_life": "everyday life, a small scene at home or in the city",
    "travel": "travel, a trip, a station or a new city",
    "news": "a short news-style report, still narrative, not a headline dump",
    "folklore": "a folk-tale or fable tone, simple characters",
    "work": "work, a workplace, colleagues, a task",
}

LANG_META = {
    "ru": {
        "name": "Russian",
        "script_note": "Mark ё where it belongs (её, ещё, чёрный, etc.). Do not use Latin letters inside the Russian text.",
        "length": "Length: 400 to 700 Russian words (count words, not characters).",
        "gloss": "Give a short English gloss (1–5 words) for each Russian lemma.",
    },
    "ja": {
        "name": "Japanese",
        "script_note": "Use standard modern orthography. Furigana is not needed in the text. Do not insert spaces between Japanese words.",
        "length": "Length: 22 to 40 short sentences (a real reading session, not a paragraph stub).",
        "gloss": "Give a short English gloss (1–5 words) for each Japanese lemma (dictionary form).",
    },
}


def _client() -> OpenAI:
    if not settings.openrouter_api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. Add it to backend/.env to generate passages."
        )
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.openrouter_api_key,
        default_headers={"HTTP-Referer": "http://localhost:3000", "X-Title": "Levla"},
    )


def _lemma_sample(level: str, language: str, n: int = 48) -> list[str]:
    pool = lemmas_at_or_below(level, language)
    if len(pool) <= n:
        return pool
    rng = random.Random(language + level + str(len(pool)))
    return sorted(rng.sample(pool, n))


def _parse_json(content: str) -> dict:
    text = (content or "").strip()
    for fence in ("```json", "```"):
        if text.startswith(fence):
            text = text[len(fence) :]
        if text.endswith("```"):
            text = text[: -3]
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.S)
        if match:
            return json.loads(match.group(0))
        raise


def generate_passage_text(
    level: str,
    topic: str,
    genre: str | None = None,
    correction_flags: list[str] | None = None,
    language: str = "ru",
) -> tuple[str, str]:
    """Return (title, text). Raises if the LLM is not configured or returns garbage."""
    meta = LANG_META.get(language, LANG_META["ru"])
    rules = grammar_rules(language)[level]
    sample = ", ".join(_lemma_sample(level, language))
    genre_line = ""
    if genre and genre in GENRE_HINTS:
        genre_line = f"Genre: {GENRE_HINTS[genre]}.\n"

    correction = ""
    if correction_flags:
        listed = "; ".join(correction_flags[:20])
        correction = (
            "\nThe previous draft drifted out of level. Rewrite the whole passage. "
            f"Fix these issues: {listed}. "
            "Do not reuse the over-level constructions.\n"
        )

    lang_name = meta["name"]
    prompt = f"""You are a {lang_name} language educator writing a graded reader.

Write a coherent {lang_name} passage for CEFR {level} learners.
Topic: {topic}
{genre_line}{meta["length"]} Write enough for a real reading session.

GRAMMAR CONSTRAINTS FOR {level}:
{rules["prompt_constraints"]}

Prefer lemmas from this in-band sample (you may use other {level}-appropriate words too):
{sample}

RULES:
1. Write ONLY in {lang_name} in the passage text. The title is also {lang_name}.
2. The passage must be a complete, readable story or article with a beginning and end.
3. {meta["script_note"]}
4. Do not include English, notes, glosses, or vocabulary lists in the text.

Respond ONLY with valid JSON:
{{
  "title": "{lang_name} title",
  "text": "Full {lang_name} passage as one or more paragraphs separated by newlines."
}}
{correction}"""

    client = _client()
    completion = client.chat.completions.create(
        model=settings.llm_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7 if not correction_flags else 0.4,
        timeout=45.0,
    )
    content = completion.choices[0].message.content or ""
    data = _parse_json(content)
    title = str(data.get("title") or "").strip()
    text = str(data.get("text") or "").strip()
    if not text:
        raise RuntimeError("LLM returned an empty passage")
    if not title:
        title = topic
    return title, text


def gloss_lemmas(lemmas: list[str], language: str = "ru") -> dict[str, str]:
    """One-shot English glosses for unknown lemmas. Empty dict on failure."""
    unique = sorted({l for l in lemmas if l})
    if language == "ru":
        unique = sorted({l.lower() for l in unique})
    if not unique:
        return {}
    if not settings.openrouter_api_key:
        return {}
    meta = LANG_META.get(language, LANG_META["ru"])
    prompt = (
        f"{meta['gloss']} "
        "Respond ONLY with JSON object mapping lemma → gloss.\n\n"
        + json.dumps(unique, ensure_ascii=False)
    )
    try:
        client = _client()
        completion = client.chat.completions.create(
            model=settings.llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            timeout=30.0,
        )
        data = _parse_json(completion.choices[0].message.content or "")
        out: dict[str, str] = {}
        for k, v in data.items():
            if isinstance(v, str) and v.strip():
                key = str(k).lower() if language == "ru" else str(k)
                out[key] = v.strip()
        return out
    except Exception:
        logger.exception("gloss_lemmas failed")
        return {}


def translate_passage(text: str, language: str) -> str | None:
    """English translation of a full passage. None if the LLM is unavailable."""
    if not text.strip() or not settings.openrouter_api_key:
        return None
    meta = LANG_META.get(language, LANG_META["ru"])
    prompt = f"""Translate this {meta["name"]} graded-reader passage into natural English.
Keep the same paragraph breaks. Do not add titles, notes, or commentary.
Respond ONLY with the English translation.

{text}"""
    try:
        client = _client()
        completion = client.chat.completions.create(
            model=settings.llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            timeout=45.0,
        )
        out = (completion.choices[0].message.content or "").strip()
        if out.startswith("```"):
            out = out.strip("`").strip()
        return out or None
    except Exception:
        logger.exception("translate_passage failed")
        return None
