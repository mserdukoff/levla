from __future__ import annotations

from app.models.schemas import ConjPiece, Token

# Particles that continue a verb/adjective chain (not case で).
_CONJ_PARTICLES = {
    "て": "te-form",
    "で": "te-form",
    "ば": "conditional",
    "ながら": "while",
    "たり": "and such",
}

_SUBSIDIARY = {
    "いる": "progressive",
    "おる": "progressive",
    "いく": "go on",
    "行く": "go on",
    "くる": "come to",
    "来る": "come to",
    "しまう": "completion",
    "みる": "try",
    "見る": "try",
    "おく": "prepare",
    "くれる": "for me",
    "あげる": "for someone",
    "もらう": "receive",
    "くださる": "please",
}

_AUX_LABELS = {
    "ます": "polite",
    "です": "copula",
    "だ": "copula",
    "た": "past",
    "ない": "negative",
    "ぬ": "negative",
    "ん": "negative",
    "れる": "passive",
    "られる": "passive / potential",
    "せる": "causative",
    "させる": "causative",
    "たい": "want to",
    "べき": "should",
    "べし": "should",
}

_RU_ROLE = {
    "VERB": "verb",
    "INFN": "verb",
    "PRTF": "verb",
    "PRTS": "verb",
    "GRND": "verb",
    "ADJF": "adj",
    "ADJS": "adj",
    "COMP": "adj",
    "PRED": "adj",
    "PREP": "particle",
    "CONJ": "particle",
    "PRCL": "particle",
    "ADVB": "adverb",
}

def attach_grammar(tokens: list[Token], language: str) -> list[Token]:
    """Fill role / conj / conj_id. Safe to run again on stored tokens."""
    for tok in tokens:
        tok.role = None
        tok.conj = []
        tok.conj_id = None
    if language == "ja":
        _attach_ja(tokens)
    else:
        _attach_ru(tokens)
    return tokens


def _pos(tok: Token) -> str:
    return (tok.morph.pos if tok.morph else None) or ""


def _detail(tok: Token) -> str:
    return (tok.morph.pos_detail if tok.morph else None) or ""


def _form(tok: Token) -> str:
    return (tok.morph.form if tok.morph else None) or ""


def _conj_type(tok: Token) -> str:
    return (tok.morph.conj_type if tok.morph else None) or ""


def _form0(tok: Token) -> str:
    return _form(tok).split("-")[0]


def _attach_ru(tokens: list[Token]) -> None:
    for tok in tokens:
        if not tok.is_word or not tok.morph:
            continue
        tok.role = _RU_ROLE.get(_pos(tok))


def _ja_base_role(tok: Token) -> str | None:
    pos = _pos(tok)
    lemma = tok.lemma or tok.text
    if pos == "particle":
        if lemma == "は":
            return "topic"
        if lemma == "が":
            return "subject"
        if lemma == "を":
            return "object"
        return "particle"
    if pos == "verb":
        return "verb"
    if pos == "aux":
        return "aux"
    if pos in {"i-adj", "na-adj"}:
        return "adj"
    if pos == "adverb":
        return "adverb"
    return None


def _is_starter(tok: Token) -> bool:
    if not tok.is_word or not tok.morph:
        return False
    return _pos(tok) in {"verb", "i-adj", "na-adj", "aux"}


def _is_conjunctive_particle(tok: Token) -> bool:
    if _pos(tok) != "particle":
        return False
    lemma = tok.lemma or tok.text
    if lemma not in _CONJ_PARTICLES:
        return False
    detail = _detail(tok)
    if lemma in {"て", "で"}:
        return detail in {"conjunctive", ""}
    return True


def _continues(prev: Token, nxt: Token) -> bool:
    if not nxt.is_word or not nxt.morph:
        return False
    npos = _pos(nxt)
    nlemma = nxt.lemma or nxt.text
    if npos == "aux":
        return True
    if _is_conjunctive_particle(nxt):
        return True
    if nlemma in _SUBSIDIARY and npos == "verb":
        prev_lemma = prev.lemma or prev.text
        return prev_lemma in {"て", "で"} or _is_conjunctive_particle(prev)
    if nlemma == "ない" and npos == "i-adj":
        return True
    if npos == "na-adj" and nlemma == "そう" and _detail(nxt) in {"aux-stem", ""}:
        return True
    return False


