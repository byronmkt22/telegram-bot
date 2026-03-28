"""
Telegram Daily Tech News Bot - Claude AI Powered
Uses Claude with web search to fetch and summarize today's real tech news.
"""

import os
import json
from datetime import datetime, timezone
from urllib.request import urlopen, Request

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# ─── CLAUDE AI NEWS GENERATOR ────────────────────────────────────────────────

def generate_news_message() -> str:
    today = datetime.now(timezone.utc).strftime("%A, %B %d %Y")

    prompt = f"""Today is {today}. Use your web search tool to find today's most important and interesting news stories in these 5 categories:

1. 🤖 AI & Tech
2. 💻 Programming & Dev
3. 📱 Gadgets & Hardware
4. 🔬 Science & Health
5. ⚡ General Technology

Find 2 real stories from the last 3 days, prioritizing the most recent ones

Format the response exactly like this as plain text:

📰 Daily Tech Digest
{today}

🤖 AI & Tech
- Headline here
Summary sentence. — Source Name: URL

- Headline here
Summary sentence. — Source Name: URL

💻 Programming & Dev
- Headline here
Summary sentence. — Source Name: URL

- Headline here
Summary sentence. — Source Name: URL

📱 Gadgets & Hardware
- Headline here
Summary sentence. — Source Name: URL

- Headline here
Summary sentence. — Source Name: URL

🔬 Science & Health
- Headline here
Summary sentence. — Source Name: URL

- Headline here
Summary sentence. — Source Name: URL

⚡ General Technology
- Headline here
Summary sentence. — Source Name: URL

- Headline here
Summary sentence. — Source Name: URL

Stay curious! 🚀

Important rules:
- Use REAL stories from the last 3 days found via web search, newest first
- Plain text only, no HTML tags, no markdown symbols
- Only output the formatted message, nothing else"""
    
    payload = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 2000,
        "tools": [
            {
                "type": "web_search_20250305",
                "name": "web_search"
            }
        ],
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }).encode("utf-8")

    req = Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
        }
    )

    try:
        with urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            # Get the last text block — that's Claude's final formatted response
            last_text = None
            for block in result["content"]:
                if block["type"] == "text":
                    last_text = block["text"]
            if last_text:
                return last_text
        return "❌ Could not generate news digest today."
    except Exception as e:
        print(f"❌ Claude API error: {e}")
        return "❌ Could not generate news digest today. Please try again later."


# ─── TELEGRAM SENDER ────────────────────────────────────────────────────────────

def send_telegram_message(text: str) -> bool:
    # Telegram max message length is 4096 characters
    # Split into chunks if needed
    max_length = 4000
    chunks = []
    
    if len(text) <= max_length:
        chunks = [text]
    else:
        # Split by double newline to avoid breaking mid-section
        paragraphs = text.split("\n\n")
        current_chunk = ""
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) + 2 <= max_length:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
        if current_chunk:
            chunks.append(current_chunk.strip())

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    for chunk in chunks:
        payload = json.dumps({
            "chat_id": TELEGRAM_CHAT_ID,
            "text": chunk,
            "disable_web_page_preview": True,
        }).encode("utf-8")

        req = Request(url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read())
                if not result.get("ok"):
                    print(f"❌ Telegram API error: {result}")
                    return False
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
            return False

    print(f"✅ News digest sent in {len(chunks)} message(s)!")
    return True


# ─── MAIN ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"🤖 Asking Claude to search today's news...")
    message = generate_news_message()
    print("📤 Sending to Telegram...")
    send_telegram_message(message)
