import os
import asyncio
import shutil

async def convert_to_hls(input_file: str, output_dir: str) -> str:
    """
    Converts a video/audio file to HLS format with all audio tracks preserved.
    Returns the path to the master playlist (.m3u8).
    """
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "index.m3u8")

    cmd = [
        "ffmpeg",
        "-i", input_file,
        "-codec:", "copy",
        "-start_number", "0",
        "-hls_time", "10",
        "-hls_list_size", "0",
        "-f", "hls",
        output_file
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        print(f"[FFMPEG ERROR] {stderr.decode()}")
        raise Exception("FFmpeg conversion failed!")

    return output_file

# Optional: cleanup temp folders
def cleanup_temp(path: str):
    if os.path.exists(path):
        shutil.rmtree(path)
