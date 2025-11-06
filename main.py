import os
import requests
from flask import Flask, request
from telegram import Update, Bot, InputFile
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from openai import OpenAI
from waitress import serve

# 🔑 تنظیم متغیرهای محیطی
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# 📦 اتصال به APIها
client = OpenAI(api_key=OPENAI_API_KEY)
bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)

# 📱 ساخت اپلیکیشن تلگرام
telegram_app = Application.builder().token(BOT_TOKEN).build()

# 🎯 فرمان /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎨 سلام! من ربات جیبلی‌ساز هستم.\n"
        "- متن بفرست برای پاسخ هوشمند\n"
        "- /translate برای ترجمه\n"
        "- /summarize برای خلاصه‌سازی\n"
        "- /imagine برای تولید تصویر از متن\n"
        "- عکس بفرست تا به سبک جیبلی بازسازی بشه"
    )

# 🌍 ترجمه
async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("/translate", "").strip()
    if not text:
        await update.message.reply_text("📌 لطفاً متنی برای ترجمه ارسال کن.")
        return

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"ترجمه کن به انگلیسی:\n{text}"}]
        )
        translated = response.choices[0].message.content
        await update.message.reply_text(f"🌍 ترجمه:\n{translated}")
    except Exception as e:
        await update.message.reply_text("❌ خطا در ترجمه.")

# 📄 خلاصه‌سازی
async def summarize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("/summarize", "").strip()
    if not text:
        await update.message.reply_text("📌 لطفاً متنی برای خلاصه‌سازی ارسال کن.")
        return

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"لطفاً این متن را خلاصه کن:\n{text}"}]
        )
        summary = response.choices[0].message.content
        await update.message.reply_text(f"📄 خلاصه:\n{summary}")
    except Exception:
        await update.message.reply_text("❌ خطا در خلاصه‌سازی.")

# 🎨 تولید تصویر
async def imagine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text.replace("/imagine", "").strip()
    if not prompt:
        await update.message.reply_text("📌 لطفاً یک توضیح برای تصویر بنویس.")
        return

    try:
        result = client.images.generate(
            model="gpt-image-1",
            prompt=f"Ghibli-style illustration of: {prompt}",
            size="512x512"
        )
        image_url = result.data[0].url
        image_data = requests.get(image_url).content
        with open("generated.jpg", "wb") as f:
            f.write(image_data)
        await update.message.reply_photo(photo=InputFile("generated.jpg"), caption="🎨 تصویر تولید شد!")
    except Exception:
        await update.message.reply_text("⚠️ خطا در تولید تصویر.")

# 🗣 پاسخ به متن‌های دیگر
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📌 لطفاً از دستورات /translate، /summarize یا /imagine استفاده کن.")

# 🖼 پاسخ به عکس
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✨ دریافت تصویر... (در نسخه بعدی تبدیل به سبک جیبلی فعال می‌شود)")

# 📌 ثبت هندلرها
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^/translate"), translate))
telegram_app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^/summarize"), summarize))
telegram_app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^/imagine"), imagine))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
telegram_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

# 🌐 وب‌هوک برای Render
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    telegram_app.update_queue.put(update)
    return "ok"

# 🚀 اجرای سرور
if __name__ == "__main__":
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    serve(app, host="0.0.0.0", port=5000)
