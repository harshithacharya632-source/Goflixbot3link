import os
import shutil
import asyncio
import subprocess
from pathlib import Path

async def convert_to_hls(input_file: str, output_dir: str):
    """
    Convert a video/audio file to HLS format with multi-audio support.
    
    Args:
        input_file (str): Path to the input media file.
        output_dir (str): Path to the directory where HLS segments will be saved.
        
    Returns:
        str: Path to the HLS master playlist.
    """
    os.makedirs(output_dir, exist_ok=True)
    master_playlist = os.path.join(output_dir, "master.m3u8")
    
    # ffmpeg command for HLS with multi-audio support
    cmd = [
        "ffmpeg",
        "-i", input_file,
        "-map", "0:v",               # map all video streams
        "-map", "0:a?",              # map all audio streams if present
        "-c:v", "copy",
        "-c:a", "aac",
        "-f", "hls",
        "-hls_time", "10",
        "-hls_list_size", "0",
        "-hls_segment_filename", os.path.join(output_dir, "segment_%03d.ts"),
        master_playlist
    ]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise Exception(f"FFmpeg failed:\n{stderr.decode()}")

    return master_playlist


def cleanup_temp(temp_dir: str):
    """
    Remove temporary directory and its contents.
    
    Args:
        temp_dir (str): Path to temporary directory.
    """
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)
