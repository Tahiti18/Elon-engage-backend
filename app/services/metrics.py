# app/services/metrics.py
from sqlalchemy.orm import Session
from sqlalchemy import text

def summary(db: Session):
    # Total tweets
    total_tweets = db.execute(text("SELECT COUNT(*) FROM tweets")).scalar()

    # Replies only
    replies = db.execute(text("SELECT COUNT(*) FROM tweets WHERE type='reply'")).scalar()

    # Emoji-only replies (safe regex: counts replies with non-ASCII chars)
    emoji_only_replies = db.execute(
        text("SELECT COUNT(*) FROM tweets WHERE type='reply' AND text ~ '[^\\x00-\\x7F]'")
    ).scalar()

    # Retweets
    retweets = db.execute(text("SELECT COUNT(*) FROM tweets WHERE type='retweet'")).scalar()

    # Domains from URLs
    domains = db.execute(
        text("SELECT domain, COUNT(*) FROM tweet_domains GROUP BY domain ORDER BY COUNT(*) DESC LIMIT 10")
    ).fetchall()

    return {
        "total_tweets": total_tweets,
        "replies": replies,
        "emoji_only_replies": emoji_only_replies,
        "retweets": retweets,
        "top_domains": [{"domain": d[0], "count": d[1]} for d in domains],
    }
