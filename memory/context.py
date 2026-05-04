import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
CONTEXT_PATH = "memory/context.json"

def load_context(agent_name: str) -> str:
    if not os.path.exists(CONTEXT_PATH):
        return ""
    with open(CONTEXT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get(agent_name, "")

def save_context(agent_name: str, new_summary: str):
    data = {}
    if os.path.exists(CONTEXT_PATH):
        with open(CONTEXT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    data[agent_name] = new_summary
    with open(CONTEXT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def compress_context(agent_name: str, old_summary: str, new_exchange: str) -> str:
    if not old_summary and not new_exchange:
        return ""
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "anthropic/claude-haiku-4.5",
            "max_tokens": 300,
            "messages": [
                {
                    "role": "system",
                    "content": "把以下對話紀錄壓縮成重點摘要，50字以內，只保留對未來對話有用的事實，禁止使用任何Markdown符號，純文字輸出。"
                },
                {
                    "role": "user",
                    "content": f"舊摘要：{old_summary}\n\n新對話：{new_exchange}"
                }
            ]
        }
    )
    result = response.json()
    if "choices" not in result:
        print("API ERROR:", result)
        return old_summary
    return result["choices"][0]["message"]["content"]

def update_context(agent_name: str, user_msg: str, assistant_msg: str):
    old = load_context(agent_name)
    new_exchange = f"用戶：{user_msg}\nAI：{assistant_msg[:200]}"
    new_summary = compress_context(agent_name, old, new_exchange)
    save_context(agent_name, new_summary)
