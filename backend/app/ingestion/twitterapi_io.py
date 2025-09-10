# app/clients/twitterapi_io.py
# One clear auth style: TwitterAPI.io expects X-API-Key (post-incident keys).
# Uses your existing envs TWITTERAPI_IO_BASE_URL and TWITTERAPI_IO_USER_TWEETS_PATH.

from typing import Any, Dict
import httpx
from app.config import settings

class TwitterApiIoClient:
    def __init__(self):
        self.api_key = (settings.TWITTERAPI_IO_KEY or "").strip()
        if not self.api_key:
            raise ValueError("TWITTERAPI_IO_KEY is missing")
        self.base_url = (settings.TWITTERAPI_IO_BASE_URL or "https://api.twitterapi.io").rstrip("/")
        self.user_tweets_path = settings.TWITTERAPI_IO_USER_TWEETS_PATH or "/v2/user/tweets"

    async def fetch_user_tweets(self, username: str, limit: int = 200) -> Dict[str, Any]:
        url = f"{self.base_url}{self.user_tweets_path}"
        headers = {
            "X-API-Key": self.api_key,           # <— IMPORTANT: use X-API-Key
            "Accept": "application/json",
        }
        params = {"username": username, "limit": str(limit)}
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.get(url, params=params, headers=headers)
            r.raise_for_status()
            return r.json()
