# start.py
import os
import humanize
from pathlib import Path
from urllib.parse import quote_plus

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from Script import script
from utils import temp, get_shortlink
from info import URL, LOG_CHANNEL, SHORTLINK
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size
from TechVJ.util.human_readable import humanbytes
from database.users_chats_db import db
from ffmpeg_utils import ensure_multi_audio_mp4

# -------------------------------
# Read credentials from environment
# -------------------------------
BOT_TOKEN = os.environ.get("BOT_TOKEN")
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH")

if not BOT_TOKEN or not API_ID or not API_HASH:
    raise ValueError("Bot credentials are missing. Set BOT_TOKEN, API_ID, and API_HASH as environment variables.")

# -------------------------------
# Initialize Pyrogram client
# -------------------------------
bot = Client(
    "GoflixBot",
    bot_token=BOT_TOKEN,
    api_id=API_ID,
    api_hash=API_HASH
)

# -------------------------------
# /start handler
# -------------------------------
@bot.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(
            LOG_CHANNEL,
            script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention)
        )
    rm = InlineKeyboardMarkup(
        [[InlineKeyboardButton("✨ Update Channel", url="https://t.me/trendi_Backup")]]
    )
    await client.send_message(
        chat_id=message.from_user.id,
        text=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
        reply_markup=rm,
        parse_mode=enums.ParseMode.HTML
    )

# -------------------------------
# File streaming handler
# -------------------------------
@bot.on_message(filters.private & (filters.document | filters.video))
async def stream_start(client, message):
    file = getattr(message, message.media.value)
    filename = file.file_name
    filesize = humanize.naturalsize(file.file_size)
    fileid = file.file_id
    user_id = message.from_user.id
    username = message.from_user.mention

    # Download file locally
    download_dir = Path("downloads")
    download_dir.mkdir(exist_ok=True)
    local_path = await client.download_media(message, file_name=download_dir / filename)

    # Convert to MP4 with all audio tracks
    converted_dir = Path("converted")
    converted_dir.mkdir(exist_ok=True)
    converted_path = ensure_multi_audio_mp4(local_path, output_dir=converted_dir)

    # Forward original file to LOG_CHANNEL (optional)
    log_msg = await client.send_cached_media(
        chat_id=LOG_CHANNEL,
        file_id=fileid,
    )

    fileName = get_name(log_msg)

    # Generate stream & download links
    if SHORTLINK is False:
        stream = f"{URL}/watch/{str(log_msg.id)}/{quote_plus(Path(converted_path).name)}?hash={get_hash(log_msg)}"
        download = f"{URL}/download/{str(log_msg.id)}/{quote_plus(Path(converted_path).name)}?hash={get_hash(log_msg)}"
    else:
        stream = await get_shortlink(
            f"{URL}/watch/{str(log_msg.id)}/{quote_plus(Path(converted_path).name)}?hash={get_hash(log_msg)}"
        )
        download = await get_shortlink(
            f"{URL}/download/{str(log_msg.id)}/{quote_plus(Path(converted_path).name)}?hash={get_hash(log_msg)}"
        )

    # Buttons for user
    rm = InlineKeyboardMarkup([
        [InlineKeyboardButton("sᴛʀᴇᴀᴍ 🖥", url=stream),
         InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ 📥", url=download)]
    ])

    # Message text
    msg_text = f"""<i><u>𝗬𝗼𝘂𝗿 𝗟𝗶𝗻𝗸 𝗚𝗲𝗻𝗲ʀ𝗮ᴛ𝗲𝗱 !</u></i>\n\n
<b>📂 Fɪʟᴇ ɴᴀᴍᴇ :</b> <i>{Path(converted_path).name}</i>\n
<b>📦 Fɪʟᴇ ꜱɪᴢᴇ :</b> <i>{humanbytes(get_media_file_size(message))}</i>\n
<b>🚸 Nᴏᴛᴇ : ʟɪɴᴋ ᴡᴏɴ'ᴛ ᴇxᴘɪʀᴇ 24 HOURS</b>"""

    await message.reply_text(
        text=msg_text,
        quote=True,
        disable_web_page_preview=True,
        reply_markup=rm,
        parse_mode=enums.ParseMode.HTML
    )

    # Clean up downloaded file to save space
    os.remove(local_path)

# -------------------------------
# Run the bot
# -------------------------------
bot.run()
