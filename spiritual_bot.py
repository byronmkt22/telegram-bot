"""
Telegram Daily Spiritual Bot
Sends a morning blend of Bible verse, inspirational quote, and Stoic wisdom.
"""

import os
import json
import random
from datetime import datetime, timezone
from urllib.request import urlopen, Request

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID_HERE")

# ─── CONTENT POOLS ──────────────────────────────────────────────────────────────

BIBLE_VERSES = [
    ("Jeremiah 29:11", "For I know the plans I have for you, declares the Lord, plans to prosper you and not to harm you, plans to give you hope and a future."),
    ("Philippians 4:13", "I can do all things through Christ who strengthens me."),
    ("Psalm 23:1", "The Lord is my shepherd; I shall not want."),
    ("Isaiah 40:31", "Those who hope in the Lord will renew their strength. They will soar on wings like eagles."),
    ("Proverbs 3:5-6", "Trust in the Lord with all your heart and lean not on your own understanding; in all your ways submit to him, and he will make your paths straight."),
    ("Romans 8:28", "And we know that in all things God works for the good of those who love him."),
    ("Joshua 1:9", "Be strong and courageous. Do not be afraid; do not be discouraged, for the Lord your God will be with you wherever you go."),
    ("Psalm 46:1", "God is our refuge and strength, an ever-present help in trouble."),
    ("Matthew 6:33", "But seek first his kingdom and his righteousness, and all these things will be given to you as well."),
    ("Lamentations 3:22-23", "The steadfast love of the Lord never ceases; his mercies never come to an end; they are new every morning."),
    ("2 Timothy 1:7", "For God has not given us a spirit of fear, but of power and of love and of a sound mind."),
    ("Psalm 118:24", "This is the day that the Lord has made; let us rejoice and be glad in it."),
]

INSPIRATIONAL_QUOTES = [
    ("Maya Angelou", "You will face many defeats in life, but never let yourself be defeated."),
    ("Nelson Mandela", "It always seems impossible until it's done."),
    ("C.S. Lewis", "You are never too old to set another goal or to dream a new dream."),
    ("Mother Teresa", "If you judge people, you have no time to love them."),
    ("Winston Churchill", "Success is not final, failure is not fatal: it is the courage to continue that counts."),
    ("Helen Keller", "Keep your face to the sunshine and you cannot see a shadow."),
    ("Ralph Waldo Emerson", "What lies behind us and what lies before us are tiny matters compared to what lies within us."),
    ("Albert Einstein", "In the middle of every difficulty lies opportunity."),
    ("Rumi", "Yesterday I was clever, so I wanted to change the world. Today I am wise, so I am changing myself."),
    ("Viktor Frankl", "When we are no longer able to change a situation, we are challenged to change ourselves."),
    ("Brené Brown", "Vulnerability is not winning or losing; it's having the courage to show up when you can't control the outcome."),
    ("Martin Luther King Jr.", "Faith is taking the first step even when you don't see the whole staircase."),
]

STOIC_QUOTES = [
    ("Marcus Aurelius", "You have power over your mind, not outside events. Realize this, and you will find strength."),
    ("Epictetus", "It's not what happens to you, but how you react to it that matters."),
    ("Seneca", "We suffer more in imagination than in reality."),
    ("Marcus Aurelius", "The impediment to action advances action. What stands in the way becomes the way."),
    ("Epictetus", "Make the best use of what is in your power, and take the rest as it happens."),
    ("Seneca", "Luck is what happens when preparation meets opportunity."),
    ("Marcus Aurelius", "Very little is needed to make a happy life; it is all within yourself, in your way of thinking."),
    ("Epictetus", "Seek not that the things which happen should happen as you wish; but wish the things which happen to be as they are, and you will have a tranquil flow of life."),
    ("Seneca", "He who fears death will never do anything worthy of a living man."),
    ("Marcus Aurelius", "Do not indulge in dreams of what you have not, but count the blessings actually present."),
    ("Zeno of Citium", "Man conquers the world by conquering himself."),
    ("Seneca", "Begin at once to live, and count each separate day as a separate life."),
]


# ─── MESSAGE BUILDER ────────────────────────────────────────────────────────────

def escape_md(text: str) -> str:
    special = r"\_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{c}" if c in special else c for c in text)


def build_spiritual_message() -> str:
    today = datetime.now(timezone.utc).strftime("%A, %B %d %Y")

    verse_ref, verse_text = random.choice(BIBLE_VERSES)
    insp_author, insp_quote = random.choice(INSPIRATIONAL_QUOTES)
    stoic_author, stoic_quote = random.choice(STOIC_QUOTES)

    lines = [
        "🌅 *Good Morning\\! Here's your daily spiritual boost:*",
        f"_{escape_md(today)}_",
        "",
        "📖 *Bible Verse*",
        f"_{escape_md(verse_text)}_",
        f"— {escape_md(verse_ref)}",
        "",
        "✨ *Inspiration*",
        f"_{escape_md(insp_quote)}_",
        f"— {escape_md(insp_author)}",
        "",
        "🏛️ *Stoic Wisdom*",
        f"_{escape_md(stoic_quote)}_",
        f"— {escape_md(stoic_author)}",
        "",
        "🙏 _Have a blessed and purposeful day\\!_",
    ]

    return "\n".join(lines)


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
    print("🙏 Building spiritual message...")
    message = build_spiritual_message()
    print("📤 Sending to Telegram...")
    send_telegram_message(message)
