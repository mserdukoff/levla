"""Verify access tokens issued by Supabase Auth (asymmetric JWKS)."""

from __future__ import annotations

from functools import lru_cache
from uuid import UUID

import jwt
from jwt import PyJWKClient

from app.core.config import settings


@lru_cache(maxsize=4)
def _jwks_client(url: str) -> PyJWKClient:
    return PyJWKClient(url, cache_keys=True, lifespan=600)


def decode_supabase_claims(token: str) -> dict | None:
    jwks_url = settings.supabase_jwks_url
    if not jwks_url or token.count(".") != 2:
        return None
    try:
        alg = jwt.get_unverified_header(token).get("alg")
        if alg not in {"ES256", "RS256"}:
            return None
        key = _jwks_client(jwks_url).get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            key.key,
            algorithms=["ES256", "RS256"],
            audience="authenticated",
            issuer=settings.supabase_jwt_issuer,
            leeway=30,
        )
    except Exception:
        return None


def auth_id_from_claims(claims: dict) -> UUID | None:
    sub = claims.get("sub")
    if not sub:
        return None
    try:
        return UUID(str(sub))
    except ValueError:
        return None
