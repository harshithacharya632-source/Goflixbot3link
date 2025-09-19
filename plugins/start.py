import os
import asyncio
import humanize
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Config
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
URL = os.environ.get("URL", "https://goflixlink.onrender.com")
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL"))
SHORTLINK = False  # Use True if you have shortlink setup

app = Client("MultiAudioBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Start command
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    rm = InlineKeyboardMarkup(
        [[InlineKeyboardButton("✨ Update Channel", url="https://t.me/trendi_Backup")]]
    )
    await message.reply_text(
        f"Hello {message.from_user.mention}! Send me a video or MKV/MP4 file to generate streaming links.",
        reply_markup=rm,
        parse_mode=enums.ParseMode.HTML
    )

# Handle video/document
@app.on_message(filters.private & (filters.video | filters.document))
async def handle_file(client, message):
    media = message.document or message.video
    file_name = media.file_name
    file_size = humanize.naturalsize(media.file_size)

    await message.reply_text(f"⏳ Processing {file_name} ...")

    # Download file to temp
    os.makedirs("downloads", exist_ok=True)
    temp_path = os.path.join("downloads", file_name)
    await client.download_media(media, file_name=temp_path)

    # Convert file using FFmpeg to preserve all audio tracks
    os.makedirs("converted", exist_ok=True)
    output_file = os.path.join("converted", file_name)

    ffmpeg_cmd = [
        "ffmpeg",
        "-i", temp_path,
        "-map", "0:v", "-map", "0:a?",  # keep video and all audio tracks
        "-c:v", "libx264",
        "-c:a", "aac",
        "-strict", "-2",
        output_file
    ]

    process = await asyncio.create_subprocess_exec(
        *ffmpeg_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        await message.reply_text(f"❌ Failed to process the file.\nError: {stderr.decode()}")
        return

    # Generate links (replace with your real server logic)
    stream_link = f"{URL}/watch/{file_name}"
    download_link = f"{URL}/download/{file_name}"

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
