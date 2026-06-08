"""Deduplication logic."""

import re

from sqlalchemy import select

from database.connection import get_session
from database.models import Topic
from trends.sources.base import RawTopic


def _normalize_string(s: str) -> str:
    """Normalize string for fuzzy comparison: lowercase, alphanumeric only."""
    return re.sub(r'[^a-z0-9]', '', s.lower())


def get_existing_topics() -> list[str]:
    """Fetch all existing topic titles and raw_titles from the database."""
    with get_session() as session:
        # Get both user-facing titles and original raw titles
        stmt = select(Topic.title, Topic.raw_title)
        results = session.execute(stmt).fetchall()
        
        existing = set()
        for row in results:
            if row[0]:
                existing.add(_normalize_string(row[0]))
            if row[1]:
                existing.add(_normalize_string(row[1]))
                
        return list(existing)


def is_duplicate(new_title: str, existing_normalized: list[str]) -> bool:
    """
    Check if a title is a duplicate.
    Currently uses simple exact match on normalized strings.
    Could be upgraded to Levenshtein distance or Embedding similarity later.
    """
    normalized_new = _normalize_string(new_title)
    
    # Fast exact match on normalized string
    if normalized_new in existing_normalized:
        return True
        
    # Check if one is a significant substring of the other (if > 10 chars)
    if len(normalized_new) > 10:
        for ex in existing_normalized:
            if len(ex) > 10 and (normalized_new in ex or ex in normalized_new):
                return True
                
    return False


def deduplicate(topics: list[RawTopic]) -> list[RawTopic]:
    """
    Filter out topics that already exist in the database.
    Also deduplicates within the incoming list itself.
    """
    existing_normalized = get_existing_topics()
    
    unique_topics = []
    seen_in_batch = set()
    
    for topic in topics:
        norm_title = _normalize_string(topic.title)
        
        # 1. Check if we already processed this in the current batch
        if norm_title in seen_in_batch:
            continue
            
        # 2. Check if it's in the database
        if is_duplicate(topic.title, existing_normalized):
            continue
            
        seen_in_batch.add(norm_title)
        unique_topics.append(topic)
        
    return unique_topics
