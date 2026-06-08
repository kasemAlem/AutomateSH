"""Tests for the trend discovery system."""

from datetime import datetime, timedelta, timezone

import pytest

from trends.deduplicator import is_duplicate, _normalize_string
from trends.scorer import calculate_score, sort_and_score
from trends.sources.base import RawTopic


def _make_topic(
    title: str = "Test",
    source: str = "github",
    engagement: int = 100,
    hours_ago: float = 1.0,
    tags: list[str] = None
) -> RawTopic:
    now = datetime.now(timezone.utc)
    return RawTopic(
        title=title,
        url="http://test",
        source=source,
        engagement=engagement,
        published_at=now - timedelta(hours=hours_ago),
        tags=tags or []
    )


class TestTrendScoring:
    """Test the trend scoring logic."""

    def test_engagement_impact(self):
        """Higher engagement should yield higher scores if recency is identical."""
        t_low = _make_topic(engagement=100)
        t_high = _make_topic(engagement=5000)
        
        score_low = calculate_score(t_low)
        score_high = calculate_score(t_high)
        
        assert score_high > score_low

    def test_recency_decay(self):
        """Older items should score lower if engagement is identical."""
        t_new = _make_topic(hours_ago=1)
        t_old = _make_topic(hours_ago=48)  # Half-life
        
        score_new = calculate_score(t_new)
        score_old = calculate_score(t_old)
        
        assert score_new > score_old
        # score_old should be roughly half of score_new (excluding engagement log curves)
        assert score_old < (score_new * 0.6)

    def test_niche_relevance_boost(self):
        """Topics with developer keywords should score higher."""
        t_generic = _make_topic(title="A new tool")
        t_niche = _make_topic(title="A new python tool for docker")
        
        score_generic = calculate_score(t_generic)
        score_niche = calculate_score(t_niche)
        
        assert score_niche > score_generic

    def test_sort_and_score(self):
        """Topics should be sorted correctly by score."""
        t_bad = _make_topic(engagement=10, hours_ago=200)
        t_good = _make_topic(engagement=5000, hours_ago=1, title="rust docker linux")
        t_mid = _make_topic(engagement=500, hours_ago=10)
        
        sorted_topics = sort_and_score([t_bad, t_good, t_mid])
        
        # Check order
        assert sorted_topics[0][0] == t_good
        assert sorted_topics[1][0] == t_mid
        assert sorted_topics[2][0] == t_bad


class TestDeduplication:
    """Test string normalization and deduplication logic."""

    def test_normalization(self):
        assert _normalize_string("Hello World 2.0!") == "helloworld20"
        assert _normalize_string("GitHub Actions: The Guide") == "githubactionstheguide"

    def test_exact_duplicate(self):
        existing = ["githubactionstheguide"]
        assert is_duplicate("GitHub Actions: The Guide", existing) is True

    def test_substring_duplicate(self):
        # "githubactions" is part of the existing long title
        existing = ["theultimate100pagegithubactionstheguide"]
        assert is_duplicate("GitHub Actions: The Guide", existing) is True

    def test_not_duplicate(self):
        existing = ["rustprogramming", "dockercontainers"]
        assert is_duplicate("GitHub Actions: The Guide", existing) is False
