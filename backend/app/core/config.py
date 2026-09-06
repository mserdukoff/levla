from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent


def normalize_database_url(url: str) -> str:
    """RDS and Heroku-style URLs often start with postgres://."""
    if url.startswith("postgres://"):
        return "postgresql+psycopg2://" + url[len("postgres://") :]
    if url.startswith("postgresql://") and "+psycopg" not in url:
        return "postgresql+psycopg2://" + url[len("postgresql://") :]
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    app_env: str = "development"
    log_level: str = "info"
    openrouter_api_key: str = ""
    llm_model: str = "openai/gpt-4o-mini"
    database_url: str = f"sqlite:///{BACKEND_DIR / 'levla.db'}"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    jwt_secret: str = "dev-change-me"
    google_client_id: str = ""
    google_client_secret: str = ""
    public_base_url: str = "http://localhost:3000"
    azure_speech_key: str = ""
    azure_speech_region: str = ""
    azure_speech_voice: str = "ja-JP-NanamiNeural"
    audio_dir: str = ""
    show_russian: bool = False
    require_auth: bool = False
    generate_monthly_cap: int = 10
    auth_cookie_name: str = "levla_token"
    smtp_url: str = ""
    data_root: str = Field(default="", validation_alias="DATA_DIR")
    s3_audio_bucket: str = ""
    s3_audio_prefix: str = "audio/"
    aws_region: str = ""
    cookie_secure: bool | None = None
    cookie_samesite: str = "lax"
    cookie_domain: str = ""
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_sslmode: str = ""
    skip_seed: bool = False
    generate_workers: int = 2
    generate_max_pending: int = 3

    @field_validator("database_url", mode="before")
    @classmethod
    def _normalize_db_url(cls, value: object) -> object:
        if isinstance(value, str):
            return normalize_database_url(value)
        return value

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() in {"production", "prod"}

    @property
    def effective_cookie_secure(self) -> bool:
        if self.cookie_secure is not None:
            return self.cookie_secure
        return self.is_production

    @property
    def audio_path(self) -> Path:
        if self.audio_dir:
            return Path(self.audio_dir)
        return BACKEND_DIR / "audio"

    @property
    def data_dir(self) -> Path:
        if self.data_root:
            return Path(self.data_root)
        return PROJECT_ROOT / "data"

    @property
    def cors_origin_list(self) -> list[str]:
        origins = [o.strip() for o in self.cors_origins.split(",") if o.strip()]
        base = self.public_base_url.rstrip("/")
        if base and base not in origins:
            origins.append(base)
        return origins

    def sqlalchemy_url(self) -> str:
        url = self.database_url
        if self.db_sslmode and "sslmode=" not in url and url.startswith("postgresql"):
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}sslmode={self.db_sslmode}"
        return url


settings = Settings()
