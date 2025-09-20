import os
import shutil
import asyncio


async def convert_to_hls(input_file: str, output_dir: str) -> str:
    """
    Convert video/audio file to HLS format with audio preserved.
    Returns path to the master.m3u8 playlist file.
    """
    os.makedirs(output_dir, exist_ok=True)

    # HLS output path
    output_path = os.path.join(output_dir, "master.m3u8")

    # ffmpeg command (keep video + all audio, HLS output)
    cmd = [
        "ffmpeg",
        "-y",                      # overwrite without asking
        "-i", input_file,          # input file
        "-c:v", "copy",            # copy video without re-encoding
        "-c:a", "copy",            # copy audio without re-encoding
        "-f", "hls",               # HLS format
        "-hls_time", "10",         # each segment = 10s
        "-hls_list_size", "0",     # include all segments in playlist
        "-hls_segment_filename", os.path.join(output_dir, "segment_%03d.ts"),
        output_path
    ]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {stderr.decode()}")

    return output_path


def cleanup_temp(path: str):
    """Remove temporary directory safely."""
    try:
        shutil.rmtree(path, ignore_errors=True)
    except Exception as e:
        print(f"⚠️ Cleanup failed: {e}")
