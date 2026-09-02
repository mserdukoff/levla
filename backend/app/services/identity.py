from __future__ import annotations

import re
from dataclasses import dataclass

from fastapi import Header, Request
from sqlalchemy.orm import Session

from app.models.db import (
    LearnerCardRow,
    LearnerLemmaRow,
    LearnerReadRow,
    LearnerRow,
    LearnerStarRow,
)

_DEVICE = re.compile(r"^[A-Za-z0-9_-]{8,64}$")


def valid_device_id(device_id: str | None) -> str | None:
    if not device_id:
        return None
    value = device_id.strip()
    if _DEVICE.match(value):
        return value
    return None


@dataclass
class Identity:
    user_id: int | None
    device_id: str | None

    @property
    def account_key(self) -> str | None:
        if self.user_id is not None:
            return f"user:{self.user_id}"
        if self.device_id:
            return f"device:{self.device_id}"
        return None

    @property
    def can_persist(self) -> bool:
        return bool(self.user_id or self.device_id)


def identity_from_request(
    request: Request,
    x_device_id: str | None = Header(default=None),
) -> Identity:
    user_id = getattr(request.state, "user_id", None)
    return Identity(user_id=user_id, device_id=valid_device_id(x_device_id))


def apply_owner_filter(query, model, identity: Identity):
    if identity.user_id is not None:
        return query.filter(model.user_id == identity.user_id)
    if identity.device_id:
        return query.filter(model.device_id == identity.device_id)
    return query.filter(False)


def merge_guest_into_user(db: Session, device_id: str, user_id: int) -> None:
    if not device_id:
        return
    for model in (
        LearnerRow,
        LearnerLemmaRow,
        LearnerStarRow,
        LearnerReadRow,
        LearnerCardRow,
    ):
        rows = db.query(model).filter(model.device_id == device_id).all()
        for row in rows:
            if getattr(row, "user_id", None) is None:
                row.user_id = user_id
    db.commit()
