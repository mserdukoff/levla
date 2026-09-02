from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.db import TrialEventRow
from app.services.identity import Identity


def record_event(
    db: Session,
    *,
    kind: str,
    identity: Identity | None = None,
    passage_id: str | None = None,
    payload: dict | None = None,
    commit: bool = True,
) -> TrialEventRow:
    row = TrialEventRow(
        kind=kind,
        device_id=identity.device_id if identity else None,
        user_id=identity.user_id if identity else None,
        passage_id=passage_id,
        payload_json=json.dumps(payload, ensure_ascii=False) if payload else None,
        created_at=datetime.now(timezone.utc),
    )
    db.add(row)
    if commit:
        db.commit()
    return row


def trial_metrics(db: Session, days: int = 30) -> dict:
    from datetime import timedelta

    from app.models.db import FeedbackRow, LearnerReadRow

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    reads = (
        db.query(LearnerReadRow)
        .filter(LearnerReadRow.created_at >= cutoff)
        .all()
    )
    by_account: dict[str, set[str]] = {}
    for row in reads:
        key = f"user:{row.user_id}" if row.user_id else f"device:{row.device_id}"
        by_account.setdefault(key, set()).add(row.passage_id)
    learners = len(by_account)
    second = sum(1 for ids in by_account.values() if len(ids) >= 2)
    second_rate = round(second / learners, 3) if learners else 0.0

    feedback = (
        db.query(FeedbackRow)
        .filter(FeedbackRow.created_at >= cutoff)
        .all()
    )
    on_level_hard = 0
    on_level_total = 0
    from app.models.db import PassageRow

    for fb in feedback:
        passage = db.get(PassageRow, fb.passage_id)
        if passage is None:
            continue
        on_level_total += 1
        if fb.rating == "too_hard":
            on_level_hard += 1
    too_hard_rate = round(on_level_hard / on_level_total, 3) if on_level_total else 0.0

    wtp = (
        db.query(TrialEventRow)
        .filter(
            TrialEventRow.created_at >= cutoff,
            TrialEventRow.kind.in_(("wtp", "pay_intent", "want_more_generates")),
        )
        .count()
    )
    return {
        "window_days": days,
        "learners_with_reads": learners,
        "second_text_completion": second_rate,
        "second_text_pass": second_rate >= 0.4,
        "too_hard_rate": too_hard_rate,
        "calibration_trust_pass": too_hard_rate < 0.15,
        "unsolicited_wtp": wtp,
        "wtp_pass": wtp >= 5,
        "go": second_rate >= 0.4 and too_hard_rate < 0.15 and wtp >= 5,
    }
