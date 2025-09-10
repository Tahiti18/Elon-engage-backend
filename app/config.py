# app/config.py  — force-read Railway env vars and fail clearly if empty
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Read directly from OS env (Railway Variables). Ignore any .env file.
    TWITTERAPI_IO_KEY: str = os.environ.get("TWITTERAPI_IO_KEY", "")
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "")
    TWITTERAPI_IO_BASE_URL: str = os.environ.get("TWITTERAPI_IO_BASE_URL", "https://api.twitterapi.io")
    TWITTERAPI_IO_USER_TWEETS_PATH: str = os.environ.get("TWITTERAPI_IO_USER_TWEETS_PATH", "/v2/user/tweets")
    DEFAULT_TIMEZONE: str = os.environ.get("DEFAULT_TIMEZONE", "Asia/Nicosia")
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")

    # Do NOT load from a .env file in production; Railway env must win.
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

settings = Settings()

# Hard guardrails with explicit messages if Railway didn't inject values:
if not settings.DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is empty. In Railway, set it as a **Reference** to Postgres.DATABASE_URL (no quotes)."
    )
if not settings.TWITTERAPI_IO_KEY:
    raise RuntimeError("TWITTERAPI_IO_KEY is empty.")
