from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.services.metrics import summary as summary_service
from app.clients.twitterapi_io import TwitterApiIoClient
from app.services.ingest import ingest_user_timeline
import os

router = APIRouter()

@router.get("/")
def root():
    return {"ok": True, "service": "Elon Engage API"}

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/_debug")
def debug_env():
    return {"PORT": os.environ.get("PORT", ""), "HAS_DATABASE_URL": bool(os.environ.get("DATABASE_URL"))}

@router.post("/ingest/elon")
async def ingest_elon(limit: int = 200, db: Session = Depends(get_db)):
    client = TwitterApiIoClient()
    try:
        payload = await client.fetch_user_tweets("elonmusk", limit=limit)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Ingestion upstream error: {e}")
    count = ingest_user_timeline(db, payload)
    db.commit()
    return {"ingested": count}

# ---- Metrics (expose BOTH paths) ----
@router.get("/metrics/summary")
@router.get("/summary")
def metrics_summary(db: Session = Depends(get_db)):
    try:
        return summary_service(db)
    except Exception as e:
        # Never 500 without context
        raise HTTPException(status_code=500, detail=f"metrics_error: {e}")
