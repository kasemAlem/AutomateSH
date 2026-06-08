"""Orchestrator for the trend discovery pipeline."""

import structlog

from database.connection import get_session
from database.models import Category, Status, Topic
from trends.agent import refine_topics
from trends.deduplicator import deduplicate
from trends.scorer import sort_and_score
from trends.sources.base import RawTopic
from trends.sources.devto import DevToSource
from trends.sources.github import GitHubSource
from trends.sources.hackernews import HackerNewsSource
from trends.sources.reddit import RedditSource

logger = structlog.get_logger()

# Instantiate all configured sources
SOURCES = [
    GitHubSource(),
    HackerNewsSource(),
    RedditSource(),
    DevToSource()
]


def run_trend_pipeline(limit_per_source: int = 25, final_limit: int = 5, save: bool = True) -> list[Topic]:
    """
    Run the full trend discovery pipeline:
    1. Fetch from all sources
    2. Score and sort all items combined
    3. Deduplicate against database and within batch
    4. Pass top N to LLM agent for selection and refinement
    5. Save to database
    
    Returns the saved Topic models.
    """
    all_raw_topics: list[RawTopic] = []
    
    # 1. Fetch
    logger.info("Starting trend discovery pipeline")
    for source in SOURCES:
        try:
            topics = source.fetch(limit=limit_per_source)
            all_raw_topics.extend(topics)
        except Exception as e:
            logger.error("Source fetch failed", source=source.name, error=str(e))
            
    if not all_raw_topics:
        logger.warning("No trends found from any source")
        return []
        
    logger.info("Fetched total raw topics", count=len(all_raw_topics))
    
    # 2. Score & Sort
    scored_topics = sort_and_score(all_raw_topics)
    # Extract just the topics, now in order of highest score
    sorted_topics = [t for t, score in scored_topics]
    
    # 3. Deduplicate
    unique_topics = deduplicate(sorted_topics)
    logger.info("Topics after deduplication", count=len(unique_topics))
    
    # We only send the top 3x of final_limit to the LLM to save tokens
    llm_candidates = unique_topics[:final_limit * 3]
    
    # We need a quick way to map back from original_title to the RawTopic and score
    candidates_map = {t.title: t for t in llm_candidates}
    scores_map = {t.title: score for t, score in scored_topics}
    
    # 4. LLM Refinement
    refined_results = refine_topics(llm_candidates, limit=final_limit)
    
    if not refined_results:
        logger.warning("LLM returned no valid topics")
        return []
        
    # 5. Build Database Models
    db_topics = []
    for result in refined_results:
        original_title = result["original_title"]
        raw_topic = candidates_map.get(original_title)
        
        if not raw_topic:
            # LLM hallucinated a title or changed it too much
            logger.warning("LLM returned unknown original title", title=original_title)
            continue
            
        score = scores_map.get(original_title, 0.0)
        
        topic = Topic(
            title=result["refined_title"],
            raw_title=original_title,
            category=Category[result["category"]],
            status=Status.TODO,
            source=raw_topic.source,
            source_url=raw_topic.url,
            trend_score=score
        )
        db_topics.append(topic)
        
    # 6. Save to DB
    if save and db_topics:
        with get_session() as session:
            for t in db_topics:
                session.add(t)
        logger.info("Saved new trending topics to database", count=len(db_topics))
        
    return db_topics
