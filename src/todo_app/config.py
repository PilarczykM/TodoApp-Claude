from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    database_url: str
    debug: bool = False
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
