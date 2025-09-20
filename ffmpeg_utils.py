async def convert_to_hls(input_file: str, output_dir: str) -> str:
    """
    Convert video/audio file to HLS format while keeping all audio streams.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "master.m3u8")

    # Keep video + ALL audio tracks
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_file,
        "-map", "0:v",           # map all video
        "-map", "0:a",           # map all audio
        "-c:v", "copy",          # copy video
        "-c:a", "copy",          # copy audio (all tracks)
        "-f", "hls",
        "-hls_time", "10",
        "-hls_list_size", "0",
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
