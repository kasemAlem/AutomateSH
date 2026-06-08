"""LLM Agent for refining trend topics."""

import json
from pathlib import Path

import structlog

from providers.factory import get_provider
from trends.sources.base import RawTopic

logger = structlog.get_logger()

PROMPT_PATH = Path("prompts/trend_agent.md")


def load_prompt() -> str:
    """Load the trend agent prompt template."""
    return PROMPT_PATH.read_text(encoding="utf-8")


def refine_topics(topics: list[RawTopic], limit: int = 5) -> list[dict]:
    """
    Pass raw topics to the LLM to select the best ones, refine their titles,
    and categorize them.
    
    Returns a list of dicts:
      [{"original_title": "...", "refined_title": "...", "category": "..."}]
    """
    if not topics:
        return []

    # Prepare input data for the LLM
    # We only send title and description to save context window
    input_data = []
    for t in topics:
        input_data.append({
            "title": t.title,
            "description": t.description[:200] if t.description else "",
            "source": t.source,
            "tags": t.tags[:3]
        })

    topics_json = json.dumps(input_data, indent=2)
    
    prompt_template = load_prompt()
    prompt = prompt_template.format(
        topics_json=topics_json,
        limit=limit
    )

    provider = get_provider()
    logger.info("Calling LLM to refine topics", input_count=len(topics), limit=limit)
    
    try:
        response_text = provider.generate(prompt)
        
        # Clean up response (some models ignore the "no markdown" instruction)
        cleaned = response_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned.replace("```json", "", 1)
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```", "", 1)
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
            
        cleaned = cleaned.strip()
        
        # Parse JSON
        results = json.loads(cleaned)
        
        # Validate format
        valid_results = []
        for r in results:
            if "original_title" in r and "refined_title" in r and "category" in r:
                # Ensure category is valid, fallback to LINUX if not
                cat = r["category"].upper()
                if cat not in ["AI_CODING", "LINUX", "GITHUB_ACTIONS"]:
                    cat = "LINUX"
                r["category"] = cat
                valid_results.append(r)
                
        logger.info("Successfully refined topics", count=len(valid_results))
        return valid_results
        
    except json.JSONDecodeError as e:
        logger.error("LLM returned invalid JSON", error=str(e), response=response_text[:200])
        return []
    except Exception as e:
        logger.error("Failed to refine topics", error=str(e))
        return []
