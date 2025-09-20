import os
import asyncio
import subprocess
import shutil
from pathlib import Path

async def convert_to_hls(input_file: str, output_dir: str) -> str:
    """
    Converts a video/audio file to HLS format with multi-audio support.
    
    Args:
        input_file (str): Path to the input media file.
        output_dir (str): Directory where HLS segments and playlist will be saved.

    Returns:
        str: Path to the generated master playlist (.m3u8)
    """
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "master.m3u8")

    # Prepare ffmpeg command
    cmd = [
        "ffmpeg",
        "-i", input_file,
        "-map", "0",               # Map all streams (video + all audio)
        "-c:v", "copy",            # Copy video codec
        "-c:a", "aac",             # Convert audio to AAC
        "-f", "hls",
        "-hls_time", "6",          # Segment length in seconds
        "-hls_playlist_type", "vod",
        "-hls_segment_filename", os.path.join(output_dir, "seg_%03d.ts"),
        output_file
    ]

    # Run FFmpeg asynchronously
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg failed:\n{stderr.decode()}")

    return output_file


def cleanup_temp(path: str):
    """
    Remove a temporary folder safely.
    
    Args:
        path (str): Folder path to remove.
    """
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)
