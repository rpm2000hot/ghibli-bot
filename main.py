import os
import requests
import openai
from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

# دریافت توکن‌ها از محیط امن
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# دستور شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎨 خوش آمدی به ربات جیبلی!\n- عکس بفرست تا به سبک جیبلی تبدیل کنم\n- متن بفرست تا با ChatGPT پاسخ بدم\n- دستور /help برای راهنما"
    )

# دستور راهنما
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 راهنمای استفاده:\n"
        "- عکس بفرست تا به سبک جیبلی تبدیل بشه\n"
        "- متن بفرست تا پاسخ هوشمند بگیری\n"
        "- دستور /start برای شروع دوباره"
    )

# پاسخ به پیام‌های متنی با ChatGPT
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        reply = response.choices[0].message.content
        await update.message.reply_text(reply)
    except Exception:
        await update.message.reply_text("❌ مشکلی در ارتباط با OpenAI پیش آمد.")

# پردازش عکس با FluxAI
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()

        # ارسال به FluxAI برای تبدیل به سبک جیبلی
        response = requests.post(
            "https://fluxai.art/api/ghibli",
            files={"image": ("photo.jpg", photo_bytes)},
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"}
        )

        if response.status_code == 200:
            with open("ghibli_result.jpg", "wb") as f:
                f.write(response.content)
            await update.message.reply_photo(
                photo=InputFile("ghibli_result.jpg"),
                caption="✨ تصویر شما به سبک جیبلی آماده است!"
            )
        else:
            await update.message.reply_text("❌ پردازش تصویر موفق نبود.")
    except Exception:
        await update.message.reply_text("⚠️ خطایی در دریافت یا ارسال تصویر رخ داد.")

# ساخت اپلیکیشن
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

# اجرای ربات
app.run_polling()
