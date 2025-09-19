import os
import asyncio
import humanize
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from urllib.parse import quote_plus
import subprocess

API_ID = int(os.environ.get("API_ID", "YOUR_API_ID"))
API_HASH = os.environ.get("API_HASH", "YOUR_API_HASH"))
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN"))
URL = os.environ.get("URL", "https://goflixlink.onrender.com")
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1001234567890"))

app = Client(
    "MultiAudioBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

async def convert_to_hls(file_path, output_dir):
    """Convert video to HLS (m3u8) with all audio tracks."""
    os.makedirs(output_dir, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-i", file_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-map", "0",
        "-f", "hls",
        "-hls_time", "10",
        "-hls_list_size", "0",
        "-hls_segment_filename", f"{output_dir}/seg_%03d.ts",
        f"{output_dir}/index.m3u8"
    ]
    process = await asyncio.create_subprocess_exec(*cmd)
    await process.wait()

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    rm = InlineKeyboardMarkup([[InlineKeyboardButton("✨ Update Channel", url="https://t.me/trendi_Backup")]])
    await message.reply_text(
        f"Hello {message.from_user.mention}!\nSend me a video/MKV file to generate streaming links.",
        reply_markup=rm,
        parse_mode=enums.ParseMode.HTML
    )

@app.on_message(filters.private & (filters.video | filters.document))
async def handle_file(client, message):
    media = message.document or message.video
    file_name = media.file_name
    file_size = humanize.naturalsize(media.file_size)

    # Acknowledge user
    processing_msg = await message.reply_text(f"⏳ Processing `{file_name}` ...", parse_mode=enums.ParseMode.MARKDOWN)

    # Download file locally for conversion
    download_path = f"downloads/{file_name}"
    os.makedirs("downloads", exist_ok=True)
    await client.download_media(media, download_path)

    # Convert to HLS in background
    hls_dir = f"hls/{os.path.splitext(file_name)[0]}"
    asyncio.create_task(convert_to_hls(download_path, hls_dir))

    # Generate streaming links (player-ready)
    stream_link = f"{URL}/hls/{quote_plus(os.path.splitext(file_name)[0])}/index.m3u8"
    download_link = f"{URL}/download/{quote_plus(file_name)}"

    # Send links to user
    rm = InlineKeyboardMarkup([
        [InlineKeyboardButton("🖥 Watch Online", url=stream_link)],
        [InlineKeyboardButton("📥 Download", url=download_link)]
    ])
    await processing_msg.edit_text(
        f"✅ Your links are ready!\n\n📂 File: `{file_name}`\n⚙️ Size: `{file_size}`\n\n⚠️ Streaming may start after conversion completes (few minutes for large files).",
        parse_mode=enums.ParseMode.MARKDOWN,
        reply_markup=rm
    )

if __name__ == "__main__":
    app.run()
