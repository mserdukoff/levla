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

    @property
    def audio_path(self) -> Path:
        if self.audio_dir:
            return Path(self.audio_dir)
        return BACKEND_DIR / "audio"

    @property
    def data_dir(self) -> Path:
        return PROJECT_ROOT / "data"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
