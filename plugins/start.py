import asyncio
import humanize
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from utils import temp, get_shortlink
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size
from ffmpeg_utils import ensure_multi_audio_mp4  # <- our fixed FFmpeg util
from info import URL, LOG_CHANNEL, SHORTLINK
from database.users_chats_db import db

app = Client(
    "TechVJBot",
    api_id=123456,           # <-- Replace with your API_ID
    api_hash="YOUR_API_HASH",# <-- Replace with your API_HASH
    bot_token="YOUR_BOT_TOKEN" # <-- Replace with your bot token
)

# ---------- START COMMAND ----------
@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)

    rm = InlineKeyboardMarkup(
        [[InlineKeyboardButton("✨ Update Channel", url="https://t.me/trendi_Backup")]]
    )

    await message.reply(
        text=(
            f"Hi {message.from_user.mention}!\n"
            f"Welcome to {temp.B_NAME} Bot."
        ),
        reply_markup=rm,
        parse_mode=enums.ParseMode.HTML
    )

# ---------- FILE HANDLER ----------
@app.on_message(filters.private & (filters.document | filters.video))
async def handle_file(client, message):
    # Get the actual file
    if message.video:
        file = message.video
    elif message.document:
        file = message.document
    else:
        await message.reply("Unsupported file type!")
        return

    await message.reply_text("✅ Received file. Converting... please wait.")

    file_path = await client.download_media(file)
    try:
        # Convert with multi-audio support
        converted_path = ensure_multi_audio_mp4(file_path)
    except Exception as e:
        await message.reply_text(f"❌ Conversion failed: {e}")
        return

    # Generate links (if you have URL setup)
    if SHORTLINK:
        stream_link = await get_shortlink(f"{URL}/watch/{file.file_id}/{get_name(file)}")
        download_link = await get_shortlink(f"{URL}/download/{file.file_id}/{get_name(file)}")
    else:
        stream_link = f"{URL}/watch/{file.file_id}/{get_name(file)}"
        download_link = f"{URL}/download/{file.file_id}/{get_name(file)}"

    # Reply with buttons
    rm = InlineKeyboardMarkup([
        [InlineKeyboardButton("🖥 Watch online 🖥", url=stream_link)],
        [InlineKeyboardButton("📥 Download 📥", url=download_link)]
    ])

    await message.reply_document(
        converted_path,
        caption="✅ Here is your multi-audio MP4 file!",
        reply_markup=rm
    )

# ---------- RUN BOT ----------
if __name__ == "__main__":
    print("Bot started...")
    app.run()
