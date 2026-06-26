"""Modeles SQLAlchemy : prix et news."""
from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime,
    UniqueConstraint, Index
)
from finapi.db import Base


class PriceRecord(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(16), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    close = Column(Float, nullable=False)
    currency = Column(String(8), default="USD")

    __table_args__ = (
        UniqueConstraint("ticker", "date", name="uq_ticker_date"),
    )


class NewsItem(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(16), nullable=False, index=True)
    published_at = Column(DateTime, nullable=False, index=True)
    title = Column(String(512), nullable=False)
    publisher = Column(String(128))
    url = Column(String(1024), unique=True)  # URL = cle de deduplication
    summary = Column(String(2048))

    __table_args__ = (
        # BONUS: index composite (ticker, published_at) sur news
        Index("ix_news_ticker_published_at", "ticker", "published_at"),
    )
