# Elon Engage Backend (Fixed)

FastAPI + Postgres backend wired for **TwitterAPI.io** ingestion and metrics.
This build **does not** import `emoji.get_emoji_regexp` and is safe with emoji>=2.x.

## Endpoints
- GET /health
- POST /ingest/elon?limit=200
- GET /metrics/summary

## Run
- `uvicorn main:app --host 0.0.0.0 --port 8000`
