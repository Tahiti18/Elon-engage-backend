from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db, Base, engine
from app.services.metrics import summary
from app.clients.twitterapi_io import TwitterApiIoClient
from app.services.ingest import ingest_user_timeline

router = APIRouter()

@router.get("/health")
def health():
    return {"status":"ok"}

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

@router.get("/metrics/summary")
def metrics_summary(db: Session = Depends(get_db)):
    return summary(db)