def _piece_label(tok: Token) -> str:
    lemma = tok.lemma or tok.text
    form0 = _form0(tok)
    if lemma == "た" and form0 == "仮定形":
        return "conditional"
    if lemma == "だ" and tok.text == "な":
        return "adnominal"
    if _is_conjunctive_particle(tok):
        return _CONJ_PARTICLES.get(lemma, "particle")
    if lemma in _SUBSIDIARY and _pos(tok) == "verb" and _detail(tok) == "bound":
        return _SUBSIDIARY[lemma]
    if lemma in _AUX_LABELS:
        return _AUX_LABELS[lemma]
    if lemma == "ない":
        return "negative"
    if form0 == "命令形":
        return "imperative"
    if form0 == "意志推量形":
        return "volitional"
    pos = _pos(tok)
    if pos in {"verb", "i-adj", "na-adj"}:
        return "stem"
    if pos == "aux":
        return "auxiliary"
    return pos or "ending"


def _ending_label(tok: Token) -> str:
    form0 = _form0(tok)
    if form0 == "連体形":
        return "attributive"
    if form0 == "意志推量形":
        return "volitional"
    if form0 == "命令形":
        return "imperative"
    return "dictionary"


def _split_head(tok: Token) -> list[ConjPiece]:
    """Split a dictionary/attributive/volitional head into stem + ending."""
    surface = tok.text
    form0 = _form0(tok)
    pos = _pos(tok)

    if form0 == "意志推量形":
        if surface.endswith("よう") and len(surface) > 2:
            return [
                ConjPiece(text=surface[:-2], label="stem"),
                ConjPiece(text="よう", label="volitional"),
            ]
        if surface.endswith("う") and len(surface) > 1:
            return [
                ConjPiece(text=surface[:-1], label="stem"),
                ConjPiece(text=surface[-1], label="volitional"),
            ]
        return [ConjPiece(text=surface, label="volitional")]

    if form0 == "命令形":
        return [ConjPiece(text=surface, label="imperative")]

    if form0 not in {"終止形", "連体形"}:
        return [ConjPiece(text=surface, label="stem")]

    end_label = _ending_label(tok)

    if pos == "i-adj" or _conj_type(tok) == "i-adj":
        if surface.endswith("い") and len(surface) > 1 and surface != "いい":
            return [
                ConjPiece(text=surface[:-1], label="stem"),
                ConjPiece(text="い", label=end_label),
            ]
        return [ConjPiece(text=surface, label="stem")]

    if pos == "verb" and len(surface) > 1:
        return [
            ConjPiece(text=surface[:-1], label="stem"),
            ConjPiece(text=surface[-1], label=end_label),
        ]

    return [ConjPiece(text=surface, label=_piece_label(tok))]


def _chain_pieces(chain: list[Token]) -> list[ConjPiece]:
    pieces: list[ConjPiece] = []
    for i, tok in enumerate(chain):
        if i == 0 and _pos(tok) in {"verb", "i-adj"}:
            pieces.extend(_split_head(tok))
        else:
            pieces.append(ConjPiece(text=tok.text, label=_piece_label(tok)))
    return pieces


def _attach_ja(tokens: list[Token]) -> None:
    i = 0
    n = len(tokens)
    while i < n:
        tok = tokens[i]
        if not _is_starter(tok):
            if tok.is_word:
                tok.role = _ja_base_role(tok)
            i += 1
            continue
        j = i + 1
        while j < n and _continues(tokens[j - 1], tokens[j]):
            j += 1
        chain = tokens[i:j]
        pieces = _chain_pieces(chain)
        head_role = _ja_base_role(chain[0]) or "verb"
        for member in chain:
            member.conj = pieces
            member.conj_id = i
            if member is chain[0]:
                member.role = head_role
            else:
                member.role = "aux"
        i = j
