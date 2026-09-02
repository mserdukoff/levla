from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.db import (
    SHELF_PUBLIC,
    SHELF_QUARANTINE,
    FeedbackRow,
    PassageRow,
)
from app.models.schemas import (
    AudioCue,
    Calibration,
    ComprehensionQuestion,
    FeedbackRating,
    PassageResponse,
    Token,
)
from app.services.gloss import attach_glosses, resolve_gloss
from app.services.identity import Identity
from app.services.llm import generate_passage_text, translate_passage
from app.services.morph import analyze_text, word_count
from app.services.passport import attach_passport
from app.services.sentences import english_aligned
from app.services.validator import ValidationResult, validate_tokens

logger = logging.getLogger(__name__)


def public_passage_filter():
    return PassageRow.shelf_status == SHELF_PUBLIC


def is_public_row(row: PassageRow) -> bool:
    status = getattr(row, "shelf_status", None) or SHELF_PUBLIC
    if status == SHELF_QUARANTINE:
        return False
    from app.services.learner import calibration_passed

    return calibration_passed(row)


def _parse_cues(raw: str | None) -> list[AudioCue]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return [AudioCue.model_validate(item) for item in data]


def _parse_comprehension(raw: str | None) -> list[ComprehensionQuestion]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return [ComprehensionQuestion.model_validate(item) for item in data]


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
    for tok in tokens:
        if tok.is_word and tok.lemma and not tok.gloss:
            # Re-analyze rather than trust tok.morph: it's frozen from
            # whenever this passage was generated, so an older row can carry
            # a pos_detail from before a tagging fix. A fresh analysis picks
            # up the current rules, same as the kanji breakdown above.
            tok.gloss = resolve_gloss(tok.lemma, language)
    calibration = Calibration.model_validate(json.loads(row.calibration_json))
    attach_passport(calibration, language=language, level=row.level, tokens=tokens)
    created = row.created_at
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    audio_url = getattr(row, "audio_url", None)
    return PassageResponse(
        id=row.id,
        language=language,  # type: ignore[arg-type]
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
        shelf_status=getattr(row, "shelf_status", None) or SHELF_PUBLIC,
        audio_url=audio_url,
        audio_cues=_parse_cues(getattr(row, "audio_cues_json", None)),
        series_id=getattr(row, "series_id", None),
        chapter_index=getattr(row, "chapter_index", None),
        comprehension=_parse_comprehension(getattr(row, "comprehension_json", None)),
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
    shelf_status: str | None = None,
    series_id: str | None = None,
    chapter_index: int | None = None,
    topic_hash: str | None = None,
    comprehension_json: str | None = None,
) -> PassageRow:
    if shelf_status is None:
        shelf_status = SHELF_PUBLIC if calibration.passed else SHELF_QUARANTINE
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
        shelf_status=shelf_status,
        series_id=series_id,
        chapter_index=chapter_index,
        topic_hash=topic_hash,
        comprehension_json=comprehension_json,
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
    series_id: str | None = None,
    chapter_index: int | None = None,
    force_public: bool = False,
) -> PassageRow:
    tokens, result = _analyze_and_validate(text, level, language, use_llm_gloss=False)
    warnings: list[str] = []
    if not result.passed:
        warnings.append("Library text still has out-of-level flags.")
    calibration = result.to_calibration(attempts=1, warnings=warnings)
    attach_passport(calibration, language=language, level=level, tokens=tokens)
    if force_public:
        status = SHELF_PUBLIC
    else:
        status = SHELF_PUBLIC if result.passed else SHELF_QUARANTINE
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
        shelf_status=status,
        series_id=series_id,
        chapter_index=chapter_index,
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
    known_lemmas: list[str] | None = None,
) -> PassageResponse:
    import hashlib

    topic_hash = hashlib.sha256(
        f"{language}|{level}|{topic.strip().lower()}|{genre or ''}".encode()
    ).hexdigest()
    cached = (
        db.query(PassageRow)
        .filter(
            PassageRow.topic_hash == topic_hash,
            PassageRow.shelf_status == SHELF_PUBLIC,
        )
        .order_by(PassageRow.created_at.desc())
        .first()
    )
    if cached is not None:
        return _to_response(cached)

    title, text, translation = generate_passage_text(
        level, topic, genre, language=language, known_lemmas=known_lemmas
    )
    tokens, result = _analyze_and_validate(text, level, language, use_llm_gloss=True)

    attempts = 1
    warnings: list[str] = []

    if not result.passed:
        logger.info("First draft failed calibration: %s", result.flags[:8])
        try:
            title2, text2, translation2 = generate_passage_text(
                level,
                topic,
                genre,
                correction_flags=result.flags,
                language=language,
                known_lemmas=known_lemmas,
            )
            tokens2, result2 = _analyze_and_validate(
                text2, level, language, use_llm_gloss=True
            )
            attempts = 2
            if result2.severity <= result.severity:
                title, text, tokens, result = title2, text2, tokens2, result2
                translation = translation2
            else:
                warnings.append(
                    "Corrective rewrite was not closer to level; kept the first draft."
                )
        except Exception:
            logger.exception("Corrective regeneration failed")
            warnings.append("Corrective rewrite failed; returning the first draft.")

    calibration = result.to_calibration(attempts=attempts, warnings=warnings)
    attach_passport(calibration, language=language, level=level, tokens=tokens)
    if result.passed and not english_aligned(text, translation, language):
        aligned = translate_passage(text, language)
        if aligned:
            translation = aligned
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
        topic_hash=topic_hash,
    )
    if not result.passed:
        logger.info("Quarantined failed draft %s (%s %s)", row.id, language, level)
    return _to_response(row)


