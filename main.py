import os
import openai
import requests
from telegram import Update, InputFile
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
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
        "🎨 خوش آمدی به ربات جیبلی‌ساز!\n"
        "- عکس بفرست تا به سبک جیبلی بازسازی بشه\n"
        "- متن بفرست تا با ChatGPT صحبت کنیم\n"
        "- دستور /help برای راهنما"
    )

# راهنما
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 راهنما:\n"
        "- عکس بفرست تا به سبک جیبلی بازسازی بشه\n"
        "- متن بفرست تا پاسخ هوشمند بگیری\n"
        "- دستور /start برای شروع دوباره"
    )

# پاسخ متنی با ChatGPT
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        reply = response.choices[0].message.content
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(
            "❌ مشکلی در ارتباط با OpenAI پیش آمد.\n"
            "لطفاً کلید API را بررسی کن یا چند دقیقه دیگر دوباره تلاش کن."
        )

# تبدیل عکس به سبک جیبلی با DALL·E
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("🖼️ در حال دریافت تصویر...")

        photo_file = await update.message.photo[-1].get_file()
        photo_path = await photo_file.download_to_drive("input.jpg")

        prompt = "A Studio Ghibli-style illustration of the uploaded photo, dreamy and magical"
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

    except Exception as e:
        await update.message.reply_text(
            "⚠️ خطایی در پردازش تصویر رخ داد.\n"
            "ممکنه کلید OpenAI اشتباه باشه یا مدل تصویر فعال نباشه."
        )

# ساخت اپلیکیشن
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

# اجرای ربات
app.run_polling()
