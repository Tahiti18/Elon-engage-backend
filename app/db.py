# app/db.py  — robust DB init with Railway fallbacks
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

def _build_url_from_pg_env() -> str:
    host = os.environ.get("PGHOST", "")
    user = os.environ.get("PGUSER", "")
    pwd  = os.environ.get("PGPASSWORD", "")
    db   = os.environ.get("PGDATABASE", "")
    port = os.environ.get("PGPORT", "5432")
    if all([host, user, pwd, db]):
        return f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{db}"
    return ""

# 1) Prefer DATABASE_URL. 2) Fallback to composing from PG* vars.
DATABASE_URL = os.environ.get("DATABASE_URL", "") or _build_url_from_pg_env()
if not DATABASE_URL:
    # Last, very explicit error so we’re not guessing in logs
    raise RuntimeError(
        "No usable DB URL. Expected `DATABASE_URL` or PGHOST/PGUSER/PGPASSWORD/PGDATABASE from Railway."
    )

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
