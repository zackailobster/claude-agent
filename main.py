import os
from flask import Flask, request
from dotenv import load_dotenv
import requests
from orchestrator import route

load_dotenv()

app = Flask(__name__)

LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

def reply_to_line(reply_token: str, message: str):
    requests.post(
        "https://api.line.me/v2/bot/message/reply",
        headers={
            "Authorization": f"Bearer {LINE_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "replyToken": reply_token,
            "messages": [{"type": "text", "text": message}]
        }
    )

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    if data:
        for event in data.get("events", []):
            if event.get("type") == "message" and event["message"]["type"] == "text":
                user_message = event["message"]["text"]
                reply_token = event["replyToken"]
                reply = route(user_message)
                if len(reply) > 4999:
                    reply = reply[:4999]
                reply_to_line(reply_token, reply)
    return "OK", 200

@app.route("/", methods=["GET"])
def health():
    return "Agent is running 🚀", 200

if __name__ == "__main__":
    app.run(port=5000, debug=False)
