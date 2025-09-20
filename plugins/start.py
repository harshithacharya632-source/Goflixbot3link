import os
import humanize
import tempfile
from urllib.parse import quote_plus
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.users_chats_db import db
from info import URL, LOG_CHANNEL, SHORTLINK
from TechVJ.util.file_properties import get_name, get_hash
from utils import temp, get_shortlink
from utils.ffmpeg_utils import convert_to_hls, cleanup_temp
from Script import script

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(
            LOG_CHANNEL,
            script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention)
        )

    rm = InlineKeyboardMarkup([
        [InlineKeyboardButton("✨ Update Channel", url="https://t.me/trendi_Backup")]
    ])

    await client.send_message(
        chat_id=message.from_user.id,
        text=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
        reply_markup=rm,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(
    filters.private & (filters.document | filters.video | filters.animation | filters.audio)
)
async def stream_start(client, message):
    # Determine file type safely
    if message.document:
        file = message.document
    elif message.video:
        file = message.video
    elif message.audio:
        file = message.audio
    elif message.animation:
        file = message.animation
    else:
        await message.reply_text("❌ Unsupported file type.")
        return

    filename = file.file_name
    filesize = humanize.naturalsize(file.file_size)

    # Forward file to LOG_CHANNEL
    log_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=file.file_id)

    # Create temp folder
    tmp_dir = tempfile.mkdtemp()
    os.makedirs(tmp_dir, exist_ok=True)
    file_path = os.path.join(tmp_dir, filename)
    await client.download_media(message, file_path)

    # Convert to HLS
    try:
        hls_path = os.path.join(tmp_dir, "hls")
        master_playlist = await convert_to_hls(file_path, hls_path)
    except Exception as e:
        await message.reply_text(f"❌ Error converting file: {e}")
        cleanup_temp(tmp_dir)
        return

    # Shortlinks
    file_name_safe = quote_plus(get_name(log_msg))
    if SHORTLINK:
        stream_url = await get_shortlink(f"{URL}/watch/{log_msg.id}/{file_name_safe}?hash={get_hash(log_msg)}")
        download_url = await get_shortlink(f"{URL}/download/{log_msg.id}/{file_name_safe}?hash={get_hash(log_msg)}")
    else:
        stream_url = f"{URL}/watch/{log_msg.id}/{file_name_safe}?hash={get_hash(log_msg)}"
        download_url = f"{URL}/download/{log_msg.id}/{file_name_safe}?hash={get_hash(log_msg)}"

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🚀 Download", url=download_url),
            InlineKeyboardButton("🖥 Watch Online", url=stream_url)
        ]
    ])

    await message.reply_text(
        f"✅ Your file is ready!\n\n📂 File: {filename}\n⚙️ Size: {filesize}\n🎵 Audio: Included ✅",
        reply_markup=buttons,
        quote=True
    )

    # Optionally, cleanup after 5 minutes (if HLS is temporary)
    # asyncio.create_task(async_cleanup(tmp_dir, delay=300))
