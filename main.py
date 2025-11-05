import os
import openai
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

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

openai.api_key = OPENAI_API_KEY
bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)
telegram_app = Application.builder().token(BOT_TOKEN).build()

# هندلر شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎨 سلام! عکس بفرست تا به سبک جیبلی بازسازی بشه.")

# هندلر متن
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": update.message.text}]
        )
        reply = response.choices[0].message.content
        await update.message.reply_text(reply)
    except Exception:
        await update.message.reply_text("❌ خطا در ارتباط با OpenAI.")

# هندلر عکس
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("🖼️ در حال دریافت تصویر...")

        # دریافت عکس
        photo_file = await update.message.photo[-1].get_file()
        photo_path = await photo_file.download_to_drive("input.jpg")

        # تولید تصویر جدید با سبک جیبلی
        prompt = "A Studio Ghibli-style illustration of a person in a dreamy forest, magical and soft colors"
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"
        )

        image_url = response['data'][0]['url']
        image_data = requests.get(image_url).content

        with open("ghibli_output.jpg", "wb") as f:
            f.write(image_data)

        await update.message.reply_photo(
            photo=InputFile("ghibli_output.jpg"),
            caption="✨ تصویر شما به سبک جیبلی آماده است!"
        )

    except Exception:
        await update.message.reply_text("⚠️ خطا در پردازش تصویر. لطفاً بعداً دوباره تلاش کن.")

# افزودن هندلرها
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
telegram_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

# مسیر Webhook
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    telegram_app.update_queue.put(update)
    return "ok"

# اجرای Flask و تنظیم Webhook
if __name__ == "__main__":
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    app.run(host="0.0.0.0", port=5000)
