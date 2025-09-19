# File: plugins/start.py

import os
import asyncio
import logging
import subprocess
from pathlib import Path

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ===========================
# Logging
# ===========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===========================
# Helper: Run FFmpeg
# ===========================
def run_ffmpeg(input_path, output_path, bitrate="128k"):
    """
    Convert video ensuring MP4 + AAC audio.
    Keeps all audio tracks.
    """
    input_path = str(input_path)
    output_path = str(Path(output_path).with_suffix(".mp4"))

    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-map", "0:v", "-map", "0:a?",  # all video + all audio
        "-c:v", "copy", "-c:a", "aac", "-b:a", bitrate,
        "-movflags", "+faststart",
        output_path
    ]

    logger.info(f"Running ffmpeg: {' '.join(cmd)}")
    process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if process.returncode != 0:
        err = process.stderr.decode(errors="ignore")
        raise RuntimeError(f"ffmpeg failed: {err}")

    return output_path

# ===========================
# Pyrogram Bot
# ===========================
@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client, message):
    await message.reply_text(
        "👋 Welcome!\n\nSend me a video file (MKV, MP4, etc) "
        "and I’ll give you streaming & download links.",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("📢 Updates", url="https://t.me/trendi_Backup")]]
        )
    )

@Client.on_message(filters.private & (filters.video | filters.document))
async def video_handler(client, message):
    try:
        msg = await message.reply_text("⬇️ Downloading your file...")

        # Download file
        file_path = await message.download()
        logger.info(f"Downloaded file: {file_path}")

        # Output path
        output_path = f"converted_{os.path.basename(file_path)}"
        output_path = str(Path(output_path).with_suffix(".mp4"))

        await msg.edit("🎬 Converting with FFmpeg (keeping all audio tracks)...")

        # Run FFmpeg
        loop = asyncio.get_event_loop()
        converted_path = await loop.run_in_executor(None, run_ffmpeg, file_path, output_path)

        await msg.edit("✅ Conversion done! Preparing links...")

        # Generate dummy links (replace with your server)
        file_name = os.path.basename(converted_path)
        base_url = "https://goflixlink.onrender.com/watch"
        stream_link = f"{base_url}/{file_name}"
        download_link = f"{base_url}/{file_name}?download=1"

        # Send buttons
        await message.reply_text(
            f"✅ Your link is ready!\n\n📂 File: {file_name}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("▶️ Stream", url=stream_link)],
                [InlineKeyboardButton("⬇️ Download", url=download_link)]
            ])
        )

        await msg.delete()

        # Cleanup original
        os.remove(file_path)

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        await message.reply_text(f"❌ Error: {e}")
