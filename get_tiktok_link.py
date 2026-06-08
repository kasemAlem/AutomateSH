import os
from composio import Composio
from dotenv import load_dotenv

def get_auth_link():
    load_dotenv()
    c = Composio(api_key=os.environ.get("COMPOSIO_API_KEY"))
    
    print("Generating TikTok authorization link...")
    
    connection = c.connected_accounts.initiate(
        user_id="default",
        auth_config_id="ac_9MeSmW47Oxl7",
        callback_url="https://composio.dev"
    )
    
    print("\n" + "="*60)
    print("SUCCESS! Here is your connection link:")
    print(connection.redirect_url)
    print("="*60 + "\n")
    print("1. Click the link above to open TikTok")
    print("2. Authorize the application")
    print("3. Come back and run: .venv/bin/python test_publish.py")

if __name__ == "__main__":
    get_auth_link()
