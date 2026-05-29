from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    github_token: str = ""
    openai_api_key: str = ""
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/merited"
    github_api_base: str = "https://api.github.com"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
