import os
import humanize
import tempfile
from urllib.parse import quote_plus
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.users_chats_db import db
from info import URL, LOG_CHANNEL, SHORTLINK
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size
from utils import temp, get_shortlink
from ffmpeg_utils import convert_to_hls, cleanup_temp
from Script import script


@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    # Debug log
    print("🚀 /start command received:", message.from_user.id)

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


@Client.on_message(filters.private & filters.media)
async def stream_start(client, message):
    # Debug log
    print("📥 Received media message:", message)

    file = getattr(message, message.media.value)
    filename = file.file_name
    filesize = humanize.naturalsize(file.file_size)
    user_id = message.from_user.id
    username = message.from_user.mention

    print(f"➡️ Processing file: {filename} ({filesize}) from user {user_id}")

    # Forward file to LOG_CHANNEL
    log_msg = await client.send_cached_media(
        chat_id=LOG_CHANNEL,
        file_id=file.file_id
    )
    print("✅ Forwarded file to LOG_CHANNEL")

    # Temp folder per file
    tmp_dir = tempfile.mkdtemp()
    file_path = os.path.join(tmp_dir, filename)
    await client.download_media(message, file_path)
    print(f"📂 File downloaded to {file_path}")

    # Convert to HLS
    try:
        hls_file = await convert_to_hls(file_path, os.path.join(tmp_dir, "hls"))
        print(f"🎞 Conversion successful: {hls_file}")
    except Exception as e:
        print("❌ Conversion failed:", e)
        await message.reply_text(f"❌ Error converting file: {e}")
        cleanup_temp(tmp_dir)
        return

    file_name_safe = quote_plus(get_name(log_msg))
    if SHORTLINK:
        stream_url = await get_shortlink(f"{URL}/watch/{log_msg.id}/{file_name_safe}?hash={get_hash(log_msg)}")
        download_url = await get_shortlink(f"{URL}/download/{log_msg.id}/{file_name_safe}?hash={get_hash(log_msg)}")
    else:
        stream_url = f"{URL}/watch/{log_msg.id}/{file_name_safe}?hash={get_hash(log_msg)}"
        download_url = f"{URL}/download/{log_msg.id}/{file_name_safe}?hash={get_hash(log_msg)}"

    print("🔗 Links generated")

    rm = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🚀 Download", url=download_url),
            InlineKeyboardButton("🖥 Watch Online", url=stream_url)
        ]
    ])

    await message.reply_text(
        f"✅ Your link is ready!\n\n📂 File: {filename}\n⚙️ Size: {filesize}\n🎵 Audio: Included ✅",
        reply_markup=rm,
        quote=True
    )
    print("📤 Sent link buttons to user")

    # Cleanup temp files after conversion
    cleanup_temp(tmp_dir)
    print("🧹 Cleaned up temp files")
