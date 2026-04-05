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


def generate_quote_explanation(spanish_quote: str, movie: str) -> str:
    """Generate a brief, meaningful explanation of the quote's importance."""
    
    prompt = f"""La siguiente es una cita espiritual de la película "{movie}":

"{spanish_quote}"

Proporciona UNA explicación breve y poderosa (máximo 2 oraciones) que ayude al lector a entender por qué esta frase es importante y transformadora para la vida cotidiana. Habla directamente al lector, de forma inspiradora y accesible.

Responde ÚNICAMENTE con la explicación, sin prefijos ni explicaciones adicionales."""

    payload = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 200,
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
            return result["content"][0]["text"].strip()
    except Exception as e:
        print(f"⚠️ Could not generate explanation: {e}")
        return "Reflexiona sobre estas palabras y permite que transformen tu perspectiva hoy."


# ─── TELEGRAM SENDER ────────────────────────────────────────────────────────────

def send_telegram_message(text: str) -> bool:
    """Send message to Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
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
    
    print("💭 Generating explanation...")
    explanation = generate_quote_explanation(quote_data['espanol'], quote_data['movie'])
    
    # Get current date in Spanish
    tz = pytz.timezone("America/Chicago")
    now = datetime.now(tz)
    DAYS_ES = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
    MONTHS_ES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                 "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    current_date = f"{DAYS_ES[now.weekday()]}, {now.day} de {MONTHS_ES[now.month-1]} de {now.year}"
    
    # Format message using HTML parse mode
    message = (
        f"🎬 <b>Sabiduría del Cine Espiritual</b>\n"
        f"<i>{current_date}</i>\n\n"
        f"<i>{quote_data['espanol']}</i>\n\n"
        f"— {quote_data['personaje']}\n"
        f"🎥 <b>{quote_data['movie']}</b>\n\n"
        f"🇺🇸 <i>\"{quote_data['original']}\"</i>\n\n"
        f"💫 <b>Por qué importa:</b>\n"
        f"{explanation}\n\n"
        f"✨ <i>Que esta verdad te inspire y guíe tu día.</i>"
    )
    
    print("📤 Sending to Telegram...")
    send_telegram_message(message)
