from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Fantasy Soccer"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 1 week
    database_url: str = "sqlite:///./fantasy_soccer.db"
    fbref_base_url: str = "https://fbref.com/en"
    # Budget each manager gets to build their squad (in millions)
    squad_budget: float = 100.0
    squad_size: int = 15
    # Starting XI size
    starting_xi: int = 11

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
