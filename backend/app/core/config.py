from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openrouter_api_key: str = ""
    llm_model: str = "openai/gpt-4o-mini"
    database_url: str = f"sqlite:///{BACKEND_DIR / 'levla.db'}"
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def data_dir(self) -> Path:
        return PROJECT_ROOT / "data"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
