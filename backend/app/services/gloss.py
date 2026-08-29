from __future__ import annotations

from app.models.schemas import Token
from app.services.data import gloss_lexicon
from app.services.llm import gloss_lemmas


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
    return tokens


def lookup_gloss(lemma: str, language: str = "ru") -> str | None:
    lexicon = gloss_lexicon(language)
    if lemma in lexicon:
        return lexicon[lemma]
    if language == "ru":
        return lexicon.get(lemma.lower())
    return None
