# app/clients/twitterapi_io.py
# Uses TwitterAPI.io "last_tweets" endpoint with X-API-Key (post-incident behavior).
# Params: userName (case-sensitive), optional cursor. Paginates until limit.

from typing import Any, Dict, List
import httpx
from app.config import settings

class TwitterApiIoClient:
    def __init__(self):
        self.api_key = (settings.TWITTERAPI_IO_KEY or "").strip()
        if not self.api_key:
            raise ValueError("TWITTERAPI_IO_KEY is missing")

        # keep your env override, default to provider base
        self.base_url = (getattr(settings, "TWITTERAPI_IO_BASE_URL", "https://api.twitterapi.io") or "https://api.twitterapi.io").rstrip("/")
        # correct path for new keys
        self.path = "/twitter/user/last_tweets"

    async def fetch_user_last_tweets(self, username: str, limit: int = 50, include_replies: bool = True) -> Dict[str, Any]:
        url = f"{self.base_url}{self.path}"
        headers = {
            "X-API-Key": self.api_key,   # <-- critical; NOT Bearer
            "Accept": "application/json",
        }

        tweets: List[Dict[str, Any]] = []
        cursor = ""

        async with httpx.AsyncClient(timeout=60) as client:
            while len(tweets) < limit:
                params = {
                    "userName": username,                      # exact casing
                    "includeReplies": str(include_replies).lower(),
                }
                if cursor:
                    params["cursor"] = cursor

                r = await client.get(url, headers=headers, params=params)
                # If upstream rejects (e.g., 401), raise so our route returns 502 with the reason.
                r.raise_for_status()

                payload = r.json()
                page = payload.get("tweets") or []
                tweets.extend(page)

                has_next = payload.get("has_next_page")
                cursor = payload.get("next_cursor") or ""
                if not has_next or not cursor:
                    break

        # Keep the same shape your ingest expects
        return {"tweets": tweets[:limit]}
