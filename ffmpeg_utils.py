import os
import asyncio

async def convert_to_hls(file_path: str, output_dir: str):
    """
    Convert input video to HLS format preserving all audio tracks.
    """
    os.makedirs(output_dir, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-i", file_path,
        "-map", "0",             # Include all streams
        "-c:v", "copy",          # Copy video
        "-c:a", "aac",           # Convert audio to AAC
        "-b:a", "192k",
        "-f", "hls",
        "-hls_time", "10",
        "-hls_list_size", "0",
        "-hls_segment_filename", f"{output_dir}/seg_%03d.ts",
        f"{output_dir}/index.m3u8"
    ]
    process = await asyncio.create_subprocess_exec(*cmd)
    await process.wait()
    return f"{output_dir}/index.m3u8"
