import subprocess
from pathlib import Path

def run_ffmpeg(cmd):
    process = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if process.returncode != 0:
        raise RuntimeError(
            f"FFmpeg failed:\n{process.stderr.decode(errors='ignore')}"
        )
    return process

def generate_hls(input_path, output_dir):
    """
    Convert input video into HLS with multiple audio tracks.
    """
    input_path = str(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    master_playlist = output_dir / "master.m3u8"

    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-map", "0:v:0", "-c:v", "libx264", "-crf", "20", "-preset", "veryfast",
        "-map", "0:a", "-c:a", "aac", "-b:a", "128k",
        "-map", "0:s?", "-c:s", "copy",
        "-start_number", "0",
        "-hls_time", "6",
        "-hls_list_size", "0",
        "-master_pl_name", "master.m3u8",
        f"{output_dir}/stream_%v.m3u8"
    ]

    run_ffmpeg(cmd)
    return master_playlist
