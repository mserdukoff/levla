from __future__ import annotations

from app.models.schemas import Token
from app.services.data import grammar_rules, level_rank, vocab_bands
from app.services.validator import ValidationResult

CONTENT_POS = {"noun", "verb", "i-adj", "na-adj", "adverb"}
KEIGO = {
    "いらっしゃる",
    "おっしゃる",
    "なさる",
    "くださる",
    "いたす",
    "申す",
    "申し上げる",
    "ございます",
    "いただく",
    "差し上げる",
    "拝見",
    "承知",
}


def _next_word(tokens: list[Token], index: int) -> Token | None:
    for t in tokens[index + 1 :]:
        if t.is_word:
            return t
    return None


def _prev_word(tokens: list[Token], index: int) -> Token | None:
    for t in reversed(tokens[:index]):
        if t.is_word:
            return t
    return None


def _detect_constructions(tokens: list[Token], i: int, tok: Token) -> list[str]:
    hits: list[str] = []
    lemma = tok.lemma or ""
    morph = tok.morph
    form = (morph.form if morph else None) or ""
    pos = (morph.pos if morph else None) or ""
    prev = _prev_word(tokens, i)
    nxt = _next_word(tokens, i)

    if tok.text in {"て", "で"} and pos == "particle":
        hits.append("te_form")
        if nxt and nxt.lemma in {"いる", "おる"}:
            hits.append("te_iru")

    if lemma in {"た", "だ"} and pos == "aux":
        if not (prev and prev.lemma in {"ます", "です"}):
            hits.append("plain_past")

    if lemma == "ない" and pos == "aux":
        if not (prev and prev.lemma in {"ます", "です"}):
            hits.append("plain_neg")

    if lemma in {"ば", "たら", "なら"} or form.startswith("仮定形"):
        hits.append("conditional")

    if lemma in {"れる", "られる"}:
        hits.append("potential")
        hits.append("passive")

    if lemma in {"させる", "せる"}:
        hits.append("causative")

    if form.startswith("連体形") and nxt and nxt.morph and nxt.morph.pos == "noun":
        if pos == "verb":
            hits.append("relative")

    if lemma in KEIGO:
        hits.append("keigo")

    return hits


def validate_tokens_ja(tokens: list[Token], level: str) -> ValidationResult:
    rules = grammar_rules("ja")[level]
    forbidden = set(rules.get("forbidden_constructions") or [])
    forbidden_lemmas = set(rules.get("forbidden_lemmas") or [])
    bands = vocab_bands("ja")
    cap = level_rank(level)

    word_tokens = [t for t in tokens if t.is_word and t.morph]
    n = max(len(word_tokens), 1)

    pos_hits = 0
    sub_hits = 0
    conj_hits = 0
    overlevel = 0
    content_n = 0
    flags: list[str] = []
    seen: set[str] = set()

    def flag(msg: str) -> None:
        if msg not in seen:
            seen.add(msg)
            flags.append(msg)

    for i, tok in enumerate(tokens):
        if not tok.is_word or not tok.morph:
            continue
        lemma = tok.morph.lemma
        pos = tok.morph.pos or ""

        for cons in _detect_constructions(tokens, i, tok):
            if cons in forbidden:
                conj_hits += 1
                flag(f"ja:{cons} ({tok.text})")

        if lemma in forbidden_lemmas:
            conj_hits += 1
            flag(f"conj:{lemma}")

        if pos in CONTENT_POS:
            content_n += 1
            band = bands.get(lemma)
            if band is None or level_rank(band) > cap:
                # Skip names / katakana loanwords that look proper
                if tok.text[:1].isupper():
                    continue
                overlevel += 1
                if band:
                    flag(f"lemma:{lemma}={band}")
                else:
                    flag(f"lemma:{lemma}=unknown")

    over_rate = overlevel / max(content_n, 1)
    lemma_flags = [f for f in flags if f.startswith("lemma:")]
    other_flags = [f for f in flags if not f.startswith("lemma:")]
    flags = other_flags + lemma_flags[:12]

    passed = (
        over_rate <= rules["max_overlevel_lemma_rate"]
        and conj_hits == 0
        and (sub_hits / n) <= rules["max_subordinate_rate"]
        and (pos_hits / n) <= rules["max_forbidden_pos_rate"]
    )

    return ValidationResult(
        passed=passed,
        overlevel_lemma_rate=round(over_rate, 4),
        subordinate_rate=round(sub_hits / n, 4),
        forbidden_case_rate=0.0,
        forbidden_tense_rate=0.0,
        forbidden_pos_rate=round(pos_hits / n, 4),
        flags=flags,
    )
