import os
import sys
from pathlib import Path
from composio import Composio
from dotenv import load_dotenv
from social.tiktok import upload_and_publish_video

def main():
    load_dotenv()
    c = Composio(api_key=os.environ.get("COMPOSIO_API_KEY"))
    
    print("Generating a fresh TikTok authorization link...")
    
    from composio.exceptions import ComposioMultipleConnectedAccountsError
    try:
        # Create a new connection request
        connection = c.connected_accounts.initiate(
            user_id="default",
            auth_config_id="ac_9MeSmW47Oxl7",
            callback_url="https://composio.dev"
        )
        
        print("\n" + "="*80)
        print(" ACTION REQUIRED: PLEASE CLICK THE LINK BELOW AND AUTHORIZE TIKTOK")
        print("="*80)
        print(f"\n   URL: {connection.redirect_url}\n")
        print("="*80)
        print("Waiting for you to complete authorization in your browser...\n")
        
        # Wait for the user to complete the OAuth flow
        account = connection.wait_for_connection(
            timeout=300.0  # Wait up to 5 minutes
        )
        print("\n✅ TikTok account successfully connected to Composio!")
    except ComposioMultipleConnectedAccountsError:
        print("\n✅ You are already connected to TikTok! Skipping authorization...")
    except Exception as e:
        print(f"\n❌ Error waiting for connection: {e}")
        print("Please run this script again and complete the authorization.")
        sys.exit(1)
        
    print("\nNow attempting to publish the video...")
    
    video_path = "output/2026-06-08-my-first-automation-test-final.mp4"
    if not Path(video_path).exists():
        print(f"Error: {video_path} not found. Run the full pipeline first.")
        sys.exit(1)
        
    title = "**One Failing Test That Saves Your Next Deployment**"
    hashtags = ["#coding", "#programming", "#developer", "#tech"]
    
    result = upload_and_publish_video(video_path, title, hashtags)
    
    if result:
        print(f"\n🎉 Success! Video published. URL: {result}")
    else:
        print("\n❌ Publish failed. Check logs above.")

if __name__ == "__main__":
    main()
