import os
import requests
from flask import Flask, request
from telegram import Update, Bot, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from openai import OpenAI
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

client = OpenAI(api_key=OPENAI_API_KEY)
bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)
telegram_app = Application.builder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎨 سلام! من ربات جیبلی‌ساز هستم.\n"
        "- متن بفرست برای پاسخ هوشمند\n"
        "- /translate برای ترجمه\n"
        "- /summarize برای خلاصه‌سازی\n"
        "- /imagine برای تولید تصویر از متن\n"
        "- عکس بفرست تا به سبک جیبلی بازسازی بشه"
    )

async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("/translate", "").strip()
    if not text:
        await update.message.reply_text("📌 لطفاً متنی برای ترجمه ارسال کن.")
        return
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"ترجمه کن به انگلیسی:\n{text}"}]
        )
        await update.message.reply_text(f"🌍 ترجمه:\n{response.choices[0].message.content}")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در ترجمه.\n{e}")

async def summarize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("/summarize", "").strip()
    if not text:
        await update.message.reply_text("📌 لطفاً متنی برای خلاصه‌سازی ارسال کن.")
        return
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"لطفاً این متن را خلاصه کن:\n{text}"}]
        )
        await update.message.reply_text(f"📄 خلاصه:\n{response.choices[0].message.content}")
    except Exception as e:
        await update.message.reply_text(f"❌ خطا در خلاصه‌سازی.\n{e}")

async def imagine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text.replace("/imagine", "").strip()
    if not prompt:
        await update.message.reply_text("📌 لطفاً یک توضیح برای تصویر بنویس.")
        return
    try:
        response = client.images.generate(
            model="gpt-image-1",
            prompt=f"Ghibli-style illustration: {prompt}",
            size="512x512"
        )
        image_url = response.data[0].url
        image_data = requests.get(image_url).content
        with open("generated.jpg", "wb") as f:
            f.write(image_data)
        await update.message.reply_photo(photo=InputFile("generated.jpg"), caption="🎨 تصویر تولید شد!")
    except Exception as e:
        await update.message.reply_text(f"⚠️ خطا در تولید تصویر.\n{e}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📌 لطفاً از دستورات /translate، /summarize یا /imagine استفاده کن.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✨ دریافت تصویر... (در نسخه بعدی تبدیل به سبک جیبلی فعال می‌شود)")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^/translate"), translate))
telegram_app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^/summarize"), summarize))
telegram_app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^/imagine"), imagine))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
telegram_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    telegram_app.process_update(update)
    return "ok"

if __name__ == "__main__":
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    from waitress import serve
    asyncio.run(telegram_app.initialize())
    serve(app, host="0.0.0.0", port=5000)
