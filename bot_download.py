import os
import requests
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Ganti dengan TOKEN bot Telegram milikmu
BOT_TOKEN = "7815728793:AAHsRIbgvrFZBypvezxtp-30fV0gpylBc30"

# Folder penyimpanan sementara
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

async def start(update: Update, context):
    await update.message.reply_text("👋 Halo! Kirim link video atau gambar untuk saya unduh.")

async def process_media(update: Update, context):
    url = update.message.text.strip()

    # Jika URL adalah video dari YouTube, TikTok, Instagram, Twitter, Facebook
    if any(site in url for site in ["youtube.com", "youtu.be", "tiktok.com", "instagram.com", "twitter.com", "facebook.com"]):
        await process_video(update, url)
        return

    # Jika URL adalah gambar (JPG, PNG, GIF, WebP)
    if url.endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
        await process_photo(update, url)
        return

    await update.message.reply_text("❌ Format tidak didukung. Pastikan URL berisi media.")

async def process_video(update: Update, url: str):
    await update.message.reply_text("⏳ Mengunduh video...")

    try:
        ydl_opts = {
            "outtmpl": f"{DOWNLOAD_FOLDER}/%(title)s.%(ext)s",
            "format": "bestvideo+bestaudio/best",
            "noplaylist": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        await update.message.reply_text("✅ Video berhasil diunduh. Mengirim...")
        await update.message.reply_video(video=open(file_path, "rb"))

        # Hapus file setelah dikirim
        os.remove(file_path)

    except Exception as e:
        await update.message.reply_text(f"❌ Gagal mengunduh video. Error: {e}")

async def process_photo(update: Update, url: str):
    await update.message.reply_text("⏳ Mengunduh gambar...")

    try:
        response = requests.get(url)
        if response.status_code == 200:
            file_name = os.path.join(DOWNLOAD_FOLDER, os.path.basename(url))
            with open(file_name, "wb") as file:
                file.write(response.content)

            await update.message.reply_text("✅ Gambar berhasil diunduh. Mengirim...")
            await update.message.reply_photo(photo=open(file_name, "rb"))

            # Hapus file setelah dikirim
            os.remove(file_name)
        else:
            await update.message.reply_text("❌ Gagal mengunduh gambar.")

    except Exception as e:
        await update.message.reply_text(f"❌ Gagal mengunduh gambar. Error: {e}")

async def help_command(update: Update, context):
    help_text = (
        "📌 *Cara Menggunakan Bot:*\n"
        "1️⃣ Kirim link video dari *YouTube, TikTok, Instagram, Twitter, Facebook*.\n"
        "2️⃣ Kirim link gambar dengan format *JPG, PNG, GIF, WebP*.\n"
        "3️⃣ Bot akan mengunduh dan mengirimkan file.\n\n"
        "❓ Jika ada masalah, ketik /help."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Handler command
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    
    # Handler untuk link media
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_media))
    
    print("Bot berjalan...")
    app.run_polling()

if __name__ == "__main__":
    main()
