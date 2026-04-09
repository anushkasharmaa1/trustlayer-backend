"""
config.py
---------
Central configuration loaded from environment variables or a .env file.
All sensitive values (API keys, DB URLs) live here — never hardcoded elsewhere.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # --- API Security ---
    api_key: str = "trustlayer-dev-key-change-in-production"

    # --- Database ---
    # Set DATABASE_URL to a real PostgreSQL DSN to enable persistent storage.
    # If left empty the system falls back to in-memory storage automatically.
    database_url: str = ""

    # --- App Meta ---
    app_name: str = "TrustLayer"
    app_version: str = "1.0.0"
    debug: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache()
def get_settings() -> Settings:
    """Return a cached singleton of Settings."""
    return Settings()
