import os
import shutil
import asyncio
import subprocess
from pathlib import Path

async def convert_to_hls(input_file: str, output_dir: str):
    """
    Convert any media file to HLS format with multiple audio tracks support.
    Returns the path to the main playlist.m3u8.
    """
    os.makedirs(output_dir, exist_ok=True)

    input_path = Path(input_file)
    output_path = Path(output_dir) / "playlist.m3u8"

    # FFmpeg command: multi-audio HLS
    cmd = [
        "ffmpeg",
        "-i", str(input_path),
        "-codec:", "copy",       # copy streams without re-encoding
        "-map", "0",             # map all streams
        "-f", "hls",
        "-hls_time", "10",
        "-hls_playlist_type", "vod",
        "-hls_segment_filename", str(Path(output_dir) / "segment_%03d.ts"),
        str(output_path)
    ]

    # Run FFmpeg asynchronously
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg failed:\n{stderr.decode()}")

    return str(output_path)


def cleanup_temp(temp_dir: str):
    """Remove temporary folder and all its files."""
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)
