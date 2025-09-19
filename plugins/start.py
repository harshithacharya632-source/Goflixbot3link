import os
import asyncio
import subprocess
import humanize
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from urllib.parse import quote_plus

# Config
API_ID = int(os.environ.get("API_ID", 12345))
API_HASH = os.environ.get("API_HASH", "your_api_hash")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")
URL = os.environ.get("URL", "https://goflixlink.onrender.com")
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", -1001234567890))
SHORTLINK = False  # Set True if you use shortlink

app = Client("FFMPEGBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Start command
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    rm = InlineKeyboardMarkup(
        [[InlineKeyboardButton("✨ Update Channel", url="https://t.me/trendi_Backup")]]
    )
    await message.reply_text(
        f"Hello {message.from_user.mention}! Send me a video or MKV file to process and stream.",
        reply_markup=rm,
        parse_mode=enums.ParseMode.HTML
    )

# Handle files
@app.on_message(filters.private & (filters.video | filters.document))
async def handle_file(client, message):
    media = message.document or message.video
    file_name = media.file_name
    file_size = humanize.naturalsize(media.file_size)
    file_id = media.file_id

    # Download file
    temp_path = f"downloads/{file_name}"
    os.makedirs("downloads", exist_ok=True)
    await message.reply_text(f"⏳ Downloading {file_name} ...")
    await client.download_media(media, file_name=temp_path)

    # Convert with FFmpeg (multi-audio support)
    output_file = f"converted/{file_name}"
    os.makedirs("converted", exist_ok=True)
    await message.reply_text(f"🔄 Processing {file_name} ... (multi-audio supported)")
    
    ffmpeg_cmd = [
        "ffmpeg", "-i", temp_path,
        "-map", "0:v", "-map", "0:a?",  # preserve all audio tracks
        "-c:v", "libx264",
        "-c:a", "aac",
        "-strict", "-2",
        output_file
    ]
    process = await asyncio.create_subprocess_exec(*ffmpeg_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    await process.communicate()

    # Send links (for simplicity, local path used)
    stream_link = f"{URL}/watch/{quote_plus(file_name)}"
    download_link = f"{URL}/download/{quote_plus(file_name)}"

    rm = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🖥 Watch online", url=stream_link)],
            [InlineKeyboardButton("📥 Download", url=download_link)]
        ]
    )

    await message.reply_text(
        f"✅ Your link is ready!\n\n📂 File: {file_name}\n⚙️ Size: {file_size}",
        reply_markup=rm
    )

if __name__ == "__main__":
    app.run()
