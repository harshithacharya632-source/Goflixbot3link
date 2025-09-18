import os
import asyncio
import random
import humanize
import subprocess
from Script import script
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from info import URL, LOG_CHANNEL, SHORTLINK
from urllib.parse import quote_plus
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size
from TechVJ.util.human_readable import humanbytes
from database.users_chats_db import db
from utils import temp, get_shortlink


# --- Helper: remux with all audio ---
async def ensure_multi_audio(input_path: str, output_path: str):
    """
    Use ffmpeg to keep all audio tracks and convert them to AAC if needed.
    """
    cmd = [
        "ffmpeg", "-i", input_path,
        "-map", "0",              # map all streams (video, audio, subs)
        "-c:v", "copy",           # don't re-encode video
        "-c:a", "aac",            # convert all audio to AAC
        "-b:a", "192k",           # audio bitrate
        "-c:s", "copy",           # keep subtitles
        output_path, "-y"
    ]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await process.communicate()


# --- Start Command ---
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
    return


# --- File Handling ---
@Client.on_message(filters.private & (filters.document | filters.video))
async def stream_start(client, message):
    file = getattr(message, message.media.value)
    fileid = file.file_id
    user_id = message.from_user.id
    username = message.from_user.mention

    # Download to local
    input_path = await client.download_media(fileid)
    output_path = f"{input_path}_fixed.mp4"

    # Run ffmpeg to ensure all audio tracks
    await ensure_multi_audio(input_path, output_path)

    # Forward converted file to LOG_CHANNEL
    log_msg = await client.send_video(
        chat_id=LOG_CHANNEL,
        video=output_path,
        file_name=file.file_name
    )

    # Clean up temp
    try:
        os.remove(input_path)
        os.remove(output_path)
    except:
        pass

    fileName = get_name(log_msg)

    # Generate stream & download links
    if SHORTLINK is False:
        stream = f"{URL}/watch/{str(log_msg.id)}/{quote_plus(fileName)}?hash={get_hash(log_msg)}"
        download = f"{URL}/download/{str(log_msg.id)}/{quote_plus(fileName)}?hash={get_hash(log_msg)}"
    else:
        stream = await get_shortlink(
            f"{URL}/watch/{str(log_msg.id)}/{quote_plus(fileName)}?hash={get_hash(log_msg)}"
        )
        download = await get_shortlink(
            f"{URL}/download/{str(log_msg.id)}/{quote_plus(fileName)}?hash={get_hash(log_msg)}"
        )

    # Log message
    await log_msg.reply_text(
        text=f"•• ʟɪɴᴋ ɢᴇɴᴇʀᴀᴛᴇᴅ ꜰᴏʀ ɪᴅ #{user_id} \n•• ᴜꜱᴇʀɴᴀᴍᴇ : {username} \n\n•• ᖴᎥᒪᗴ Nᗩᗰᴇ : {fileName}",
        quote=True,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [[
                InlineKeyboardButton("🚀 Fast Download 🚀", url=download),
                InlineKeyboardButton("🖥 Watch online 🖥", url=stream)
            ]]
        )
    )

    # Buttons for user
    rm = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("sᴛʀᴇᴀᴍ 🖥", url=stream),
                InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ 📥", url=download)
            ]
        ]
    )

    msg_text = """<i><u>𝗬𝗼𝘂𝗿 𝗟𝗶𝗻𝗸 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 !</u></i>\n\n
<b>📂 Fɪʟᴇ ɴᴀᴍᴇ :</b> <i>{}</i>\n\n
<b>📦 Fɪʟᴇ ꜱɪᴢᴇ :</b> <i>{}</i>\n\n
<b>🚸 Nᴏᴛᴇ : ʟɪɴᴋ ᴡᴏɴ'ᴛ ᴇxᴘɪʀᴇ ᴛɪʟʟ ɪ ᴅᴇʟᴇᴛᴇ</b>"""

    await message.reply_text(
        text=msg_text.format(
            fileName,
            humanbytes(get_media_file_size(message))
        ),
        quote=True,
        disable_web_page_preview=True,
        reply_markup=rm
    )
