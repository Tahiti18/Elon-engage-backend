from pydantic import BaseModel
import os

class Settings(BaseModel):
    TWITTERAPI_IO_KEY: str | None = os.getenv("TWITTERAPI_IO_KEY")
    DATABASE_URL: str | None = os.getenv("DATABASE_URL")
    DEFAULT_TIMEZONE: str = os.getenv("DEFAULT_TIMEZONE", "Asia/Nicosia")
    APP_ENV: str = os.getenv("APP_ENV", "production")
    OPENROUTER_API_KEY: str | None = os.getenv("OPENROUTER_API_KEY")
    WORKERS: int = int(os.getenv("WORKERS", "2"))
    # TEMPORARY: confirm from twitterapi.io docs
    TWITTERAPI_BASE_URL: str = os.getenv("TWITTERAPI_BASE_URL", "https://api.twitterapi.io")

settings = Settings()
