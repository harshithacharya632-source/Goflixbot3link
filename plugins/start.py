from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import URL, LOG_CHANNEL
from urllib.parse import quote_plus
from TechVJ.util.file_properties import get_name, get_hash
from database.users_chats_db import db
from utils import temp


@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
    rm = InlineKeyboardMarkup(
        [[InlineKeyboardButton("✨ Update Channel", url="https://t.me/trendi_Backup")]]
    )
    await client.send_message(
        chat_id=message.from_user.id,
        text="👋 Hello! Send me any video or file to get stream/download links.",
        reply_markup=rm,
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_message(filters.private & (filters.video | filters.document))
async def stream_start(client, message):
    file = getattr(message, message.media.value)
    fileid = file.file_id

    # forward to log channel
    log_msg = await client.send_cached_media(
        chat_id=LOG_CHANNEL,
        file_id=fileid
    )

    filename = get_name(log_msg)
    stream = f"{URL}/watch/{log_msg.id}/{quote_plus(filename)}?hash={get_hash(log_msg)}"
    download = f"{URL}/download/{log_msg.id}/{quote_plus(filename)}?hash={get_hash(log_msg)}"

    # send buttons
    buttons = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("🖥 Stream", url=stream),
            InlineKeyboardButton("📥 Download", url=download)
        ]]
    )

    await message.reply_text(
        f"<b>✅ Your link is ready!</b>\n\n"
        f"📂 <b>File:</b> {filename}\n\n"
        f"🚀 Links won’t expire until deleted.",
        reply_markup=buttons,
        parse_mode=enums.ParseMode.HTML
    )
