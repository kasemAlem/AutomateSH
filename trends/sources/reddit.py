"""Reddit trend source."""

from datetime import datetime, timezone

import requests
import structlog

from trends.sources.base import RawTopic, TrendSource

logger = structlog.get_logger()


class RedditSource(TrendSource):
    """
    Fetches trending posts from specific programming subreddits.
    Uses the unauthenticated Reddit JSON API.
    """

    def __init__(self, subreddit: str = "programming+coding+webdev+devops"):
        self.subreddit = subreddit

    @property
    def name(self) -> str:
        return "reddit"

    def fetch(self, limit: int = 25) -> list[RawTopic]:
        """Fetch hot posts from the configured subreddits."""
        url = f"https://www.reddit.com/r/{self.subreddit}/hot.json?limit={limit}"
        
        # Reddit requires a custom User-Agent, otherwise it returns 429 Too Many Requests
        headers = {
            "User-Agent": "script:automate.sh.content.engine:v1.0 (by /u/automate_sh)"
        }

        logger.info("Fetching Reddit trends", url=url)

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            topics = []
            children = data.get("data", {}).get("children", [])
            
            for child in children:
                item = child.get("data", {})
                
                # Skip stickied posts
                if item.get("stickied", False):
                    continue
                    
                ts = item.get("created_utc")
                if not ts:
                    continue
                    
                published_at = datetime.fromtimestamp(ts, tz=timezone.utc)
                
                permalink = item.get("permalink", "")
                story_url = f"https://www.reddit.com{permalink}" if permalink else item.get("url", "")

                # Convert to RawTopic
                topic = RawTopic(
                    title=item.get("title", "Unknown"),
                    url=story_url,
                    source=self.name,
                    engagement=item.get("score", 0), # Upvotes
                    published_at=published_at,
                    description=item.get("selftext", "")[:500] if item.get("is_self") else "",
                    tags=[item.get("subreddit", "")]
                )
                topics.append(topic)
                
                # We might have skipped stickies, so respect the limit manually
                if len(topics) >= limit:
                    break

            logger.info("Fetched Reddit trends", count=len(topics))
            return topics

        except Exception as e:
            logger.error("Failed to fetch Reddit trends", error=str(e))
            return []
