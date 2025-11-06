import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from waitress import serve
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# --- Flask setup ---
app = Flask(__name__)

# --- Telegram setup ---
telegram_app = Application.builder().token(BOT_TOKEN).build()

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎨 سلام! ربات جیبلی‌ساز فعاله ✅")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🗣 گفتی: {update.message.text}")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# --- Flask routes ---
@app.route("/", methods=["GET"])
def home():
    return "✅ Ghibli Bot Webhook is running!", 200

@app.route("/webhook", methods=["POST"])
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return "ok", 200

# --- Set webhook ---
async def set_webhook():
    await telegram_app.bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    print(f"✅ Webhook set to: {WEBHOOK_URL}/webhook")

# --- Main entry ---
if __name__ == "__main__":
    import asyncio
    asyncio.run(set_webhook())
    print("🚀 Starting server on port 8080...")
    serve(app, host="0.0.0.0", port=8080)
