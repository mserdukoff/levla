from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.db import GenerateQuotaRow
from app.services.identity import Identity


def remaining_generates(db: Session, identity: Identity) -> int:
    key = identity.account_key
    if not key:
        return 0
    month = datetime.now(timezone.utc).strftime("%Y-%m")
    row = (
        db.query(GenerateQuotaRow)
        .filter(
            GenerateQuotaRow.account_key == key,
            GenerateQuotaRow.year_month == month,
        )
        .one_or_none()
    )
    used = row.count if row else 0
    return max(0, settings.generate_monthly_cap - used)


def consume_generate(db: Session, identity: Identity) -> None:
    key = identity.account_key
    if not key:
        raise HTTPException(
            status_code=401,
            detail="Sign in to generate a custom passage.",
        )
    month = datetime.now(timezone.utc).strftime("%Y-%m")
    row = (
        db.query(GenerateQuotaRow)
        .filter(
            GenerateQuotaRow.account_key == key,
            GenerateQuotaRow.year_month == month,
        )
        .one_or_none()
    )
    if row is None:
        row = GenerateQuotaRow(account_key=key, year_month=month, count=0)
        db.add(row)
        db.flush()
    if row.count >= settings.generate_monthly_cap:
        raise HTTPException(
            status_code=429,
            detail="Monthly custom-passage limit reached. Read from the catalog, or try next month.",
        )
    row.count += 1
    db.commit()
