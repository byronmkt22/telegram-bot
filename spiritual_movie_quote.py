"""
Telegram Spiritual Movie Quote Bot - Spanish Edition
Fetches a real spiritual movie quote daily and sends it with translation.
"""

import os
import json
import random
import time
from datetime import datetime
from urllib.request import urlopen, Request
import pytz

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

MOVIES = [
    "The Shack (2017)",
    "Peaceful Warrior (2006)",
    "The Shift (2009)",
]

# ─── CLAUDE AI QUOTE GENERATOR ────────────────────────────────────────────────

def generate_movie_quote() -> dict:
    """Generate a spiritual movie quote with translation."""
    
    movie = random.choice(MOVIES)
    
    prompt = f"""Eres un experto en cine espiritual y emocional, con gran sensibilidad ✨
De la película: "{movie}", proporciona UNA sola frase o cita REAL y memorable que sea profunda y conmovedora.

Primero selecciona una cita poderosa, luego tradúcela al español de forma poética, bella y natural, conservando su esencia emocional y espiritual.

Responde ÚNICAMENTE en este formato exacto, sin emoticones ni texto adicional:
ORIGINAL: [frase original en inglés], {movie}
ESPANOL: [traducción poética al español]
PERSONAJE: [nombre del personaje o "Narrador" si corresponde]"""

    payload = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 500,
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
            response_text = result["content"][0]["text"].strip()
            
            # Parse the response
            quote_data = {
                "original": "",
                "espanol": "",
                "personaje": "",
                "movie": movie
            }
            
            for line in response_text.splitlines():
                if line.startswith("ORIGINAL:"):
                    quote_data["original"] = line.replace("ORIGINAL:", "").strip()
                elif line.startswith("ESPANOL:"):
                    quote_data["espanol"] = line.replace("ESPANOL:", "").strip()
                elif line.startswith("PERSONAJE:"):
                    quote_data["personaje"] = line.replace("PERSONAJE:", "").strip()
            
            return quote_data
            
    except Exception as e:
        print(f"❌ Claude API error: {e}")
        return {
            "original": "The greatest journey is the one within.",
            "espanol": "El viaje más grande es el que ocurre dentro de nosotros.",
            "personaje": "Narrador",
            "movie": movie
        }


# ─── TELEGRAM SENDER ────────────────────────────────────────────────────────────

def send_telegram_message(text: str) -> bool:
    """Send message to Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }).encode("utf-8")

    req = Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            if result.get("ok"):
                print("✅ Spiritual movie quote sent!")
                return True
            else:
                print(f"❌ Telegram API error: {result}")
                return False
    except Exception as e:
        print(f"❌ Failed to send message: {e}")
        return False


# ─── MAIN ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🎬 Asking Claude for a spiritual movie quote...")
    quote_data = generate_movie_quote()
    
    # Get current date in Spanish
    tz = pytz.timezone("America/Chicago")
    now = datetime.now(tz)
    DAYS_ES = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
    MONTHS_ES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                 "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    current_date = f"{DAYS_ES[now.weekday()]}, {now.day} de {MONTHS_ES[now.month-1]} de {now.year}"
    
    # Format message
    message = (
        f"🎬 *Sabiduría del Cine Espiritual*\n"
        f"_{current_date}_\n\n"
        f"_{quote_data['espanol']}_\n\n"
        f"— {quote_data['personaje']}\n"
        f"🎥 *{quote_data['movie']}*\n\n"
        f"🇺🇸 _\\"{quote_data['original']}\\"_\n\n"
        f"✨ _Que esta verdad te inspire y guíe tu día._"
    )
    
    print("📤 Sending to Telegram...")
    send_telegram_message(message)
