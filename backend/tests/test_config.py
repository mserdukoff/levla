from app.core.config import normalize_database_url


def test_postgres_url_from_rds():
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
