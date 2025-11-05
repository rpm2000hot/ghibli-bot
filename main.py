import os
import openai
import requests
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # آدرس دامنه یا URL سرویس شما

openai.api_key = OPENAI_API_KEY
bot = Bot(token=BOT_TOKEN)

app = Flask(__name__)

# هندلرهای ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎨 خوش آمدی! عکس یا متن بفرست.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": update.message.text}]
        )
        reply = response.choices[0].message.content
        await update.message.reply_text(reply)
    except:
        await update.message.reply_text("❌ خطا در ارتباط با OpenAI.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✨ دریافت تصویر... (نسخه Webhook هنوز از DALL·E پشتیبانی کامل ندارد)")

# ساخت اپلیکیشن تلگرام
telegram_app = Application.builder().token(BOT_TOKEN).build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
telegram_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

# مسیر دریافت Webhook
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    telegram_app.update_queue.put(update)
    return "ok"

# تنظیم Webhook هنگام اجرا
@app.before_first_request
def set_webhook():
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")

# اجرای Flask روی پورت 5000
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
