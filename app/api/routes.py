from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.services.metrics import summary
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
    # No secrets returned; just enough to confirm wiring
    return {"PORT": os.environ.get("PORT", ""), "HAS_DATABASE_URL": bool(os.environ.get("DATABASE_URL"))}

@router.post("/ingest/elon")
async def ingest_elon(limit: int = 200, db: Session = Depends(get_db)):
    client
