import os
from composio import Composio

def update_credentials():
    print("=== Update TikTok Credentials in Composio ===")
    client_id = input("Enter your new Sandbox Client Key: ").strip()
    client_secret = input("Enter your new Sandbox Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("Error: You must provide both.")
        return

    c = Composio(api_key=os.environ.get("COMPOSIO_API_KEY"))
    
    try:
        # Re-create the auth config with the new sandbox credentials
        auth_config = c.auth_configs.create(
            app_name="tiktok",
            auth_mode="OAUTH2",
            credentials={
                "client_id": client_id,
                "client_secret": client_secret,
                "scopes": [
                    "user.info.basic",
                    "user.info.profile",
                    "user.info.stats",
                    "video.list",
                    "video.upload",
                    "video.publish"
                ]
            }
        )
        print(f"\n✅ Successfully updated Composio!")
        print(f"Your new auth_config_id is: {auth_config.id}")
        print("\nNow, OPEN your 'connect_and_publish.py' file and replace the old auth_config_id")
        print(f"with this new one: {auth_config.id}")
        
    except Exception as e:
        print(f"Error updating Composio: {e}")

if __name__ == "__main__":
    update_credentials()
