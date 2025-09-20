import os
import asyncio
import logging

logger = logging.getLogger(__name__)

TEMP_DIR = "temp"  # folder for HLS/MP4
os.makedirs(TEMP_DIR, exist_ok=True)


async def convert_to_hls(input_file: str, output_name: str) -> str:
    """
    Convert video to HLS (.m3u8) format asynchronously.
    Returns the path to the generated .m3u8 file.
    """
    output_dir = os.path.join(TEMP_DIR, output_name)
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "index.m3u8")

    # ✅ Skip if already exists
    if os.path.exists(output_path):
        logger.info(f"HLS already exists for {input_file}")
        return output_path

    cmd = [
        "ffmpeg", "-i", input_file,
        "-c:v", "libx264", "-c:a", "aac",
        "-preset", "veryfast", "-f", "hls",
        "-hls_time", "10", "-hls_playlist_type", "vod",
        output_path
    ]

    logger.info(f"Running FFmpeg: {' '.join(cmd)}")

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        logger.error(f"FFmpeg failed: {stderr.decode()}")
        raise Exception("FFmpeg conversion failed")

    return output_path


async def convert_to_mp4(input_file: str, output_name: str) -> str:
    """
    Convert video to MP4 format asynchronously.
    Returns the path to the generated MP4 file.
    """
    output_path = os.path.join(TEMP_DIR, f"{output_name}.mp4")

    # ✅ Skip if already exists
    if os.path.exists(output_path):
        logger.info(f"MP4 already exists for {input_file}")
        return output_path

    cmd = [
        "ffmpeg", "-i", input_file,
        "-c:v", "libx264", "-c:a", "aac",
        "-preset", "veryfast", "-movflags", "+faststart",
        output_path
    ]

    logger.info(f"Running FFmpeg: {' '.join(cmd)}")

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        logger.error(f"FFmpeg failed: {stderr.decode()}")
        raise Exception("FFmpeg conversion failed")

    return output_path


def cleanup_temp():
    """ Delete all files in temp folder """
    import shutil
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
        os.makedirs(TEMP_DIR, exist_ok=True)
        logger.info("Temp folder cleaned.")
