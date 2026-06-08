import os
from composio import Composio

c = Composio(api_key=os.environ.get("COMPOSIO_API_KEY"))

try:
    print("Executing fetch publish status via c.tools.execute...")
    res = c.tools.execute(
        slug="tiktok_fetch_publish_status",
        arguments={"publish_id": "123"},
        user_id="default",
        dangerously_skip_version_check=True
    )
    print("Response:", res)
except Exception as e:
    print(f"Exception occurred: {e}")
