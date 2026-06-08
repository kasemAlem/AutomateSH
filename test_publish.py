import os
import sys
from pathlib import Path
from social.tiktok import upload_and_publish_video

def test_publish():
    # Use the existing generated video
    video_path = "output/2026-06-08-my-first-automation-test-final.mp4"
    if not Path(video_path).exists():
        print(f"Error: {video_path} not found. Run the full pipeline first.")
        sys.exit(1)
        
    title = "**One Failing Test That Saves Your Next Deployment**"
    hashtags = ["#coding", "#programming", "#developer", "#tech"]
    
    print("Testing TikTok publish directly...")
    result = upload_and_publish_video(video_path, title, hashtags)
    
    if result:
        print(f"Success! Video published. URL: {result}")
    else:
        print("Publish failed. Check logs above.")

if __name__ == "__main__":
    test_publish()
