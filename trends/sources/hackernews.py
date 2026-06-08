"""HackerNews trend source."""

from datetime import datetime, timezone

import requests
import structlog

from trends.sources.base import RawTopic, TrendSource

logger = structlog.get_logger()


class HackerNewsSource(TrendSource):
    """
    Fetches trending HackerNews stories.
    Uses the Algolia HN Search API for better querying capabilities.
    """

    @property
    def name(self) -> str:
        return "hackernews"

    def fetch(self, limit: int = 25) -> list[RawTopic]:
        """Fetch front page stories using Algolia."""
        # Use Algolia search to get front page items
        url = f"https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage={limit}"
        
        headers = {
            "User-Agent": "Automate.sh Content Engine"
        }

        logger.info("Fetching HackerNews trends", url=url)

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            topics = []
            for item in data.get("hits", []):
                # item["created_at_i"] is a unix timestamp
                ts = item.get("created_at_i")
                if not ts:
                    continue
                    
                published_at = datetime.fromtimestamp(ts, tz=timezone.utc)
                
                # Get URL or fallback to HN item page
                story_url = item.get("url")
                if not story_url:
                    story_url = f"https://news.ycombinator.com/item?id={item.get('objectID')}"

                # Convert to RawTopic
                topic = RawTopic(
                    title=item.get("title", "Unknown"),
                    url=story_url,
                    source=self.name,
                    engagement=item.get("points", 0),
                    published_at=published_at,
                    description=""  # HN stories usually don't have descriptions in this endpoint
                )
                topics.append(topic)

            logger.info("Fetched HackerNews trends", count=len(topics))
            return topics

        except Exception as e:
            logger.error("Failed to fetch HackerNews trends", error=str(e))
            return []
