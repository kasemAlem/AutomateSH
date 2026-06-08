"""Dev.to trend source."""

from datetime import datetime, timezone

import requests
import structlog

from trends.sources.base import RawTopic, TrendSource

logger = structlog.get_logger()


class DevToSource(TrendSource):
    """
    Fetches trending articles from Dev.to.
    Uses the Forem API.
    """

    @property
    def name(self) -> str:
        return "devto"

    def fetch(self, limit: int = 25) -> list[RawTopic]:
        """Fetch top articles of the week from Dev.to."""
        url = f"https://dev.to/api/articles?state=rising&per_page={limit}"
        
        headers = {
            "Accept": "application/vnd.forem.api-v1+json",
            "User-Agent": "Automate.sh Content Engine"
        }

        logger.info("Fetching Dev.to trends", url=url)

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            topics = []
            for item in data:
                created_at_str = item.get("published_at")
                if not created_at_str:
                    continue
                    
                published_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))

                # Engagement = positive reactions + comments
                engagement = item.get("public_reactions_count", 0) + item.get("comments_count", 0)

                # Convert to RawTopic
                topic = RawTopic(
                    title=item.get("title", "Unknown"),
                    url=item.get("url", ""),
                    source=self.name,
                    engagement=engagement,
                    published_at=published_at,
                    description=item.get("description", ""),
                    tags=item.get("tag_list", [])
                )
                topics.append(topic)

            logger.info("Fetched Dev.to trends", count=len(topics))
            return topics

        except Exception as e:
            logger.error("Failed to fetch Dev.to trends", error=str(e))
            return []
