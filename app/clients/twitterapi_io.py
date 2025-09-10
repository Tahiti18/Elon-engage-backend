import httpx
from app.config import settings

class TwitterApiIoClient:
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key or settings.TWITTERAPI_IO_KEY
        self.base_url = base_url or settings.TWITTERAPI_IO_BASE_URL
        self.user_tweets_path = settings.TWITTERAPI_IO_USER_TWEETS_PATH

    async def fetch_user_tweets(self, username: str, limit: int = 200):
        """
        Endpoint path is configurable. Default assumes:
          - GET {base_url}{user_tweets_path}?username=<username>&limit=<n>
          - Header: Authorization: Bearer <key>
        """
        headers = {"Authorization": f"Bearer {self.api_key}"}
        params = {"username": username, "limit": str(limit)}
        url = f"{self.base_url.rstrip('/')}{self.user_tweets_path}"
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.get(url, params=params, headers=headers)
            r.raise_for_status()
            return r.json()
