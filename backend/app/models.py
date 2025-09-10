from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean, BigInteger, ForeignKey, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from .db import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)  # X user id (string)
    username: Mapped[str | None] = mapped_column(String(50), index=True)
    name: Mapped[str | None] = mapped_column(String(200))
    followers: Mapped[int | None] = mapped_column(Integer)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Tweet(Base):
    __tablename__ = "tweets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tweet_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    user_id: Mapped[str] = mapped_column(String(50), index=True)  # author id (string)
    in_reply_to_tweet_id: Mapped[str | None] = mapped_column(String(50), index=True)
    referenced_tweet_type: Mapped[str | None] = mapped_column(String(20))  # reply|retweet|quote|original
    text: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime | None] = mapped_column(DateTime)
    like_count: Mapped[int | None] = mapped_column(Integer)
    reply_count: Mapped[int | None] = mapped_column(Integer)
    retweet_count: Mapped[int | None] = mapped_column(Integer)
    quote_count: Mapped[int | None] = mapped_column(Integer)
    has_media: Mapped[bool] = mapped_column(Boolean, default=False)
    has_links: Mapped[bool] = mapped_column(Boolean, default=False)
    emojis: Mapped[str | None] = mapped_column(Text)  # comma-separated

Index("ix_tweets_author_created", Tweet.user_id, Tweet.created_at)

class Edge(Base):
    __tablename__ = "edges"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    src_tweet_id: Mapped[str] = mapped_column(String(50), index=True)
    dst_tweet_id: Mapped[str | None] = mapped_column(String(50), index=True)
    relation: Mapped[str] = mapped_column(String(20))  # reply|retweet|quote

class DomainRef(Base):
    __tablename__ = "domains"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tweet_id: Mapped[str] = mapped_column(String(50), index=True)
    domain: Mapped[str] = mapped_column(String(255), index=True)

class FeatureDaily(Base):
    __tablename__ = "features_daily"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    day: Mapped[str] = mapped_column(String(10), index=True)  # YYYY-MM-DD
    original_pct: Mapped[float | None]
    reply_pct: Mapped[float | None]
    retweet_pct: Mapped[float | None]
    quote_pct: Mapped[float | None]
    emoji_only_replies: Mapped[int | None]
