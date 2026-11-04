from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    bot_token: SecretStr = Field(alias="BOT_TOKEN")
    owner_id: int = Field(alias="OWNER_ID", gt=0)
    database_url: str = Field(alias="DATABASE_URL")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @property
    def async_database_url(self) -> str:
        url = self.database_url.strip()
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+asyncpg://", 1)
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()
