# app/clients/twitterapi_io.py
# Corrects endpoint + auth per TwitterAPI.io docs.
# - Endpoint: /twitter/user/last_tweets
# - Auth: X-API-Key
# - Param: userName (case-sensitive)
# - Handles pagination to honor your limit.

from typing import Any, Dict, List
import httpx
from app.config import settings

class TwitterApiIoClient:
    def __init__(self):
        self.api_key = (settings.TWITTERAPI_IO_KEY or "").strip()
        if not self.api_key:
            raise ValueError("TWITTERAPI_IO_KEY is missing")
        self.base_url = (settings.TWITTERAPI_IO_BASE_URL or "https://api.twitterapi.io").rstrip("/")
        self.path = "/twitter/user/last_tweets"

    async def fetch_user_last_tweets(self, username: str, limit: int = 50, include_replies: bool = True) -> Dict[str, Any]:
        url = f"{self.base_url}{self.path}"
        headers = {
            "X-API-Key": self.api_key,     # REQUIRED by provider
            "Accept": "application/json",
        }

        tweets: List[Dict[str, Any]] = []
        cursor = ""
        # API returns up to 20 per page; we loop until we hit `limit` or run out.
        async with httpx.AsyncClient(timeout=60) as client:
            while len(tweets) < limit:
                params = {
                    "userName": username,           # case-sensitive per docs
                    "includeReplies": str(include_replies).lower(),
                }
                if cursor:
                    params["cursor"] = cursor

                r = await client.get(url, headers=headers, params=params)
                r.raise_for_status()
                payload = r.json()

                page = payload.get("tweets") or []
                tweets.extend(page)
                has_next = bool(payload.get("has_next_page"))
                cursor = payload.get("next_cursor") or ""

                if not has_next or not cursor:
                    break

        return {"tweets": tweets[:limit]}
