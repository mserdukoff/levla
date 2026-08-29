from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.db import LearnerLemmaRow, LearnerReadRow, LearnerRow, PassageRow
from app.models.schemas import Token
from app.services.validator import CONTENT_POS as RU_CONTENT
from app.services.validator_ja import CONTENT_POS as JA_CONTENT

LEVELS = ("A1", "A2", "B1", "B2")
DEFAULT_LEVEL = "A2"
_DEVICE = re.compile(r"^[A-Za-z0-9_-]{8,64}$")


def valid_device_id(device_id: str | None) -> str | None:
    if not device_id:
        return None
    value = device_id.strip()
    if _DEVICE.match(value):
        return value
    return None


def content_tokens(tokens: list[Token], language: str) -> list[Token]:
    allowed = JA_CONTENT if language == "ja" else RU_CONTENT
    out: list[Token] = []
    for tok in tokens:
        if not tok.is_word or not tok.lemma or not tok.morph:
            continue
        if tok.morph.pos in allowed:
            out.append(tok)
    return out


def unique_content_lemmas(tokens: list[Token], language: str) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for tok in content_tokens(tokens, language):
        lemma = tok.lemma or ""
        if lemma and lemma not in seen:
            seen.add(lemma)
            ordered.append(lemma)
    return ordered


def lemma_token_stats(
    tokens: list[Token],
    language: str,
    seen: set[str],
) -> tuple[int, int]:
    """Count content-word tokens as new vs already seen (not unique lemmas)."""
    new = 0
    recycled = 0
    for tok in content_tokens(tokens, language):
        lemma = tok.lemma or ""
        if lemma in seen:
            recycled += 1
        else:
            new += 1
    return new, recycled


def tokens_from_row(row: PassageRow) -> list[Token]:
    return [Token.model_validate(t) for t in json.loads(row.tokens_json)]


def calibration_passed(row: PassageRow) -> bool:
    try:
        data = json.loads(row.calibration_json)
        return bool(data.get("passed"))
    except Exception:
        return False


def bump_level(level: str, rating: str) -> str:
    idx = LEVELS.index(level) if level in LEVELS else LEVELS.index(DEFAULT_LEVEL)
    if rating == "too_easy":
        idx = min(idx + 1, len(LEVELS) - 1)
    elif rating == "too_hard":
        idx = max(idx - 1, 0)
    return LEVELS[idx]


def get_learner(db: Session, device_id: str, language: str) -> LearnerRow | None:
    return (
        db.query(LearnerRow)
        .filter(LearnerRow.device_id == device_id, LearnerRow.language == language)
        .one_or_none()
    )


def get_or_create_learner(db: Session, device_id: str, language: str) -> LearnerRow:
    row = get_learner(db, device_id, language)
    if row is not None:
        return row
    row = LearnerRow(
        device_id=device_id,
        language=language,
        level=DEFAULT_LEVEL,
        updated_at=datetime.now(timezone.utc),
    )
    db.add(row)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        row = get_learner(db, device_id, language)
        if row is None:
            raise
    return row


def seen_lemmas(db: Session, device_id: str, language: str) -> set[str]:
    rows = (
        db.query(LearnerLemmaRow.lemma)
        .filter(
            LearnerLemmaRow.device_id == device_id,
            LearnerLemmaRow.language == language,
        )
        .all()
    )
    return {r[0] for r in rows}


def read_ids(db: Session, device_id: str) -> set[str]:
    rows = (
        db.query(LearnerReadRow.passage_id)
        .filter(LearnerReadRow.device_id == device_id)
        .all()
    )
    return {r[0] for r in rows}


def ingest_passage(
    db: Session,
    device_id: str,
    language: str,
    passage_id: str,
    tokens: list[Token],
) -> None:
    now = datetime.now(timezone.utc)
    existing = seen_lemmas(db, device_id, language)
    for lemma in unique_content_lemmas(tokens, language):
        if lemma in existing:
            continue
        db.add(
            LearnerLemmaRow(
                device_id=device_id,
                language=language,
                lemma=lemma,
                created_at=now,
            )
        )
        existing.add(lemma)
    already = (
        db.query(LearnerReadRow)
        .filter(
            LearnerReadRow.device_id == device_id,
            LearnerReadRow.passage_id == passage_id,
        )
        .one_or_none()
    )
    if already is None:
        db.add(
            LearnerReadRow(
                device_id=device_id,
                passage_id=passage_id,
                created_at=now,
            )
        )


def _level_priority(placement: str) -> list[str]:
    if placement not in LEVELS:
        placement = DEFAULT_LEVEL
    idx = LEVELS.index(placement)
    order = [placement]
    if idx + 1 < len(LEVELS):
        order.append(LEVELS[idx + 1])
    if idx - 1 >= 0:
        order.append(LEVELS[idx - 1])
    for lv in LEVELS:
        if lv not in order:
            order.append(lv)
    return order


def pick_next_id(
    db: Session,
    language: str,
    placement: str,
    already_read: set[str],
    exclude_id: str | None = None,
) -> str | None:
    rows = (
        db.query(PassageRow)
        .filter(PassageRow.language == language)
        .order_by(PassageRow.created_at.desc())
        .all()
    )
    if not rows:
        return None

    def score(row: PassageRow) -> tuple[int, int, float]:
        passed = 0 if calibration_passed(row) else 1
        created = row.created_at.timestamp() if row.created_at else 0.0
        return (passed, 0, -created)

    for level in _level_priority(placement):
        unread = [
            r
            for r in rows
            if r.level == level and r.id not in already_read and r.id != exclude_id
        ]
        if unread:
            unread.sort(key=score)
            return unread[0].id

    rest = [r for r in rows if r.id != exclude_id]
    if not rest:
        return rows[0].id
    rest.sort(key=score)
    return rest[0].id
