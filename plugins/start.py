import asyncio
import humanize
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ffmpeg_utils import ensure_multi_audio_mp4  # <- your FFmpeg multi-audio fix
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size
from utils import temp, get_shortlink
from database.users_chats_db import db
from info import URL, LOG_CHANNEL, SHORTLINK

# ---------- BOT CONFIG ----------
api_id = 123456            # replace with your API_ID
api_hash = "YOUR_API_HASH" # replace with your API_HASH
bot_token = "YOUR_BOT_TOKEN" # replace with your bot token

app = Client("TechVJBot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# ---------- /start COMMAND ----------
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)

    rm = InlineKeyboardMarkup(
        [[InlineKeyboardButton("✨ Update Channel", url="https://t.me/trendi_Backup")]]
    )

    await message.reply_text(
        f"Hi {message.from_user.mention}!\nWelcome to {temp.B_NAME} Bot.",
        reply_markup=rm,
        parse_mode=enums.ParseMode.HTML
    )

# ---------- FILE HANDLER ----------
@app.on_message(filters.private & (filters.document | filters.video))
async def handle_file(client, message):
    file = message.video or message.document
    if not file:
        await message.reply_text("❌ Unsupported file type!")
        return

    await message.reply_text("✅ Received file. Converting to multi-audio MP4...")

    # Download the file
    input_path = await client.download_media(file)

    try:
        # Convert keeping all audio tracks
        output_path = ensure_multi_audio_mp4(input_path)
    except Exception as e:
        await message.reply_text(f"❌ Conversion failed:\n{e}")
        return

    # Generate links (optional)
    if SHORTLINK:
        stream_link = await get_shortlink(f"{URL}/watch/{file.file_id}/{get_name(file)}")
        download_link = await get_shortlink(f"{URL}/download/{file.file_id}/{get_name(file)}")
    else:
        stream_link = f"{URL}/watch/{file.file_id}/{get_name(file)}"
        download_link = f"{URL}/download/{file.file_id}/{get_name(file)}"

    # Reply with converted file
    rm = InlineKeyboardMarkup([
        [InlineKeyboardButton("🖥 Watch online 🖥", url=stream_link)],
        [InlineKeyboardButton("📥 Download 📥", url=download_link)]
    ])

    await message.reply_document(
        output_path,
        caption="✅ Here is your multi-audio MP4 file!",
        reply_markup=rm
    )

# ---------- RUN BOT ----------
if __name__ == "__main__":
    print("Bot is starting...")
    app.run()
