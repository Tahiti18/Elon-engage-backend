from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from app.models import User, Tweet, TweetStats, Domain, TweetDomain, TweetEmoji, Edge
from urllib.parse import urlparse
import re

# Broad unicode range approach; avoids dependency on emoji.get_emoji_regexp
EMOJI_PATTERN = re.compile(r'[\U00010000-\U0010ffff]', flags=re.UNICODE)

def upsert_user(db: Session, data: Dict[str, Any]) -> Optional[User]:
    uid = int(data.get('id') or data.get('user_id') or 0)
    if uid == 0:
        return None
    u = db.get(User, uid)
    if not u:
        u = User(id=uid, username=data.get('username',''), name=data.get('name',''))
        db.add(u)
    u.followers = int(data.get('followers', u.followers or 0))
    u.verified = bool(data.get('verified', u.verified or False))
    u.account_type = data.get('account_type', u.account_type or 'individual')
    return u

def extract_domains(text: str) -> List[str]:
    hosts = set()
    for token in (text or '').split():
        if token.startswith("http://") or token.startswith("https://"):
            try:
                host = urlparse(token).hostname
                if host:
                    hosts.add(host.lower())
            except Exception:
                pass
    return list(hosts)

def extract_emojis(text: str) -> List[str]:
    return [ch for ch in (text or '') if EMOJI_PATTERN.match(ch)]

def normalize_type(item: Dict[str,Any]) -> str:
    if item.get('is_retweet') or item.get('retweeted_status_id'):
        return 'retweet'
    if item.get('is_quote') or item.get('quoted_status_id'):
        return 'quote'
    if item.get('in_reply_to_status_id'):
        return 'reply'
    return 'original'

def save_tweet_row(db: Session, item: Dict[str, Any]) -> Optional[Tweet]:
    tid = int(item.get('id') or 0)
    uid = int(item.get('user',{}).get('id') or 0)
    if tid == 0 or uid == 0:
        return None
    tw = db.get(Tweet, tid)
    if not tw:
        tw = Tweet(id=tid, user_id=uid)
        db.add(tw)
    tw.text = item.get('full_text') or item.get('text','')
    tw.type = normalize_type(item)
    tw.reply_to_id = item.get('in_reply_to_status_id')
    tw.quote_of_id = item.get('quoted_status_id')
    tw.retweet_of_id = item.get('retweeted_status_id')

    stats = tw.stats or TweetStats(tweet_id=tid)
    stats.replies = int(item.get('reply_count', 0))
    stats.retweets = int(item.get('retweet_count', 0))
    stats.likes = int(item.get('favorite_count', 0))
    # bookmarks rarely available
    db.add(stats)

    for host in extract_domains(tw.text):
        d = db.query(Domain).filter_by(host=host).one_or_none()
        if not d:
            d = Domain(host=host)
            db.add(d)
            db.flush()
        if not db.query(TweetDomain).filter_by(tweet_id=tid, domain_id=d.id).one_or_none():
            db.add(TweetDomain(tweet_id=tid, domain_id=d.id))

    for e in extract_emojis(tw.text):
        if not db.query(TweetEmoji).filter_by(tweet_id=tid, emoji=e).one_or_none():
            db.add(TweetEmoji(tweet_id=tid, emoji=e))

    target_uid = item.get('in_reply_to_user_id') or item.get('retweeted_user_id') or item.get('quoted_user_id')
    if target_uid:
        relation = 'reply' if tw.reply_to_id else ('retweet' if tw.retweet_of_id else ('quote' if tw.quote_of_id else ''))
        if relation:
            db.add(Edge(tweet_id=tid, source_user_id=uid, target_user_id=int(target_uid), relation=relation))

    return tw

def ingest_user_timeline(db: Session, payload: Dict[str, Any]) -> int:
    items = payload.get('data') or payload.get('tweets') or []
    count = 0
    for item in items:
        t = save_tweet_row(db, item)
        if t:
            count += 1
    return count
