from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "inpa-data-bridge"
    app_env: str = "dev"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"

    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/inpa"
    )

    inpa_base_url: str = "https://portale.inpa.gov.it"
    inpa_search_path: str = "/concorsi-smart/api/concorso-public-area/search-better"
    inpa_page_size: int = 50
    inpa_timeout_seconds: int = 30
    user_agent: str = "inpa-data-bridge/0.1.0"

    sync_enabled: bool = True
    sync_cron: str = "*/15 * * * *"
    sync_max_pages_per_run: int = 5


@lru_cache
def get_settings() -> Settings:
    return Settings()
