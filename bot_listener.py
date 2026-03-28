"""
Telegram Bot Listener — handles /news command on demand.
Runs persistently on Railway alongside the scheduled GitHub Actions digest.
"""

import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Reuse everything from your existing script
from telegram_news_bot import build_message, send_telegram_message

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responds to /news with a fresh digest."""
    await update.message.reply_text("⏳ Fetching latest news, give me a second...")
    message = build_message()
    await send_telegram_message_async(message, context)


async def send_telegram_message_async(text: str, context: ContextTypes.DEFAULT_TYPE):
    """Send via the bot's own connection (avoids mixing urllib + async)."""
    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=text,
        parse_mode="MarkdownV2",
        disable_web_page_preview=True,
    )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hey! I'm your Daily Tech News Bot.\n\nUse /news to get a fresh digest anytime."
    )


def main():
    print("🤖 Bot listener starting...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("news", news_command))
    print("✅ Listening for commands...")
    app.run_polling()


if __name__ == "__main__":
    main()
