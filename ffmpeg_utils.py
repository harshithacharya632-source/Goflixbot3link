import os
import shutil
import asyncio
import subprocess

# Allowed video/audio extensions
ALLOWED_EXTENSIONS = (".mkv", ".mp4", ".mov", ".avi", ".webm", ".flv", ".mp3", ".aac", ".wav", ".ogg")

async def convert_to_hls(input_file: str, output_dir: str) -> str:
    """
    Convert a video/audio file to HLS (.m3u8) format.
    Returns path to the main playlist (.m3u8).
    """
    # Check extension
    if not input_file.lower().endswith(ALLOWED_EXTENSIONS):
        raise ValueError(f"Unsupported file type: {input_file}")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Output HLS playlist path
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    playlist_path = os.path.join(output_dir, f"{base_name}.m3u8")

    # FFmpeg command
    # - Use copy codecs for faster processing if compatible
    # - Handle multi-audio streams
    cmd = [
        "ffmpeg",
        "-y",  # overwrite
        "-i", input_file,
        "-map", "0",  # include all streams
        "-c:v", "libx264",
        "-c:a", "aac",
        "-f", "hls",
        "-hls_time", "10",
        "-hls_playlist_type", "vod",
        "-hls_flags", "delete_segments+temp_file",
        playlist_path
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg failed:\n{stderr.decode()}")

    return playlist_path

def cleanup_temp(temp_dir: str):
    """
    Remove temp directories safely.
    """
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"Error cleaning temp directory {temp_dir}: {e}")
