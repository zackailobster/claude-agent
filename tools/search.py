import os
import requests
from dotenv import load_dotenv

load_dotenv()

SERPER_KEY = os.getenv("SERPER_API_KEY")

def search(query: str, num: int = 5) -> list:
    response = requests.post(
        "https://google.serper.dev/search",
        headers={
            "X-API-KEY": SERPER_KEY,
            "Content-Type": "application/json"
        },
        json={
            "q": query,
            "num": num,
            "hl": "zh-tw",
            "gl": "tw"
        }
    )
    data = response.json()
    results = []
    for item in data.get("organic", []):
        results.append({
            "title": item.get("title"),
            "link": item.get("link"),
            "snippet": item.get("snippet")
        })
    return results

def search_platform(keyword: str, platform: str, num: int = 3) -> list:
    platform_map = {
        "ptt": "site:ptt.cc",
        "dcard": "site:dcard.tw",
        "reddit": "site:reddit.com",
        "threads": "site:threads.net",
        "facebook": "site:facebook.com",
        "新聞": "新聞"
    }
    prefix = platform_map.get(platform, "")
    query = f"{prefix} {keyword}".strip()
    return search(query, num)

