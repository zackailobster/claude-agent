import os
import json
import requests
from dotenv import load_dotenv
from tools.search import search_platform
from memory.context import load_context, update_context

load_dotenv()

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
KEYWORDS_PATH = "memory/keywords.json"

def load_keywords():
    with open(KEYWORDS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_keywords(data):
    with open(KEYWORDS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_keyword(keyword: str):
    data = load_keywords()
    if keyword not in data["keywords"]:
        data["keywords"].append(keyword)
        save_keywords(data)
        return f"✅ 已新增關鍵字：{keyword}"
    return f"⚠️ 關鍵字已存在：{keyword}"

def remove_keyword(keyword: str):
    data = load_keywords()
    if keyword in data["keywords"]:
        data["keywords"].remove(keyword)
        save_keywords(data)
        return f"🗑️ 已刪除關鍵字：{keyword}"
    return f"⚠️ 找不到關鍵字：{keyword}"

def list_keywords():
    data = load_keywords()
    keywords = data["keywords"]
    if not keywords:
        return "目前沒有監控關鍵字"
    return "📌 目前監控關鍵字：\n" + "\n".join(f"• {k}" for k in keywords)

def fetch_trends(keyword: str) -> list:
    data = load_keywords()
    sources = data["sources"]
    all_results = []
    for source in sources:
        results = search_platform(keyword, source, num=2)
        for r in results:
            r["source"] = source
        all_results.extend(results)
    return all_results

def analyze_with_claude(keyword: str, results: list) -> str:
    if not results:
        return f"找不到關於「{keyword}」的相關內容"

    context = load_context("marketing")

    content = "\n\n".join([
        f"來源：{r['source']}\n標題：{r['title']}\n摘要：{r['snippet']}\n連結：{r['link']}"
        for r in results
    ])

    messages = [
        {
            "role": "system",
            "content": """你是一個專業的數位行銷趨勢分析師。
根據提供的資料，用繁體中文產出一份簡潔有力的趨勢報告。
格式規定，違反即重寫：
- 絕對禁止出現任何Markdown符號包括**粗體**、#標題、-列表，違反請重寫，只能用純文字和emoji
- 標題層次只能用 emoji 表示
- 條列只能用 • 或 emoji 開頭
- 來源平台用（）標註在該條末尾
- 結尾必須有「🎯 行銷人觀點」段落
- 全文控制在 300 字以內
- 文字要流暢，像在跟人說話"""
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
        "content": f"關鍵字：{keyword}\n\n以下是各平台搜尋結果：\n\n{content}"
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
    update_context("marketing", keyword, reply)
    return reply

def run_morning_report() -> str:
    data = load_keywords()
    keywords = data["keywords"]

    if not keywords:
        return "⚠️ 目前沒有設定監控關鍵字"

    report = "🌅 早安！以下是今日行銷趨勢早報\n"
    report += "━━━━━━━━━━━━━━━━\n\n"

    for keyword in keywords:
        results = fetch_trends(keyword)
        analysis = analyze_with_claude(keyword, results)
        report += f"🔍 {keyword}\n\n{analysis}\n\n"
        report += "─────────────────\n\n"

    return report

def query(question: str) -> str:
    results = []
    data = load_keywords()
    for keyword in data["keywords"]:
        r = fetch_trends(keyword)
        results.extend(r)
    reply = analyze_with_claude(question, results)
    update_context("marketing", question, reply)
    return reply
