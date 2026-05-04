import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

if __name__ == "__main__":
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "anthropic/claude-sonnet-4-5",
            "messages": [
                {"role": "user", "content": "你好"}
            ]
        }
    )
    print(json.dumps(response.json(), indent=2))
