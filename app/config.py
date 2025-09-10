from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    TWITTERAPI_IO_KEY: str
    DATABASE_URL: str
    TWITTERAPI_IO_BASE_URL: str = "https://api.twitterapi.io"
    TWITTERAPI_IO_USER_TWEETS_PATH: str = "/v2/user/tweets"
    DEFAULT_TIMEZONE: str = "Asia/Nicosia"
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
