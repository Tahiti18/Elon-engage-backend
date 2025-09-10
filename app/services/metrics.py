from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.models import Tweet, Domain, TweetDomain

def summary(db: Session) -> dict:
    total = db.query(func.count(Tweet.id)).scalar() or 0
    by_type = dict(db.query(Tweet.type, func.count(Tweet.id)).group_by(Tweet.type).all())

    # emoji-only replies (approx): text comprised solely of non-BMP unicode (emojis)
    emoji_only = db.execute(
        text(r"SELECT COUNT(*) FROM tweets WHERE type='reply' AND text ~ '^[\x{10000}-\x{10FFFF}]+$'")
    ).scalar() or 0

    top_domains = db.query(Domain.host, func.count(TweetDomain.tweet_id)) \
        .join(TweetDomain, Domain.id==TweetDomain.domain_id) \
        .group_by(Domain.host) \
        .order_by(func.count(TweetDomain.tweet_id).desc()) \
        .limit(10).all()

    return {
        "total_tweets": total,
        "by_type": by_type,
        "emoji_only_replies": emoji_only,
        "top_domains": [{"host": h, "count": c} for h,c in top_domains],
    }
