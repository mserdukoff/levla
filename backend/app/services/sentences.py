from __future__ import annotations

import re

from app.models.schemas import Token

JA_END = set("。！？")
RU_END = set(".!?…")


def sentence_ids(tokens: list[Token], language: str) -> list[int]:
    end = JA_END if language == "ja" else RU_END
    ids: list[int] = []
    sid = 0
    for tok in tokens:
        ids.append(sid)
        if not tok.is_word and any(ch in end for ch in tok.text):
            sid += 1
    return ids


def split_sentences(text: str, language: str) -> list[str]:
    if language == "ja":
        parts = re.split(r"(?<=[。！？])", text)
        return [p.strip() for p in parts if p.strip()]
    parts = re.split(r"(?<=[.!?…])(?:\s+|$)", text.strip())
    return [p.strip() for p in parts if p.strip()]


def english_aligned(source: str, translation: str | None, language: str) -> bool:
    if not translation:
        return False
    return len(split_sentences(source, language)) == len(
        split_sentences(translation, "en")
    )


def sentence_text_at(tokens: list[Token], language: str, sentence_index: int) -> str:
    ids = sentence_ids(tokens, language)
    bits: list[str] = []
    for tok, sid in zip(tokens, ids):
        if sid == sentence_index:
            bits.append(tok.text)
            if tok.ws:
                bits.append(tok.ws)
    return "".join(bits).strip()


def sentence_text_for_lemma(
    tokens: list[Token], language: str, lemma: str
) -> str | None:
    ids = sentence_ids(tokens, language)
    for tok, sid in zip(tokens, ids):
        if tok.lemma == lemma:
            return sentence_text_at(tokens, language, sid)
    return None
