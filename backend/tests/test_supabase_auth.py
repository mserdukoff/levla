import jwt

from app.core.config import Settings
from app.services.supabase_jwt import decode_supabase_claims


def test_infer_supabase_url_from_direct_host():
    s = Settings.model_construct(
        supabase_url="",
        database_url="postgresql+psycopg2://postgres:x@db.abcd.supabase.co:5432/postgres",
    )
    assert s.effective_supabase_url == "https://abcd.supabase.co"
    assert s.supabase_jwks_url.endswith("/auth/v1/.well-known/jwks.json")
    assert s.supabase_jwt_issuer == "https://abcd.supabase.co/auth/v1"


def test_explicit_supabase_url_wins():
    s = Settings.model_construct(
        supabase_url="https://explicit.supabase.co/",
        database_url="sqlite:///./levla.db",
    )
    assert s.effective_supabase_url == "https://explicit.supabase.co"


def test_hs256_is_not_a_supabase_access_token(monkeypatch):
    from app.core import config

    monkeypatch.setattr(
        config.settings, "supabase_url", "https://abcd.supabase.co"
    )
    token = jwt.encode(
        {"sub": "1", "role": "authenticated", "aud": "authenticated"},
        "secret",
        algorithm="HS256",
    )
    assert decode_supabase_claims(token) is None
