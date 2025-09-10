from typing import Any, Dict, List
import httpx
from datetime import datetime
from ..config import settings
from ..features.emoji import extract_emojis

# TEMPORARY: confirm the exact endpoint paths from twitterapi.io docs for your plan.
# Assumed pattern:
# - GET {TWITTERAPI_BASE_URL}/v1/timeline/user?username=elonmusk&limit=100

class TwitterAPIIO:
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key or settings.TWITTERAPI_IO_KEY
        self.base_url = base_url or settings.TWITTERAPI_BASE_URL
        if not self.api_key:
            raise ValueError("TWITTERAPI_IO_KEY is missing")
        self.client = httpx.Client(timeout=30.0, headers={
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        })

    def fetch_user_timeline(self, username: str, limit: int = 100) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/v1/timeline/user"
        params = {"username": username, "limit": limit}
        r = self.client.get(url, params=params)
        r.raise_for_status()
        data = r.json()
        # EXPECTED format: adjust mapping below as needed based on actual payload.
        items = data.get("data") or data  # fallback if top-level is list
        if not isinstance(items, list):
            raise ValueError("Unexpected response structure from twitterapi.io")
        return items

    @staticmethod
    def normalize_tweet(raw: Dict[str, Any]) -> Dict[str, Any]:
        # Map common fields, adapt if your plan returns different names.
        tid = str(raw.get("id") or raw.get("tweet_id") or "")
        uid = str((raw.get("user") or {}).get("id") or raw.get("author_id") or "")
        text = raw.get("text") or ""
        created_at = raw.get("created_at") or raw.get("created")
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace("Z","+00:00"))
            except Exception:
                created_at = None
        ref_type = None
        if raw.get("referenced_tweets"):
            # e.g. [{"type":"retweeted","id":"..."}]
            ref = raw["referenced_tweets"][0]
            ref_type = ref.get("type")
        elif raw.get("is_retweet"):
            ref_type = "retweet"

        emojis = extract_emojis(text)
        has_links = "http" in text.lower()
        has_media = bool(raw.get("attachments") or raw.get("media"))

        return {
            "tweet_id": tid,
            "user_id": uid,
            "text": text,
            "created_at": created_at,
            "referenced_tweet_type": ref_type or ("original" if not raw.get("in_reply_to_status_id") else "reply"),
            "like_count": raw.get("public_metrics", {}).get("like_count") if raw.get("public_metrics") else raw.get("likes"),
            "reply_count": raw.get("public_metrics", {}).get("reply_count") if raw.get("public_metrics") else raw.get("replies"),
            "retweet_count": raw.get("public_metrics", {}).get("retweet_count") if raw.get("public_metrics") else raw.get("retweets"),
            "quote_count": raw.get("public_metrics", {}).get("quote_count") if raw.get("public_metrics") else raw.get("quotes"),
            "has_media": has_media,
            "has_links": has_links,
            "emojis": ",".join(emojis) if emojis else None
        }
