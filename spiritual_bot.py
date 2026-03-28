"""
Telegram Daily Spiritual Bot
Uses Claude AI to generate a fresh, unique spiritual message every morning.
"""

import os
import json
from datetime import datetime, timezone
from urllib.request import urlopen, Request

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

# ─── CLAUDE AI MESSAGE GENERATOR ────────────────────────────────────────────────

def generate_spiritual_message() -> str:
    today = datetime.now(timezone.utc).strftime("%A, %B %d %Y")

    prompt = f"""Today is {today}. Generate a warm, uplifting morning spiritual message that includes exactly these three sections:

1. 📖 A Bible verse (include the reference, e.g. John 3:16)
2. ✨ An inspirational quote from a known person (include their name)
3. 🏛️ A Stoic wisdom quote (include the philosopher's name)

Format your response exactly like this, ready to send as a Telegram message using MarkdownV2:

🌅 *Good Morning\\! Here's your daily spiritual boost:*
_{today}_

📖 *Bible Verse*
_[verse text]_
— [Book Chapter:Verse]

✨ *Inspiration*
_[quote text]_
— [Author Name]

🏛️ *Stoic Wisdom*
_[quote text]_
— [Philosopher Name]

🙏 _Have a blessed and purposeful day\\!_

Important rules:
- Escape these characters with a backslash in the text: _ * [ ] ( ) ~ ` > # + - = | {{ }} . !
- Do not add any explanation or extra text, just the message itself
- Make it feel fresh, personal and uplifting for the day"""

    payload = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 1000,
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
        with urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            return result["content"][0]["text"]
    except Exception as e:
        print(f"❌ Claude API error: {e}")
        # Fallback message if API fails
        return (
            "🌅 *Good Morning\\!*\n\n"
            "📖 *Bible Verse*\n"
            "_The steadfast love of the Lord never ceases; his mercies never come to an end\\._\n"
            "— Lamentations 3:22\n\n"
            "🙏 _Have a blessed and purposeful day\\!_"
        )


# ─── TELEGRAM SENDER ────────────────────────────────────────────────────────────

def send_telegram_message(text: str) -> bool:
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": True,
    }).encode("utf-8")

    req = Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            if result.get("ok"):
                print("✅ Spiritual message sent!")
                return True
            else:
                print(f"❌ Telegram API error: {result}")
                return False
    except Exception as e:
        print(f"❌ Failed to send message: {e}")
        return False


# ─── MAIN ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🙏 Asking Claude for today's spiritual message...")
    message = generate_spiritual_message()
    print("📤 Sending to Telegram...")
    send_telegram_message(message)
