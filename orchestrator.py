import os
import requests
from dotenv import load_dotenv
from agents.marketing import query as marketing_query, add_keyword, remove_keyword, list_keywords
from agents.coding import run as coding_run
from memory.context import load_context, update_context

load_dotenv()

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

def route(user_message: str) -> str:

    # 關鍵字管理指令，直接攔截不走 LLM
    if user_message.startswith("+關鍵字 "):
        keyword = user_message.replace("+關鍵字 ", "").strip()
        return add_keyword(keyword)

    if user_message.startswith("-關鍵字 "):
        keyword = user_message.replace("-關鍵字 ", "").strip()
        return remove_keyword(keyword)

    if user_message.strip() in ["關鍵字清單", "查看關鍵字", "關鍵字列表"]:
        return list_keywords()

    # 用 LLM 判斷要路由到哪個 agent
    context = load_context("orchestrator")

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "anthropic/claude-haiku-4.5",
            "max_tokens": 50,
            "messages": [
                {
                    "role": "system",
                    "content": """你是一個指令路由器，判斷用戶的訊息應該交給哪個 agent 處理。
只能回覆以下其中一個單詞，不能有其他文字：
- marketing：行銷趨勢、競品分析、社群、廣告、內容策略相關
- coding：寫程式、debug、技術問題、API串接相關
- general：其他閒聊或無法分類的問題"""
                },
                {
                    "role": "user",
                    "content": f"背景：{context}\n\n用戶說：{user_message}"
                }
            ]
        }
    )

    agent_type = response.json()["choices"][0]["message"]["content"].strip().lower()

    # 路由到對應 agent
    if "marketing" in agent_type:
        reply = marketing_query(user_message)
    elif "coding" in agent_type:
        reply = coding_run(user_message)
    else:
        reply = general_reply(user_message, context)

    update_context("orchestrator", user_message, reply)
    return reply

def general_reply(message: str, context: str) -> str:
    messages = [
        {
            "role": "system",
            "content": """你是一個行銷科技助手，協助數位行銷專家處理日常問題。
格式規定：
- 禁止出現任何Markdown符號包括**粗體**、#標題，只能用純文字和emoji
- 簡潔直接，不廢話"""
        }
    ]

    if context:
        messages.append({"role": "user", "content": f"[背景記憶] {context}"})
        messages.append({"role": "assistant", "content": "收到。"})

    messages.append({"role": "user", "content": message})

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
    return response.json()["choices"][0]["message"]["content"]
