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
    Convert input video into HLS keeping ALL audio tracks + subtitles.
    """
    input_path = str(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    master_playlist = output_dir / "master.m3u8"

    cmd = [
        "ffmpeg", "-y", "-i", input_path,

        # Video
        "-map", "0:v:0", "-c:v", "libx264", "-crf", "20", "-preset", "veryfast",

        # All audios
        "-map", "0:a?", "-c:a", "aac", "-b:a", "128k",

        # All subtitles
        "-map", "0:s?", "-c:s", "copy",

        # HLS settings
        "-start_number", "0",
        "-hls_time", "6",
        "-hls_list_size", "0",
        "-f", "hls",

        str(master_playlist)
    ]

    run_ffmpeg(cmd)
    return master_playlist
