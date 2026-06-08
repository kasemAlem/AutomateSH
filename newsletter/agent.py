import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import structlog
from langchain_core.messages import SystemMessage, HumanMessage

from app.config import get_settings
from database.connection import get_session
from database.models import Topic, Status
from providers.factory import get_provider

logger = structlog.get_logger(__name__)

SYSTEM_PROMPT = """You are the author of "Automate.sh Weekly" - a premium newsletter for software engineers.
Your goal is to take a list of videos/articles published this week and write a cohesive, engaging newsletter.

Structure:
1. Catchy subject line / headline.
2. A brief intro hook (e.g., "This week in automation...").
3. A summary of the key content published this week (use the provided topics).
4. Extract 1-2 actionable technical takeaways from the provided markdown scripts.
5. A brief outro encouraging them to try it out or reply.

Tone: Professional, developer-focused, concise, and high-value (no fluff).
Output MUST be valid Markdown.
"""

def generate_weekly_newsletter():
    """Fetches published topics from the last 7 days and generates a newsletter."""
    logger.info("Starting weekly newsletter generation")
    
    # Calculate date 7 days ago
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    
    with get_session() as session:
        # Fetch published topics from the last 7 days
        topics = session.query(Topic).filter(
            Topic.status == Status.PUBLISHED,
            Topic.updated_at >= seven_days_ago
        ).all()
        
        if not topics:
            logger.info("No published topics found in the last 7 days. Skipping newsletter.")
            return None
            
        logger.info(f"Found {len(topics)} published topics. Reading content...")
        
        content_summaries = []
        for topic in topics:
            summary = f"Title: {topic.title}\n"
            if topic.markdown_path and os.path.exists(topic.markdown_path):
                with open(topic.markdown_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Just grab the first 1000 characters to avoid huge context limits
                    summary += f"Content Snippet: {content[:1000]}...\n"
            content_summaries.append(summary)
            
    # Compile the prompt
    human_prompt = "Here is the content published this week:\n\n" + "\n---\n".join(content_summaries)
    
    logger.info("Calling LLM to generate newsletter...")
    provider = get_provider()
    llm = provider.get_llm()
    
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=human_prompt)
    ]
    
    response = llm.invoke(messages)
    newsletter_content = response.content
    
    # Save the newsletter
    settings = get_settings()
    output_dir = Path(settings.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    out_path = output_dir / f"newsletter-{date_str}.md"
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(newsletter_content)
        
    logger.info(f"Newsletter successfully generated and saved to {out_path}")
    return out_path
