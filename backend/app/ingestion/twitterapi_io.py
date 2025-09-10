# app/clients/twitterapi_io.py
#
# Robust TwitterAPI.io client:
# - async (matches our FastAPI usage)
# - tries multiple auth header formats (Bearer, X-API-Key, raw Authorization)
# - uses our existing env names TWITTERAPI_IO_BASE_URL and TWITTERAPI_IO_USER_TWEETS_PATH
# - clear errors if upstream rejects the key

from typing import Any, Dict
import httpx
from app.config import settings

class TwitterApiIoClient:
    def __init__(self, api_key: str | None = None, base_url: str | None = None, path: str | None = None):
        self.api_key = (api_key or settings.TWITTERAPI_IO_KEY or "").strip()
        if not self.api_key:
            raise ValueError("TWITTERAPI_IO_KEY is missing")
        self.base_url = (base_url or settings.TWITTERAPI_IO_BASE_URL).rstrip("/")
        self.user_tweets_path = (path or settings.TWITTERAPI_IO_USER_TWEETS_PATH)
        # e.g. base_url = https://api.twitterapi.io
        #      path     = /v2/user/tweets  (adjust via env if provider changed)

    async def _get(self, url: str, params: Dict[str, Any]) -> httpx.Response:
        # Try common auth header patterns used by providers that change formats
        header_sets = [
            {"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"},
            {"X-API-Key": self.api_key, "Accept": "application/json"},
            {"Authorization": self.api_key, "Accept": "application/json"},  # raw key fallback
        ]
        async with httpx.AsyncClient(timeout=60) as client:
            last_exc: Exception | None = None
            for headers in header_sets:
                try:
                    r = await client.get(url, params=params, headers=headers)
                    # If unauthorized, try next header style
                    if r.status_code == 401:
                        last_exc = httpx.HTTPStatusError("401 Unauthorized", request=r.request, response=r)
                        continue
                    r.raise_for_status()
                    return r
                except httpx.HTTPStatusError as e:
                    # For 4xx (except 401 handled above) or 5xx, bubble up the first meaningful one
                    last_exc = e
                    if r.status_code in (400, 403, 404, 429, 500, 502, 503):
                        break
                except Exception as e:
                    last_exc = e
            # If we’re here, all header styles failed
            if last_exc:
                raise last_exc
            raise RuntimeError("Unknown upstream error contacting TwitterAPI.io")

    async def fetch_user_tweets(self, username: str, limit: int = 200) -> Dict[str, Any]:
        """
        Returns provider JSON payload.
        The endpoint path is fully configurable via env:
        - TWITTERAPI_IO_BASE_URL (e.g., https://api.twitterapi.io)
        - TWITTERAPI_IO_USER_TWEETS_PATH (e.g., /v2/user/tweets)
        Query params: username, limit
        """
        url = f"{self.base_url}{self.user_tweets_path}"
        params = {"username": username, "limit": str(limit)}
        resp = await self._get(url, params=params)
        return resp.json()
