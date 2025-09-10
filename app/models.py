from sqlalchemy import Column, String, Integer, BigInteger, Boolean, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(BigInteger, primary_key=True)
    username = Column(String(50), index=True, unique=True, nullable=False)
    name = Column(String(200))
    followers = Column(BigInteger, default=0)
    verified = Column(Boolean, default=False)
    account_type = Column(String(20), default="individual")  # or 'organization'

    tweets = relationship("Tweet", back_populates="user")

class Tweet(Base):
    __tablename__ = "tweets"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    text = Column(Text, default="")
    type = Column(String(20), index=True)  # original | reply | retweet | quote
    reply_to_id = Column(BigInteger, nullable=True)
    quote_of_id = Column(BigInteger, nullable=True)
    retweet_of_id = Column(BigInteger, nullable=True)

    user = relationship("User", back_populates="tweets")
    stats = relationship("TweetStats", uselist=False, back_populates="tweet")

class TweetStats(Base):
    __tablename__ = "tweet_stats"
    tweet_id = Column(BigInteger, ForeignKey("tweets.id"), primary_key=True)
    replies = Column(Integer, default=0)
    retweets = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    bookmarks = Column(Integer, default=0)

    tweet = relationship("Tweet", back_populates="stats")

class Domain(Base):
    __tablename__ = "domains"
    id = Column(Integer, primary_key=True, autoincrement=True)
    host = Column(String(255), unique=True, nullable=False, index=True)

class TweetDomain(Base):
    __tablename__ = "tweet_domains"
    tweet_id = Column(BigInteger, ForeignKey("tweets.id"), primary_key=True)
    domain_id = Column(Integer, ForeignKey("domains.id"), primary_key=True)

class TweetEmoji(Base):
    __tablename__ = "tweet_emojis"
    tweet_id = Column(BigInteger, ForeignKey("tweets.id"), primary_key=True)
    emoji = Column(String(16), primary_key=True)

class Edge(Base):
    __tablename__ = "edges"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tweet_id = Column(BigInteger, index=True, nullable=False)
    source_user_id = Column(BigInteger, index=True, nullable=False)
    target_user_id = Column(BigInteger, index=True, nullable=False)
    relation = Column(String(20), index=True)  # reply|retweet|quote
    __table_args__ = (UniqueConstraint('tweet_id', 'relation', name='uq_edge_tweet_relation'),)
