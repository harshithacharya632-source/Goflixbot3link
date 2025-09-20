import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ffmpeg_utils import convert_to_hls, cleanup_temp
from utils import get_shortlink, temp


@Client.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        f"Hello {message.from_user.first_name} 👋, My Name Is File to link Goflix\n\n"
        "✏️ I Am An Advanced File Stream Bot With Multiple Player Support And URL Shortener. Best UI Performance.\n\n"
        "Now Send Me A Media To See Magic ✨",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("📢 Join Channel", url="https://t.me/trendi_Backup")]]
        ),
    )


@Client.on_message(filters.video | filters.document)
async def media_handler(client, message):
    # download file
    file_path = await message.download()
    msg = await message.reply_text("⚡ Converting file... Please wait!")

    try:
        # convert to HLS (m3u8)
        output_dir = await convert_to_hls(file_path)

        # create a sample streaming URL
        stream_link = f"https://your-domain.com/stream/{os.path.basename(output_dir)}"
        short_link = await get_shortlink(stream_link)

        # send link back
        await msg.edit_text(
            f"✅ Your File Is Ready!\n\n🎬 [Click Here To Watch Online]({short_link})",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("🚀 Fast Download 🚀", url=short_link)],
                    [InlineKeyboardButton("📢 Join Channel", url="https://t.me/trendi_Backup")],
                ]
            ),
        )
    except Exception as e:
        await msg.edit_text(f"❌ Error: {e}")
    finally:
        # cleanup temp files
        await cleanup_temp(file_path)
