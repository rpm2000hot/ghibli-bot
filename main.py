import os
import requests
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

BOT_TOKEN = "8073634487:AAEn3ZxqfUYtGCmQm3HoW21HjcdzDgV0ziU"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎨 خوش آمدی به ربات Ghibli! فقط یک عکس بفرست تا آن را به سبک انیمه‌های جیبلی تبدیل کنم."
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = await photo_file.download_as_bytearray()

    # ارسال عکس به API پردازش تصویر (شبیه‌سازی‌شده)
    # در اینجا باید به API واقعی Ghibli-style متصل شوی
    # برای نمونه، فرض می‌کنیم API پاسخ تصویر پردازش‌شده را می‌دهد
    response = requests.post("https://ghibliart.ai/api/process", files={"image": photo_bytes})

    if response.status_code == 200:
        with open("ghibli_result.jpg", "wb") as f:
            f.write(response.content)
        await update.message.reply_photo(photo=InputFile("ghibli_result.jpg"), caption="✨ تصویر شما آماده است!")
    else:
        await update.message.reply_text("متأسفم، مشکلی در پردازش تصویر پیش آمد.")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.run_polling()
