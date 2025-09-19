import os
import asyncio
import humanize
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ===== CONFIG =====
API_ID = int(os.environ.get("API_ID", "YOUR_API_ID"))
API_HASH = os.environ.get("API_HASH", "YOUR_API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")
URL = os.environ.get("URL", "https://goflixlink.onrender.com")
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1001234567890"))
SHORTLINK = False  # True if using shortlink service

# ===== CLIENT =====
app = Client(
    "MultiAudioBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# ===== START COMMAND =====
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

# ===== HANDLE FILES =====
@app.on_message(filters.private & (filters.video | filters.document))
async def handle_file(client, message):
    media = message.document or message.video
    file_name = media.file_name
    file_size = humanize.naturalsize(media.file_size)

    # Notify user
    processing_msg = await message.reply_text(f"⏳ Processing `{file_name}` ...", parse_mode=enums.ParseMode.MARKDOWN)

    # Create temp directories
    os.makedirs("downloads", exist_ok=True)
    os.makedirs("converted", exist_ok=True)

    input_path = os.path.join("downloads", file_name)
    output_path = os.path.join("converted", file_name)

    # Download file
    await client.download_media(media, file_name=input_path)

    # Convert with FFmpeg preserving all audio tracks
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", input_path,
        "-map", "0:v", "-map", "0:a?",  # video + all audio
        "-c:v", "libx264",
        "-c:a", "aac",
        "-strict", "-2",
        output_path
    ]

    process = await asyncio.create_subprocess_exec(
        *ffmpeg_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        await processing_msg.edit_text(f"❌ Failed to process `{file_name}`\nError: {stderr.decode()}")
        return

    # Generate streaming/download links
    stream_link = f"{URL}/watch/{file_name}"
    download_link = f"{URL}/download/{file_name}"

    # Reply with buttons
    rm = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🖥 Watch Online", url=stream_link)],
            [InlineKeyboardButton("📥 Download", url=download_link)]
        ]
    )

    await processing_msg.edit_text(
        f"✅ Your link is ready!\n\n📂 File: `{file_name}`\n⚙️ Size: `{file_size}`",
        parse_mode=enums.ParseMode.MARKDOWN,
        reply_markup=rm
    )

# ===== RUN BOT =====
if __name__ == "__main__":
    app.run()
