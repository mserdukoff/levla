from __future__ import annotations

from app.models.schemas import MorphInfo, Token
from app.services.data import gloss_lexicon
from app.services.llm import gloss_lemmas

# A name (person, place, org) has no dictionary meaning to look up. Rather
# than leave these permanently unglossed — confusing on a saved-words list
# or a review card — the reader shows this instead once every real lookup
# (lexicon, then LLM) has come back empty.
NAME_GLOSS = "(name)"


def is_proper_noun(morph: MorphInfo | None) -> bool:
    """True for tokens the analyzer tagged as a person, place, or org name.

    Sudachi marks these with POS slot 1 == 固有名詞; pymorphy3 marks them
    with a Name/Surn/Patr/Geox/Orgn/Trad grammeme. Both are surfaced onto
    `pos_detail` as "proper-noun" by morph_ja.py / morph.py.
    """
    return bool(morph and morph.pos_detail == "proper-noun")


def attach_glosses(
    tokens: list[Token],
    use_llm: bool = True,
    language: str = "ru",
) -> list[Token]:
    lexicon = gloss_lexicon(language)
    missing: list[str] = []
    for tok in tokens:
        if not tok.is_word or not tok.lemma:
            continue
        gloss = lexicon.get(tok.lemma)
        if gloss is None and language == "ru":
            gloss = lexicon.get(tok.lemma.lower())
        if gloss:
            tok.gloss = gloss
        else:
            missing.append(tok.lemma)

    filled = gloss_lemmas(missing, language) if use_llm and missing else {}
    if filled:
        for tok in tokens:
            if tok.is_word and tok.lemma and not tok.gloss:
                tok.gloss = filled.get(tok.lemma)
                if tok.gloss is None and language == "ru":
                    tok.gloss = filled.get(tok.lemma.lower())

    for tok in tokens:
        if tok.is_word and not tok.gloss and is_proper_noun(tok.morph):
            tok.gloss = NAME_GLOSS
    return tokens


def lookup_gloss(lemma: str, language: str = "ru") -> str | None:
    lexicon = gloss_lexicon(language)
    if lemma in lexicon:
        return lexicon[lemma]
    if language == "ru":
        return lexicon.get(lemma.lower())
    return None


def resolve_gloss(lemma: str, language: str = "ru", morph: MorphInfo | None = None) -> str | None:
    """Lexicon lookup, falling back to a name marker for tagged proper nouns.

    Lexicon-only (no LLM call), so it is cheap enough to run at read time —
    used to backfill gloss-less tokens in already-generated passages and
    already-saved words, the same way kanji and grammar are recomputed on
    every read.
    """
    gloss = lookup_gloss(lemma, language)
    if gloss:
        return gloss
    if morph is None:
        from app.services.morph import analyze_word

        morph = analyze_word(lemma, language)
    if is_proper_noun(morph):
        return NAME_GLOSS
    return None
