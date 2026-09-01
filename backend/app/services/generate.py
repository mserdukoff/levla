from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.db import FeedbackRow, PassageRow
from app.models.schemas import (
    Calibration,
    FeedbackRating,
    PassageResponse,
    Token,
)
from app.services.gloss import attach_glosses
from app.services.llm import generate_passage_text, translate_passage
from app.services.morph import analyze_text, word_count
from app.services.validator import ValidationResult, validate_tokens

logger = logging.getLogger(__name__)


def _to_response(row: PassageRow) -> PassageResponse:
    tokens = [Token.model_validate(t) for t in json.loads(row.tokens_json)]
    language = getattr(row, "language", None) or "ru"
    if language == "ja":
        from app.services.kanji import breakdown

        for tok in tokens:
            if tok.is_word:
                reading = tok.morph.reading if tok.morph else None
                tok.kanji = breakdown(tok.text, reading)
    from app.services.grammar import attach_grammar

    attach_grammar(tokens, language)
    calibration = Calibration.model_validate(json.loads(row.calibration_json))
    created = row.created_at
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    return PassageResponse(
        id=row.id,
        language=getattr(row, "language", None) or "ru",  # type: ignore[arg-type]
        level=row.level,  # type: ignore[arg-type]
        topic=row.topic,
        genre=row.genre,
        title=row.title,
        text=row.text,
        tokens=tokens,
        calibration=calibration,
        word_count=row.word_count,
        created_at=created,
        translation=getattr(row, "translation", None) or None,
    )


def _persist(
    db: Session,
    *,
    language: str,
    level: str,
    topic: str,
    genre: str | None,
    title: str,
    text: str,
    tokens: list[Token],
    calibration: Calibration,
    translation: str | None = None,
) -> PassageRow:
    row = PassageRow(
        id=str(uuid.uuid4()),
        language=language,
        level=level,
        topic=topic,
        genre=genre,
        title=title,
        text=text,
        tokens_json=json.dumps(
            [t.model_dump() for t in tokens], ensure_ascii=False
        ),
        calibration_json=calibration.model_dump_json(),
        word_count=word_count(tokens),
        translation=translation,
        created_at=datetime.now(timezone.utc),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def save_authored_passage(
    db: Session,
    *,
    language: str,
    level: str,
    topic: str,
    genre: str | None,
    title: str,
    text: str,
    translation: str | None = None,
) -> PassageRow:
    tokens, result = _analyze_and_validate(text, level, language, use_llm_gloss=False)
    warnings: list[str] = []
    if not result.passed:
        warnings.append("Library text still has out-of-level flags.")
    calibration = result.to_calibration(attempts=1, warnings=warnings)
    return _persist(
        db,
        language=language,
        level=level,
        topic=topic,
        genre=genre,
        title=title,
        text=text,
        tokens=tokens,
        calibration=calibration,
        translation=translation,
    )


def _analyze_and_validate(
    text: str,
    level: str,
    language: str,
    use_llm_gloss: bool,
) -> tuple[list[Token], ValidationResult]:
    tokens = analyze_text(text, language)
    tokens = attach_glosses(tokens, use_llm=use_llm_gloss, language=language)
    result = validate_tokens(tokens, level, language)
    return tokens, result


def generate_passage(
    db: Session,
    level: str,
    topic: str,
    genre: str | None = None,
    language: str = "ru",
) -> PassageResponse:
    title, text = generate_passage_text(level, topic, genre, language=language)
    tokens, result = _analyze_and_validate(text, level, language, use_llm_gloss=True)

    attempts = 1
    warnings: list[str] = []

    if not result.passed:
        logger.info("First draft failed calibration: %s", result.flags[:8])
        try:
            title2, text2 = generate_passage_text(
                level, topic, genre, correction_flags=result.flags, language=language
            )
            tokens2, result2 = _analyze_and_validate(
                text2, level, language, use_llm_gloss=True
            )
            attempts = 2
            if result2.severity <= result.severity:
                title, text, tokens, result = title2, text2, tokens2, result2
            else:
                warnings.append(
                    "Corrective rewrite was not closer to level; kept the first draft."
                )
        except Exception:
            logger.exception("Corrective regeneration failed")
            warnings.append("Corrective rewrite failed; returning the first draft.")

    if not result.passed:
        warnings.append(
            "Passage still has out-of-level structures. Read the flags; this is a soft-fail."
        )

    calibration = result.to_calibration(attempts=attempts, warnings=warnings)
    translation = translate_passage(text, language)
    row = _persist(
        db,
        language=language,
        level=level,
        topic=topic,
        genre=genre,
        title=title,
        text=text,
        tokens=tokens,
        calibration=calibration,
        translation=translation,
    )
    return _to_response(row)


def ensure_translation(db: Session, passage_id: str) -> str | None:
    row = db.get(PassageRow, passage_id)
    if row is None:
        return None
    existing = getattr(row, "translation", None)
    if existing:
        return existing
    translation = translate_passage(row.text, row.language or "ru")
    if translation:
        row.translation = translation
        db.commit()
    return translation


def get_passage(db: Session, passage_id: str) -> PassageResponse | None:
    row = db.get(PassageRow, passage_id)
    if row is None:
        return None
    return _to_response(row)


def save_feedback(db: Session, passage_id: str, rating: FeedbackRating) -> bool:
    if db.get(PassageRow, passage_id) is None:
        return False
    db.add(FeedbackRow(passage_id=passage_id, rating=rating))
    db.commit()
    return True


def complete_read(
    db: Session,
    passage_id: str,
    rating: FeedbackRating,
    device_id: str | None,
) -> dict | None:
    row = db.get(PassageRow, passage_id)
    if row is None:
        return None
    db.add(FeedbackRow(passage_id=passage_id, rating=rating))
    result: dict = {
        "ok": True,
        "passage_id": passage_id,
        "rating": rating,
        "placement": None,
        "next_id": None,
        "new_lemmas": 0,
        "recycled_lemmas": 0,
    }
    if device_id:
        from app.services.learner import (
            bump_level,
            get_or_create_learner,
            ingest_passage,
            lemma_token_stats,
            pick_next_id,
            read_ids,
            seen_lemmas,
            tokens_from_row,
        )

        language = row.language or "ru"
        learner = get_or_create_learner(db, device_id, language)
        tokens = tokens_from_row(row)
        seen = seen_lemmas(db, device_id, language)
        new, recycled = lemma_token_stats(tokens, language, seen)
        ingest_passage(db, device_id, language, passage_id, tokens)
        learner.level = bump_level(learner.level, rating)
        already = read_ids(db, device_id)
        already.add(passage_id)
        next_id = pick_next_id(
            db, language, learner.level, already, exclude_id=passage_id
        )
        result.update(
            placement=learner.level,
            next_id=next_id,
            new_lemmas=new,
            recycled_lemmas=recycled,
        )
    db.commit()
    return result
