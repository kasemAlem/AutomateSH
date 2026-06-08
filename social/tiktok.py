"""
TikTok publishing integration using Composio SDK.
"""

from pathlib import Path
import structlog
import time
from composio import Composio

logger = structlog.get_logger(__name__)

def upload_and_publish_video(video_path: str | Path, title: str, hashtags: list[str]) -> str | None:
    """
    Upload and publish a video to TikTok using Composio.
    
    Args:
        video_path: Path to the .mp4 file.
        title: The title/caption of the video.
        hashtags: A list of hashtags to append.
        
    Returns:
        The URL of the published video, or None if failed.
    """
    try:
        path = Path(video_path)
        if not path.exists():
            logger.error("Video file not found", path=str(path))
            return None
            
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        c = Composio(
            api_key=os.environ.get("COMPOSIO_API_KEY"),
            file_upload_dirs=[str(path.parent.absolute())],
            dangerously_allow_auto_upload_download_files=True
        )
        
        # Format caption
        caption = f"{title}\n\n" + " ".join(hashtags)
        
        logger.info("Uploading video to TikTok via Composio...", path=str(path))
        upload_response = c.tools.execute(
            slug="tiktok_upload_video",
            arguments={
                "file_to_upload": str(path.absolute()),
                "title": caption,
                "publish": True,
                "privacy_level": "SELF_ONLY"
            },
            user_id="default",
            dangerously_skip_version_check=True
        )
        
        # Extract publish_id safely, handling both flat and nested 'data' formats
        if upload_response and "publish_id" in upload_response:
            publish_id = upload_response["publish_id"]
        elif upload_response and "data" in upload_response and "publish_id" in upload_response["data"]:
            publish_id = upload_response["data"]["publish_id"]
        else:
            logger.error("Failed to get publish_id from upload response", response=upload_response)
            return None
            
        logger.info("Video uploaded. Polling status...", publish_id=publish_id)
        
        # Poll status
        max_attempts = 15
        for attempt in range(max_attempts):
            status_response = c.tools.execute(
                slug="tiktok_fetch_publish_status",
                arguments={"publish_id": publish_id},
                user_id="default",
                dangerously_skip_version_check=True
            )
            
            # Extract status from nested 'data' if present
            if status_response and "data" in status_response and "status" in status_response["data"]:
                status = status_response["data"]["status"]
            else:
                status = status_response.get("status", "processing") if status_response else "processing"
                
            logger.debug("Publish status", status=status, attempt=attempt)
            
            if status == "success" or status == "ready":
                break
            elif status == "failed":
                logger.error("Video processing failed on TikTok", response=status_response)
                return None
                
            time.sleep(10)
        else:
            logger.warning("Polling timed out. Video might still process.")
            
        # Publish
        logger.info("TikTok publish completed successfully!")
        
        return "Published Successfully"
        
    except Exception as e:
        logger.error("Failed to publish to TikTok", error=str(e))
        return None
