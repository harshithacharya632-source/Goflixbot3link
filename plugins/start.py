import os
from pathlib import Path
from ffmpeg_utils import ensure_multi_audio_mp4

@Client.on_message(filters.private & (filters.document | filters.video))
async def stream_start(client, message):
    file = getattr(message, message.media.value)
    filename = file.file_name
    filesize = humanize.naturalsize(file.file_size)
    fileid = file.file_id
    user_id = message.from_user.id
    username = message.from_user.mention

    # Download file locally first
    download_dir = Path("downloads")
    download_dir.mkdir(exist_ok=True)
    local_path = await client.download_media(message, file_name=download_dir / filename)

    # Convert to MP4 with all audio tracks (multi-language supported)
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

    # Reply to user
    rm = InlineKeyboardMarkup([
        [InlineKeyboardButton("sᴛʀᴇᴀᴍ 🖥", url=stream),
         InlineKeyboardButton("ᴅᴏᴡɴʟᴏᴀᴅ 📥", url=download)]
    ])

    msg_text = """<i><u>𝗬𝗼𝘂𝗿 𝗟𝗶𝗻𝗸 𝗚𝗲𝗻𝗲ʀ𝗮𝘁𝗲𝗱 !</u></i>\n\n
<b>📂 Fɪʟᴇ ɴᴀᴍᴇ :</b> <i>{}</i>\n\n
<b>📦 Fɪʟᴇ ꜱɪᴢᴇ :</b> <i>{}</i>\n\n
<b>🚸 Nᴏᴛᴇ : ʟɪɴᴋ ᴡᴏɴ'ᴛ ᴇxᴘɪʀᴇ 24 HOURS</b>"""

    await message.reply_text(
        text=msg_text.format(
            Path(converted_path).name,
            humanbytes(get_media_file_size(message)),
        ),
        quote=True,
        disable_web_page_preview=True,
        reply_markup=rm,
        parse_mode=enums.ParseMode.HTML
    )

    # Optional: cleanup old downloads to save space
    os.remove(local_path)
