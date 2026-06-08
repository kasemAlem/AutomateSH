"""Trend scoring logic."""

import math

from trends.sources.base import RawTopic

# Base engagement expected from different sources to hit a "1.0" multiplier
# This normalizes the fact that a GitHub star is harder to get than a Reddit upvote
BASE_ENGAGEMENT = {
    "github": 500.0,
    "hackernews": 200.0,
    "reddit": 1000.0,
    "devto": 50.0,
}

# Niche keywords that boost the score for developer content
NICHE_KEYWORDS = {
    "python", "javascript", "typescript", "rust", "go", "golang",
    "react", "nextjs", "vue",
    "docker", "kubernetes", "k8s", "github actions", "ci/cd", "devops",
    "linux", "terminal", "bash", "zsh", "tmux", "vim", "neovim",
    "ai", "llm", "claude", "gpt", "openai", "machine learning",
    "database", "postgres", "sql", "redis",
}


def calculate_score(topic: RawTopic) -> float:
    """
    Calculate a trend score from 0.0 to 10.0 for a given raw topic.
    Formula balances Engagement × Recency × Niche Relevance.
    """
    # 1. Normalized Engagement (Logarithmic to prevent mega-viral outliers crushing everything)
    base = BASE_ENGAGEMENT.get(topic.source, 500.0)
    # Using log2 so hitting the base engagement = 1.0 multiplier
    # e.g., 500 github stars / 500 = 1.0. max(1, log2(1+1)) = 1.0
    engagement_ratio = max(1.0, topic.engagement) / base
    engagement_factor = math.log2(1.0 + engagement_ratio)

    # 2. Time Decay (Half-life of 48 hours)
    # Exponential decay: e^(-lambda * t)
    # lambda = ln(2) / half_life
    half_life_hours = 48.0
    decay_constant = math.log(2.0) / half_life_hours
    recency_factor = math.exp(-decay_constant * topic.age_hours)

    # 3. Niche Relevance Multiplier
    # Boost topics that match our developer focus
    content = f"{topic.title} {topic.description} {' '.join(topic.tags)}".lower()
    
    niche_matches = sum(1 for kw in NICHE_KEYWORDS if kw in content)
    # Max out at 3 matches for a 1.5x boost
    relevance_factor = 1.0 + (min(3, niche_matches) * 0.16)

    # Calculate raw score
    raw_score = engagement_factor * recency_factor * relevance_factor * 2.5

    # Clamp between 0.0 and 10.0
    return max(0.0, min(10.0, raw_score))


def sort_and_score(topics: list[RawTopic]) -> list[tuple[RawTopic, float]]:
    """Score a list of topics and return them sorted highest to lowest."""
    scored = [(topic, calculate_score(topic)) for topic in topics]
    # Sort descending by score
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored
