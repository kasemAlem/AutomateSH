"""GitHub trend source."""

from datetime import datetime, timedelta, timezone
from urllib.parse import quote

import requests
import structlog

from trends.sources.base import RawTopic, TrendSource

logger = structlog.get_logger()


class GitHubSource(TrendSource):
    """
    Fetches trending GitHub repositories created recently.
    Uses the GitHub Search API.
    """

    @property
    def name(self) -> str:
        return "github"

    def fetch(self, limit: int = 25) -> list[RawTopic]:
        """Fetch repositories created in the last 7 days sorted by stars."""
        # Calculate date 7 days ago
        seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")

        # Query: created:>YYYY-MM-DD
        query = f"created:>{seven_days_ago}"
        encoded_query = quote(query)

        url = (
            f"https://api.github.com/search/repositories"
            f"?q={encoded_query}&sort=stars&order=desc&per_page={limit}"
        )

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Automate.sh Content Engine"
        }

        logger.info("Fetching GitHub trends", url=url)

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            topics = []
            for item in data.get("items", []):
                # Parse created_at: "2023-01-01T00:00:00Z"
                created_at_str = item.get("created_at")
                if not created_at_str:
                    continue
                    
                published_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))

                # Convert to RawTopic
                topic = RawTopic(
                    title=item.get("full_name", "Unknown"),
                    url=item.get("html_url", ""),
                    source=self.name,
                    engagement=item.get("stargazers_count", 0),
                    published_at=published_at,
                    description=item.get("description") or "",
                    tags=item.get("topics", []),
                    language=item.get("language") or ""
                )
                topics.append(topic)

            logger.info("Fetched GitHub trends", count=len(topics))
            return topics

        except Exception as e:
            logger.error("Failed to fetch GitHub trends", error=str(e))
            return []
