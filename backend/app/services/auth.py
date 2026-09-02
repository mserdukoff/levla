from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import jwt
from fastapi import HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.db import MagicLinkRow, UserRow
from app.services.identity import merge_guest_into_user, valid_device_id

logger = logging.getLogger(__name__)

GOOGLE_AUTH = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO = "https://openidconnect.googleapis.com/v1/userinfo"


def issue_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(days=30),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_token(token: str) -> int | None:
    try:
        data = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return int(data["sub"])
    except Exception:
        return None


def set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        settings.auth_cookie_name,
        token,
        httponly=True,
        samesite="lax",
        max_age=30 * 24 * 3600,
        path="/",
    )


def clear_auth_cookie(response: Response) -> None:
    response.delete_cookie(settings.auth_cookie_name, path="/")


def user_id_from_request(request: Request) -> int | None:
    token = request.cookies.get(settings.auth_cookie_name)
    if not token:
        auth = request.headers.get("Authorization") or ""
        if auth.lower().startswith("bearer "):
            token = auth[7:].strip()
    if not token:
        return None
    return decode_token(token)


def get_or_create_email_user(db: Session, email: str, display_name: str | None = None) -> UserRow:
    email = email.strip().lower()
    row = db.query(UserRow).filter(UserRow.email == email).one_or_none()
    if row is None:
        row = UserRow(email=email, display_name=display_name or email.split("@")[0])
        db.add(row)
        db.commit()
        db.refresh(row)
    return row


def get_or_create_google_user(
    db: Session, sub: str, email: str | None, name: str | None
) -> UserRow:
    row = db.query(UserRow).filter(UserRow.google_sub == sub).one_or_none()
    if row is None and email:
        row = db.query(UserRow).filter(UserRow.email == email.lower()).one_or_none()
        if row is not None:
            row.google_sub = sub
    if row is None:
        row = UserRow(
            google_sub=sub,
            email=email.lower() if email else None,
            display_name=name,
        )
        db.add(row)
    db.commit()
    db.refresh(row)
    return row


def finish_login(
    db: Session, response: Response, user: UserRow, device_id: str | None
) -> None:
    if device_id:
        merge_guest_into_user(db, device_id, user.id)
    set_auth_cookie(response, issue_token(user.id))


def google_authorize_url(state: str) -> str:
    if not settings.google_client_id:
        raise HTTPException(status_code=503, detail="Google sign-in is not configured.")
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": f"{settings.public_base_url}/api/auth/google/callback",
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "online",
        "prompt": "select_account",
    }
    return f"{GOOGLE_AUTH}?{urlencode(params)}"


def exchange_google_code(code: str) -> dict:
    import httpx

    with httpx.Client(timeout=20) as client:
        token_res = client.post(
            GOOGLE_TOKEN,
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": f"{settings.public_base_url}/api/auth/google/callback",
                "grant_type": "authorization_code",
            },
        )
        token_res.raise_for_status()
        access = token_res.json().get("access_token")
        info = client.get(
            GOOGLE_USERINFO, headers={"Authorization": f"Bearer {access}"}
        )
        info.raise_for_status()
        return info.json()


def create_magic_link(db: Session, email: str) -> str:
    token = uuid.uuid4().hex
    row = MagicLinkRow(
        email=email.strip().lower(),
        token=token,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=2),
        used=False,
    )
    db.add(row)
    db.commit()
    link = f"{settings.public_base_url}/api/auth/magic/callback?token={token}"
    if settings.smtp_url:
        logger.info("Magic link for %s: %s", email, link)
    else:
        logger.info("Magic link (no SMTP) for %s: %s", email, link)
    return link


def consume_magic_link(db: Session, token: str) -> UserRow:
    row = db.query(MagicLinkRow).filter(MagicLinkRow.token == token).one_or_none()
    if row is None or row.used:
        raise HTTPException(status_code=400, detail="This sign-in link is invalid.")
    if row.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="This sign-in link has expired.")
    row.used = True
    user = get_or_create_email_user(db, row.email)
    db.commit()
    return user
