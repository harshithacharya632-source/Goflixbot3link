import os
import humanize
from urllib.parse import quote_plus
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.users_chats_db import db
from utils import temp, get_shortlink
from info import URL, LOG_CHANNEL, SHORTLINK
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size
from TechVJ.util.human_readable import humanbytes
from ffmpeg_utils import convert_to_hls
from Script import script

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(
            LOG_CHANNEL,
            script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention)
        )
    rm = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("✨ Update Channel", url="https://t.me/trendi_Backup")
        ]]
    )
    await client.send_message(
        chat_id=message.from_user.id,
        text=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
        reply_markup=rm,
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.private & (filters.document | filters.video))
async def stream_start(client, message):
    file = getattr(message, message.media.value)
    fileid = file.file_id
    filename = file.file_name
    filesize = humanize.naturalsize(file.file_size)
    user_id = message.from_user.id
    username = message.from_user.mention

    # Forward to LOG_CHANNEL
    log_msg = await client.send_cached_media(
        chat_id=LOG_CHANNEL,
        file_id=fileid,
    )

    file_name_safe = quote_plus(get_name(log_msg))

    # Generate download and stream URLs
    if SHORTLINK:
        stream = await get_shortlink(f"{URL}/watch/{log_msg.id}/{file_name_safe}?hash={get_hash(log_msg)}")
        download = await get_shortlink(f"{URL}/download/{log_msg.id}/{file_name_safe}?hash={get_hash(log_msg)}")
    else:
        stream = f"{URL}/watch/{log_msg.id}/{file_name_safe}?hash={get_hash(log_msg)}"
        download = f"{URL}/download/{log_msg.id}/{file_name_safe}?hash={get_hash(log_msg)}"

    # Convert to HLS for online streaming
    hls_dir = f"./downloads/{log_msg.id}"
    os.makedirs(hls_dir, exist_ok=True)
    file_path = f"./downloads/{log_msg.id}/{filename}"
    await client.download_media(message, file_path)
    hls_file = await convert_to_hls(file_path, hls_dir)

    # Send links
    rm = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🚀 Download", url=download),
            InlineKeyboardButton("🖥 Watch Online", url=stream)
        ]
    ])

    msg_text = (
        f"✅ Your link is ready!\n\n"
        f"📂 File: {filename}\n"
        f"⚙️ Size: {filesize}\n"
        f"🔗 Stream: {stream}\n"
        f"📥 Download: {download}\n"
        f"🎵 Audio: Included ✅\n"
        f"🚨 Note: Links won't expire until deleted."
    )

    await message.reply_text(
        msg_text,
        reply_markup=rm,
        disable_web_page_preview=True,
        quote=True
    )
