import logging
import os
import torch
from PIL import Image
from io import BytesIO
from torchvision import transforms
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from animegan2_pytorch import Generator
import requests

# 🔐 توکن ربات تلگرام
TOKEN = "8073634487:AAEn3ZxqfUYtGCmQm3HoW21HjcdzDgV0ziU"

# 📦 مسیر و لینک مدل
MODEL_PATH = "paprika.pt"
MODEL_URL = "https://huggingface.co/vumichien/AnimeGANv2_Paprika/resolve/main/paprika.pt"

# 📥 دانلود مدل در صورت نیاز
def download_model():
    if not os.path.exists(MODEL_PATH):
        print("📥 در حال دانلود مدل AnimeGANv2...")
        response = requests.get(MODEL_URL)
        with open(MODEL_PATH, "wb") as f:
            f.write(response.content)
        print("✅ مدل دانلود شد.")

# 🧠 بارگذاری مدل
download_model()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = Generator().to(device)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.eval()

# 🎨 تبدیل تصویر به انیمه
def convert_to_anime(image: Image.Image) -> BytesIO:
    transform = transforms.Compose([
        transforms.Resize((512, 512)),
        transforms.ToTensor(),
    ])
    input_tensor = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        output_tensor = model(input_tensor)[0].cpu()
    output_image = transforms.ToPILImage()(output_tensor.clamp(0, 1))

    output_bytes = BytesIO()
    output_image.save(output_bytes, format='JPEG')
    output_bytes.seek(0)
    return output_bytes

# 🤖 هندلرهای ربات
def start(update: Update, context: CallbackContext):
    update.message.reply_text("سلام! عکس بفرست تا به سبک انیمه جیبلی تبدیلش کنم 🎨")

def handle_photo(update: Update, context: CallbackContext):
    photo_file = update.message.photo[-1].get_file()
    photo_bytes = BytesIO()
    photo_file.download(out=photo_bytes)
    photo_bytes.seek(0)

    image = Image.open(photo_bytes).convert("RGB")
    anime_image = convert_to_anime(image)

    update.message.reply_photo(photo=anime_image, caption="✨ تصویر انیمه‌شده آماده‌ست!")

# 🚀 اجرای ربات
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
