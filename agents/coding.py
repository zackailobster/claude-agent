import os
import requests
from dotenv import load_dotenv
from memory.context import load_context, update_context

load_dotenv()

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

def run(question: str) -> str:
    context = load_context("coding")

    messages = [
        {
            "role": "system",
            "content": """你是一個專業的 Python 工程師，專注於行銷自動化、資料處理、API 串接。
回覆規定：
- 禁止出現任何Markdown符號包括**粗體**、#標題、-列表，違反請重寫，只能用純文字和emoji
- 程式碼用 ``` 包住
- 說明文字要簡潔，像在跟同事溝通
- 如果有多個步驟，用數字加 emoji 條列
- 直接給解法，不要廢話"""
        }
    ]

    if context:
        messages.append({
            "role": "user",
            "content": f"[背景記憶] {context}"
        })
        messages.append({
            "role": "assistant",
            "content": "收到，我記得這些背景。"
        })

    messages.append({
        "role": "user",
        "content": question
    })

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "anthropic/claude-sonnet-4-5",
            "messages": messages
        }
    )

    reply = response.json()["choices"][0]["message"]["content"]
    update_context("coding", question, reply)
    return reply
