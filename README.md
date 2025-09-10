# Elon Engage Backend (FastAPI + Postgres)

Purpose: ingest @elonmusk activity via twitterapi.io and compute breakdowns (emoji-only replies, repost/quote mix, target-account sizes, domains, timing).

## Quick start (local)
1) `cp .env.example .env` and set `TWITTERAPI_IO_KEY=new1_...`
2) (Optional) Set `DATABASE_URL` to Postgres; otherwise falls back to SQLite `sqlite:///./local.db`
3) `pip install -r backend/requirements.txt`
4) `cd backend && uvicorn app.main:app --reload` then open `http://127.0.0.1:8000/health`

## Railway
- Push this repo to GitHub
- On Railway: **Architecture → + New → PostgreSQL**
- Service: **Latest-fomo-superbot → Variables → New Variable (Reference) → Name: DATABASE_URL → Reference Postgres.DATABASE_URL → Save → Redeploy**
- Add `TWITTERAPI_IO_KEY` and `OPENROUTER_API_KEY` in Variables
- Verify logs show “DB ready” and visit `/health`

## Endpoints
- `GET /health`
- `POST /ingest/elon`  → on-demand pull from twitterapi.io (TEMPORARY: ensure endpoint base path matches your plan docs)
- `GET /metrics/summary` → type mix, emoji-only counts, target bands

## Note
- twitterapi.io is **unofficial**. Ensure usage aligns with your risk tolerance.
- Update `TWITTERAPI_BASE_URL` in config if your plan uses a different host/path.
