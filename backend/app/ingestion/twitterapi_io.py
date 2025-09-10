# app/clients/twitterapi_io.py
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

    async def _try(self, url: str, params: Dict[str, Any], headers: Dict[str, str]) -> httpx.Response:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.get(url, params=params, headers=headers)
            r.raise_for_status()
            return r

    async def _get(self, url: str, params: Dict[str, Any]) -> httpx.Response:
        trials = [
            {"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"},
            {"Authorization": self.api_key, "Accept": "application/json"},              # raw key
            {"X-API-Key": self.api_key, "Accept": "application/json"},
            {"Api-Key": self.api_key, "Accept": "application/json"},
            {"ApiKey": self.api_key, "Accept": "application/json"},
        ]
        last_err: Exception | None = None
        # Header trials
        for h in trials:
            try:
                return await self._try(url, params, h)
            except httpx.HTTPStatusError as e:
                if e.response is not None and e.response.status_code == 401:
                    last_err = e
                    continue
                last_err = e
                break
            except Exception as e:
                last_err = e
                break
        # Final fallback: pass as query param
        qp = dict(params)
        qp["api_key"] = self.api_key
        try:
            return await self._try(url, qp, {"Accept": "application/json"})
        except Exception as e:
            raise last_err or e

    async def fetch_user_tweets(self, username: str, limit: int = 200) -> Dict[str, Any]:
        url = f"{self.base_url}{self.user_tweets_path}"
        params = {"username": username, "limit": str(limit)}
        resp = await self._get(url, params)
        return resp.json()
