from app.core.config import (
    apply_db_sslmode,
    is_supabase_url,
    is_transaction_pooler,
    normalize_database_url,
    resolve_sslmode,
)


def test_postgres_url_scheme():
    assert (
        normalize_database_url("postgres://u:p@db.example:5432/levla")
        == "postgresql+psycopg2://u:p@db.example:5432/levla"
    )


def test_postgresql_url_gets_driver():
    assert (
        normalize_database_url("postgresql://u:p@localhost/levla")
        == "postgresql+psycopg2://u:p@localhost/levla"
    )


def test_sqlite_url_unchanged():
    url = "sqlite:///./levla.db"
    assert normalize_database_url(url) == url


def test_already_driver_prefixed():
    url = "postgresql+psycopg2://u:p@localhost/levla"
    assert normalize_database_url(url) == url


def test_supabase_session_pooler_detected():
    url = (
        "postgresql+psycopg2://postgres.abc:pw@aws-0-us-east-1.pooler.supabase.com:5432/postgres"
    )
    assert is_supabase_url(url)
    assert not is_transaction_pooler(url)


def test_supabase_transaction_pooler_detected():
    url = (
        "postgresql://postgres.abc:pw@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
    )
    assert is_supabase_url(url)
    assert is_transaction_pooler(url)


def test_supabase_direct_host_detected():
    url = "postgresql://postgres:pw@db.abcdefghijkl.supabase.co:5432/postgres"
    assert is_supabase_url(url)
    assert not is_transaction_pooler(url)


def test_local_postgres_is_not_supabase():
    url = "postgresql+psycopg2://levla:levla@postgres:5432/levla"
    assert not is_supabase_url(url)
    assert not is_transaction_pooler(url)


def test_supabase_ssl_defaults_to_require():
    url = "postgresql+psycopg2://postgres:pw@db.abc.supabase.co:5432/postgres"
    assert resolve_sslmode(url, "") == "require"
    assert apply_db_sslmode(url, "require").endswith("?sslmode=require")


def test_explicit_sslmode_wins():
    url = "postgresql+psycopg2://postgres:pw@db.abc.supabase.co:5432/postgres"
    assert resolve_sslmode(url, "verify-full") == "verify-full"


def test_sslmode_not_duplicated():
    url = "postgresql+psycopg2://u:p@localhost/levla?sslmode=require"
    assert apply_db_sslmode(url, "require") == url
