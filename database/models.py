"""
SQLAlchemy models for the content strategy database.
"""

from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, DateTime, Enum as SAEnum, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""
    pass


class Category(str, Enum):
    """Content category."""
    AI_CODING = "AI_CODING"
    LINUX = "LINUX"
    GITHUB_ACTIONS = "GITHUB_ACTIONS"


class Status(str, Enum):
    """Content production status."""
    TODO = "TODO"
    GENERATED = "GENERATED"
    RECORDED = "RECORDED"
    PUBLISHED = "PUBLISHED"


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Topic(Base):
    """Content topic record — tracks full lifecycle from idea to published."""

    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False, index=True)
    category = Column(
        SAEnum(Category, name="category_enum"),
        nullable=False,
        default=Category.AI_CODING,
        index=True,
    )
    difficulty = Column(String(50), default="intermediate")
    status = Column(
        SAEnum(Status, name="status_enum"),
        nullable=False,
        default=Status.TODO,
        index=True,
    )
    markdown_path = Column(String(1000), nullable=True)
    quality_score = Column(Integer, nullable=True)
    prompt_version = Column(String(50), default="v1.0")
    notes = Column(Text, nullable=True)

    # ── Phase 3: Trend Discovery fields ──────────────────────
    source = Column(String(50), nullable=True, default="manual", index=True)
    """Where this topic was discovered: manual | github | hackernews | reddit | devto"""

    trend_score = Column(Float, nullable=True)
    """Trend score 0-10 (engagement × recency × niche relevance)."""

    raw_title = Column(String(500), nullable=True)
    """Original title from the trend source, before LLM refinement."""

    source_url = Column(String(1000), nullable=True)
    """URL to the original trending item."""

    created_at = Column(DateTime(timezone=True), default=_now)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now)

    def __repr__(self) -> str:
        return f"<Topic id={self.id} status={self.status.value} title={self.title[:30]!r}>"
