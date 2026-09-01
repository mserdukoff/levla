from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.db import PassageRow
from app.models.schemas import LibraryItem, LibraryResponse
from app.services.learner import (
    DEFAULT_LEVEL,
    calibration_passed,
    get_learner,
    lemma_token_stats,
    list_stars,
    pick_next_id,
    read_ids,
    seen_lemmas,
    tokens_from_row,
)


def list_library(
    db: Session,
    language: str,
    device_id: str | None,
) -> LibraryResponse:
    rows = (
        db.query(PassageRow)
        .filter(PassageRow.language == language)
        .order_by(PassageRow.created_at.desc())
        .all()
    )
    placement = DEFAULT_LEVEL
    seen: set[str] = set()
    already_read: set[str] = set()
    if device_id:
        learner = get_learner(db, device_id, language)
        if learner is not None:
            placement = learner.level
        seen = seen_lemmas(db, device_id, language)
        already_read = read_ids(db, device_id)

    next_id = pick_next_id(db, language, placement, already_read)
    items: list[LibraryItem] = []
    for row in rows:
        tokens = tokens_from_row(row)
        new, recycled = lemma_token_stats(tokens, language, seen)
        items.append(
            LibraryItem(
                id=row.id,
                language=row.language,  # type: ignore[arg-type]
                level=row.level,  # type: ignore[arg-type]
                topic=row.topic,
                genre=row.genre,
                title=row.title,
                word_count=row.word_count,
                created_at=row.created_at,
                passed=calibration_passed(row),
                read=row.id in already_read,
                recommended=row.id == next_id,
                new_lemmas=new,
                recycled_lemmas=recycled,
            )
        )
    items.sort(
        key=lambda it: (
            0 if it.recommended else 1,
            0 if not it.read else 1,
            it.level,
            -it.created_at.timestamp() if it.created_at else 0,
        )
    )
    return LibraryResponse(
        language=language,  # type: ignore[arg-type]
        placement=placement,  # type: ignore[arg-type]
        next_id=next_id,
        seen_lemmas=len(seen),
        items=items,
        words=list_stars(db, device_id, language) if device_id else [],
    )