def ensure_translation(db: Session, passage_id: str) -> str | None:
    row = db.get(PassageRow, passage_id)
    if row is None:
        return None
    existing = getattr(row, "translation", None)
    language = row.language or "ru"
    if english_aligned(row.text, existing, language):
        return existing
    translation = translate_passage(row.text, language)
    if translation:
        row.translation = translation
        db.commit()
        return translation
    return existing


def get_passage(
    db: Session,
    passage_id: str,
    *,
    include_quarantine: bool = False,
) -> PassageResponse | None:
    row = db.get(PassageRow, passage_id)
    if row is None:
        return None
    if not include_quarantine and not is_public_row(row):
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
    identity: Identity | None = None,
    device_id: str | None = None,
) -> dict | None:
    row = db.get(PassageRow, passage_id)
    if row is None:
        return None
    if identity is None:
        identity = Identity(user_id=None, device_id=device_id)
    elif isinstance(identity, str):
        identity = Identity(user_id=None, device_id=identity)
    db.add(
        FeedbackRow(
            passage_id=passage_id,
            rating=rating,
            device_id=identity.device_id,
            user_id=identity.user_id,
        )
    )
    result: dict = {
        "ok": True,
        "passage_id": passage_id,
        "rating": rating,
        "placement": None,
        "next_id": None,
        "new_lemmas": 0,
        "recycled_lemmas": 0,
    }
    if identity.can_persist:
        from app.services.learner import (
            apply_placement,
            get_or_create_learner,
            ingest_passage,
            lemma_token_stats,
            pick_next_id,
            read_ids,
            seen_lemmas,
            tokens_from_row,
        )
        from app.services.trial import record_event

        language = row.language or "ru"
        learner = get_or_create_learner(db, identity, language)
        tokens = tokens_from_row(row)
        seen = seen_lemmas(db, identity, language)
        new, recycled = lemma_token_stats(tokens, language, seen)
        ingest_passage(db, identity, language, passage_id, tokens)
        apply_placement(learner, rating)
        already = read_ids(db, identity)
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
        record_event(
            db,
            kind="read_complete",
            identity=identity,
            passage_id=passage_id,
            payload={"rating": rating, "level": row.level},
            commit=False,
        )
    db.commit()
    return result
