# app/services/metrics.py
from sqlalchemy.orm import Session
from sqlalchemy import text

def summary(db: Session) -> dict:
    # 1) Totals
    total = db.execute(text("SELECT COUNT(*) FROM tweets")).scalar() or 0

    # 2) By type
    by_type_rows = db.execute(text("""
        SELECT COALESCE(type,'unknown') AS t, COUNT(*) 
        FROM tweets 
        GROUP BY COALESCE(type,'unknown')
    """)).fetchall()
    by_type = {row[0]: row[1] for row in by_type_rows}

    # 3) Emoji-only replies (safe proxy in Postgres):
    #    "contains at least one non-ASCII" AND "no ASCII letters/digits"
    emoji_only = db.execute(text(r"""
        SELECT COUNT(*) 
        FROM tweets 
        WHERE type='reply'
          AND text IS NOT NULL
          AND text ~ '[^\x00-\x7F]'
          AND text !~ '[A-Za-z0-9]'
    """)).scalar() or 0

    # 4) Top domains (CORRECT JOIN to existing schema)
    #    domains(host) <-> tweet_domains(tweet_id, domain_id)
    top_domains_rows = db.execute(text("""
        SELECT d.host, COUNT(td.tweet_id) AS c
        FROM domains d
        JOIN tweet_domains td ON d.id = td.domain_id
        GROUP BY d.host
        ORDER BY c DESC
        LIMIT 10
    """)).fetchall()
    top_domains = [{"host": r[0], "count": r[1]} for r in top_domains_rows]

    return {
        "total_tweets": total,
        "by_type": by_type,
        "emoji_only_replies": emoji_only,
        "top_domains": top_domains,
    }
