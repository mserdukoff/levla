from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.models.db import SessionLocal
from app.models.schemas import (
    FeedbackRequest,
    FeedbackResponse,
    GenerateRequest,
    GlossRequest,
    GlossResponse,
    LibraryResponse,
    PassageResponse,
    PassageStats,
    StarredWord,
    StarRequest,
    TranslationResponse,
    UnstarRequest,
)
from app.services.generate import (
    complete_read,
    ensure_translation,
    generate_passage,
    get_passage,
)
from app.services.gloss import lookup_gloss
from app.services.learner import (
    DEFAULT_LEVEL,
    get_learner,
    lemma_token_stats,
    list_stars,
    pick_next_id,
    read_ids,
    seen_lemmas,
    star_lemma,
    starred_lemmas,
    tokens_from_row,
    unstar_lemma,
    valid_device_id,
)
from app.services.library import list_library
from app.services.morph import analyze_word

router = APIRouter(prefix="/api")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/health")
def health():
    return {"ok": True, "name": "levla"}


@router.post("/generate", response_model=PassageResponse)
def post_generate(body: GenerateRequest, db: Session = Depends(get_db)):
    try:
        return generate_passage(
            db, body.level, body.topic.strip(), body.genre, body.language
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Generation failed: {e}") from e


@router.get("/library", response_model=LibraryResponse)
def get_library(
    language: str = "ja",
    db: Session = Depends(get_db),
    x_device_id: str | None = Header(default=None),
):
    if language not in {"ru", "ja"}:
        raise HTTPException(status_code=400, detail="language must be ru or ja")
    return list_library(db, language, valid_device_id(x_device_id))


@router.get("/passages/{passage_id}", response_model=PassageResponse)
def get_passage_route(passage_id: str, db: Session = Depends(get_db)):
    passage = get_passage(db, passage_id)
    if passage is None:
        raise HTTPException(status_code=404, detail="Passage not found")
    return passage


@router.get("/passages/{passage_id}/translation", response_model=TranslationResponse)
def get_passage_translation(passage_id: str, db: Session = Depends(get_db)):
    translation = ensure_translation(db, passage_id)
    if translation is None:
        row_missing = get_passage(db, passage_id) is None
        if row_missing:
            raise HTTPException(status_code=404, detail="Passage not found")
        raise HTTPException(status_code=503, detail="Translation is not available yet.")
    return TranslationResponse(passage_id=passage_id, translation=translation)


@router.get("/passages/{passage_id}/stats", response_model=PassageStats)
def get_passage_stats(
    passage_id: str,
    db: Session = Depends(get_db),
    x_device_id: str | None = Header(default=None),
):
    from app.models.db import PassageRow

    row = db.get(PassageRow, passage_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Passage not found")
    language = row.language or "ru"
    device_id = valid_device_id(x_device_id)
    placement = DEFAULT_LEVEL
    already: set[str] = set()
    seen: set[str] = set()
    if device_id:
        learner = get_learner(db, device_id, language)
        if learner is not None:
            placement = learner.level
        seen = seen_lemmas(db, device_id, language)
        already = read_ids(db, device_id)
    new, recycled = lemma_token_stats(tokens_from_row(row), language, seen)
    next_id = pick_next_id(
        db, language, placement, already, exclude_id=passage_id
    )
    starred = sorted(starred_lemmas(db, device_id, language)) if device_id else []
    return PassageStats(
        passage_id=passage_id,
        language=language,  # type: ignore[arg-type]
        placement=placement,  # type: ignore[arg-type]
        read=passage_id in already,
        new_lemmas=new,
        recycled_lemmas=recycled,
        next_id=next_id,
        known_lemmas=sorted(seen),
        starred_lemmas=starred,
    )


@router.post("/gloss", response_model=GlossResponse)
def post_gloss(body: GlossRequest, db: Session = Depends(get_db)):
    word = body.word.strip()
    if body.passage_id:
        passage = get_passage(db, body.passage_id)
        if passage:
            for tok in passage.tokens:
                if tok.is_word and tok.text == word:
                    morph = tok.morph
                    if morph is None:
                        break
                    return GlossResponse(
                        word=word,
                        lemma=morph.lemma,
                        morph=morph,
                        gloss=tok.gloss,
                        level=tok.level,
                        kanji=tok.kanji,
                        role=tok.role,
                        conj=tok.conj,
                    )
    lang = "ru"
    if body.passage_id:
        passage = get_passage(db, body.passage_id)
        if passage:
            lang = passage.language
    morph = analyze_word(word, lang)
    kanji = []
    if lang == "ja":
        from app.services.kanji import breakdown

        kanji = breakdown(word, morph.reading)
    from app.models.schemas import Token
    from app.services.grammar import attach_grammar

    live = Token(text=word, lemma=morph.lemma, morph=morph, is_word=True, kanji=kanji)
    attach_grammar([live], lang)
    return GlossResponse(
        word=word,
        lemma=morph.lemma,
        morph=morph,
        gloss=lookup_gloss(morph.lemma, lang),
        level=None,
        kanji=kanji,
        role=live.role,
        conj=live.conj,
    )


@router.post("/feedback", response_model=FeedbackResponse)
def post_feedback(
    body: FeedbackRequest,
    db: Session = Depends(get_db),
    x_device_id: str | None = Header(default=None),
):
    result = complete_read(
        db, body.passage_id, body.rating, valid_device_id(x_device_id)
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Passage not found")
    return FeedbackResponse(**result)


@router.get("/words", response_model=list[StarredWord])
def get_words(
    language: str = "ja",
    db: Session = Depends(get_db),
    x_device_id: str | None = Header(default=None),
):
    if language not in {"ru", "ja"}:
        raise HTTPException(status_code=400, detail="language must be ru or ja")
    device_id = valid_device_id(x_device_id)
    if not device_id:
        return []
    return list_stars(db, device_id, language)


@router.post("/words", response_model=StarredWord)
def post_word(
    body: StarRequest,
    db: Session = Depends(get_db),
    x_device_id: str | None = Header(default=None),
):
    device_id = valid_device_id(x_device_id)
    if not device_id:
        raise HTTPException(status_code=400, detail="A device id is required to save a word.")
    language = body.language
    if body.passage_id:
        passage = get_passage(db, body.passage_id)
        if passage is None:
            raise HTTPException(status_code=404, detail="Passage not found")
        language = passage.language
    if language not in {"ru", "ja"}:
        raise HTTPException(status_code=400, detail="language must be ru or ja")
    lemma = body.lemma.strip()
    if not lemma:
        raise HTTPException(status_code=400, detail="lemma is required")
    return star_lemma(
        db,
        device_id,
        language,
        lemma,
        body.gloss.strip() if body.gloss else None,
        body.passage_id,
    )


@router.delete("/words", response_model=dict)
def delete_word(
    body: UnstarRequest,
    db: Session = Depends(get_db),
    x_device_id: str | None = Header(default=None),
):
    device_id = valid_device_id(x_device_id)
    if not device_id:
        raise HTTPException(status_code=400, detail="A device id is required to remove a word.")
    unstar_lemma(db, device_id, body.language, body.lemma.strip())
    return {"ok": True}
