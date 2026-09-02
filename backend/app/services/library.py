from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.db import SHELF_PUBLIC, PassageRow
from app.models.schemas import LibraryItem, LibraryResponse
from app.services.identity import Identity
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
    identity: Identity | str | None,
) -> LibraryResponse:
    if isinstance(identity, str):
        identity = Identity(user_id=None, device_id=identity)
    rows = (
        db.query(PassageRow)
        .filter(
            PassageRow.language == language,
            PassageRow.shelf_status == SHELF_PUBLIC,
        )
        .order_by(PassageRow.created_at.desc())
        .all()
    )
    rows = [r for r in rows if calibration_passed(r)]
    placement = DEFAULT_LEVEL
    seen: set[str] = set()
    already_read: set[str] = set()
    words = []
    if identity and identity.can_persist:
        learner = get_learner(db, identity, language)
        if learner is not None:
            placement = learner.level
        seen = seen_lemmas(db, identity, language)
        already_read = read_ids(db, identity)
        words = list_stars(db, identity, language)

    next_id = pick_next_id(db, language, placement, already_read)
    items: list[LibraryItem] = []
    for row in rows:
        tokens = tokens_from_row(row)
        new, recycled = lemma_token_stats(tokens, language, seen)
        total = new + recycled
        pct = round(new / total, 3) if total else 0.0
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
                passed=True,
                read=row.id in already_read,
                recommended=row.id == next_id,
                new_lemmas=new,
                recycled_lemmas=recycled,
                series_id=getattr(row, "series_id", None),
                chapter_index=getattr(row, "chapter_index", None),
                has_audio=bool(getattr(row, "audio_url", None)),
                new_lemma_pct=pct,
            )
        )
    items.sort(
        key=lambda it: (
            0 if it.recommended else 1,
            0 if not it.read else 1,
            it.chapter_index if it.chapter_index is not None else 99,
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
        words=words,
    )
