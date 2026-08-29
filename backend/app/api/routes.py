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
    TranslationResponse,
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
    pick_next_id,
    read_ids,
    seen_lemmas,
    tokens_from_row,
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
    return PassageStats(
        passage_id=passage_id,
        language=language,  # type: ignore[arg-type]
        placement=placement,  # type: ignore[arg-type]
        read=passage_id in already,
        new_lemmas=new,
        recycled_lemmas=recycled,
        next_id=next_id,
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
    return GlossResponse(
        word=word,
        lemma=morph.lemma,
        morph=morph,
        gloss=lookup_gloss(morph.lemma, lang),
        level=None,
        kanji=kanji,
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
