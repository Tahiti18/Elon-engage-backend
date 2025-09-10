from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db, Base, engine
from ..models import Tweet
from ..ingestion.twitterapi_io import TwitterAPIIO

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/ingest/elon")
def ingest_elon(limit: int = 100, db: Session = Depends(get_db)):
    Base.metadata.create_all(bind=engine)
    api = TwitterAPIIO()
    items = api.fetch_user_timeline("elonmusk", limit=limit)
    normalized = [api.normalize_tweet(i) for i in items]
    # Upsert by tweet_id
    dup = 0
    new = 0
    for t in normalized:
        if not t["tweet_id"]:
            continue
        exists = db.query(Tweet).filter(Tweet.tweet_id == t["tweet_id"]).first()
        if exists:
            dup += 1
            continue
        row = Tweet(**t)
        db.add(row)
        new += 1
    db.commit()
    return {"ingested": new, "duplicates": dup, "total_seen": len(normalized)}

@router.get("/metrics/summary")
def metrics_summary(db: Session = Depends(get_db)):
    total = db.query(Tweet).count()
    if total == 0:
        return {"total": 0, "message": "No data yet. POST /ingest/elon first."}
    type_counts = {}
    for ttype, in db.query(Tweet.referenced_tweet_type).all():
        if not ttype: 
            ttype = "unknown"
        type_counts[ttype] = type_counts.get(ttype, 0) + 1
    # Emoji-only replies = reply with only emojis (no letters/digits)
    import re
    emoji_only = 0
    for row in db.query(Tweet).filter(Tweet.referenced_tweet_type=="reply").all():
        txt = (row.text or "").strip()
        if txt and not re.search(r"[A-Za-z0-9]", txt):
            emoji_only += 1
    return {
        "total": total,
        "type_counts": type_counts,
        "emoji_only_replies": emoji_only,
        "emoji_only_reply_pct": round(100.0*emoji_only/total, 2)
    }
