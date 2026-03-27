"""
Telegram Daily Tech News Bot
Fetches RSS feeds across tech topics and sends a formatted digest to Telegram.
"""

import os
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from urllib.request import urlopen, Request
from urllib.error import URLError
import json

# ─── CONFIGURATION ──────────────────────────────────────────────────────────────
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "YOUR_BOT_TOKEN_HERE")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID_HERE")

# Free RSS feeds covering General Tech/AI, Cybersecurity, Programming, Gadgets
RSS_FEEDS = {
    "🤖 AI & General Tech": [
        "https://feeds.feedburner.com/TechCrunch",
        "https://www.theverge.com/rss/index.xml",
    ],
    "🔐 Cybersecurity": [
        "https://feeds.feedburner.com/TheHackersNews",
        "https://www.darkreading.com/rss.xml",
    ],
    "💻 Programming & Dev": [
        "https://dev.to/feed",
        "https://www.infoq.com/feed/",
    ],
    "📱 Gadgets & Hardware": [
        "https://www.engadget.com/rss.xml",
        "https://feeds.arstechnica.com/arstechnica/gadgets",
    ],
}

MAX_ITEMS_PER_CATEGORY = 2   # How many headlines per category
MAX_TITLE_LENGTH = 80        # Truncate long titles


# ─── RSS PARSING ────────────────────────────────────────────────────────────────
def fetch_rss(url: str) -> list[dict]:
    """Fetch and parse an RSS feed, return list of {title, link} dicts."""
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0 TechNewsBot/1.0"})
        with urlopen(req, timeout=10) as resp:
            raw = resp.read()
        root = ET.fromstring(raw)
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        items = []
        # Standard RSS <item> format
        for item in root.iter("item"):
            title_el = item.find("title")
            link_el = item.find("link")
            if title_el is not None and link_el is not None:
                title = (title_el.text or "").strip()
                link = (link_el.text or "").strip()
                if title and link:
                    items.append({"title": title, "link": link})

        # Atom <entry> format (fallback)
        if not items:
            for entry in root.findall(".//atom:entry", ns):
                title_el = entry.find("atom:title", ns)
                link_el = entry.find("atom:link", ns)
                if title_el is not None and link_el is not None:
                    title = (title_el.text or "").strip()
                    link = link_el.get("href", "").strip()
                    if title and link:
                        items.append({"title": title, "link": link})

        return items[:MAX_ITEMS_PER_CATEGORY]

    except (URLError, ET.ParseError, Exception) as e:
        print(f"  ⚠️  Failed to fetch {url}: {e}")
        return []


# ─── MESSAGE BUILDER ────────────────────────────────────────────────────────────
def truncate(text: str, max_len: int) -> str:
    return text if len(text) <= max_len else text[: max_len - 1] + "…"


def build_message() -> str:
    today = datetime.now(timezone.utc).strftime("%A, %B %d %Y")
    lines = [
        f"📰 *Daily Tech Digest*",
        f"_{today}_",
        "",
    ]

    for category, urls in RSS_FEEDS.items():
        items = []
        for url in urls:
            fetched = fetch_rss(url)
            items.extend(fetched)
            if len(items) >= MAX_ITEMS_PER_CATEGORY:
                break
        items = items[:MAX_ITEMS_PER_CATEGORY]

        if not items:
            continue

        lines.append(f"*{category}*")
        for item in items:
            title = truncate(item["title"], MAX_TITLE_LENGTH)
            link = item["link"]
            # Telegram MarkdownV2 requires escaping some chars in plain text
            lines.append(f"• [{escape_md(title)}]({link})")
        lines.append("")

    lines.append("_Stay curious\\! 🚀_")
    return "\n".join(lines)


def escape_md(text: str) -> str:
    """Escape special characters for Telegram MarkdownV2."""
    special = r"\_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{c}" if c in special else c for c in text)


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
                print("✅ Message sent successfully!")
                return True
            else:
                print(f"❌ Telegram API error: {result}")
                return False
    except Exception as e:
        print(f"❌ Failed to send message: {e}")
        return False


# ─── MAIN ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"🤖 Building tech news digest...")
    message = build_message()
    print("📤 Sending to Telegram...")
    send_telegram_message(message)