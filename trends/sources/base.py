"""
Trend source base types.

RawTopic — the common data structure every source returns.
TrendSource — the abstract interface every source must implement.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class RawTopic:
    """
    A single trending item fetched from a source.

    All sources normalise their output into this structure so the scorer
    and deduplicator can work source-agnostically.
    """

    title: str
    """Main title / headline of the trending item."""

    url: str
    """Canonical link to the original item."""

    source: str
    """Identifier of the source: 'github' | 'hackernews' | 'reddit' | 'devto'"""

    engagement: int
    """
    Raw engagement number — meaning depends on source:
      - GitHub: star count of the repository
      - HackerNews: story points
      - Reddit: upvote score
      - Dev.to: reactions + comments combined
    """

    published_at: datetime
    """When the item was published/created (UTC-aware)."""

    description: str = ""
    """Short description or body snippet (may be empty)."""

    tags: list[str] = field(default_factory=list)
    """Topic tags / labels provided by the source."""

    language: str = ""
    """Programming language (GitHub only; empty for other sources)."""

    def __post_init__(self) -> None:
        # Ensure timezone-aware datetime
        if self.published_at.tzinfo is None:
            self.published_at = self.published_at.replace(tzinfo=timezone.utc)

    @property
    def age_hours(self) -> float:
        """How many hours ago this item was published."""
        now = datetime.now(timezone.utc)
        delta = now - self.published_at
        return max(0.0, delta.total_seconds() / 3600)

    def __str__(self) -> str:
        return f"[{self.source}] {self.title} (eng={self.engagement}, {self.age_hours:.0f}h ago)"


class TrendSource(ABC):
    """Abstract base for all trend sources."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique source identifier ('github', 'hackernews', etc.)."""
        ...

    @abstractmethod
    def fetch(self, limit: int = 25) -> list[RawTopic]:
        """
        Fetch trending items from this source.

        Args:
            limit: Maximum number of items to return.

        Returns:
            List of RawTopic objects, newest/hottest first.
        """
        ...
