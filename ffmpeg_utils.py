# ffmpeg_utils.py
import subprocess, json
from pathlib import Path

def ffprobe_streams(path):
    cmd = ["ffprobe", "-v", "error", "-show_streams", "-print_format", "json", str(path)]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {p.stderr.decode(errors='ignore')}")
    return json.loads(p.stdout or b"{}")

def has_audio_stream(path):
    info = ffprobe_streams(path)
    for s in info.get("streams", []):
        if s.get("codec_type") == "audio":
            return True
    return False

def first_audio_codec(path):
    info = ffprobe_streams(path)
    for s in info.get("streams", []):
        if s.get("codec_type") == "audio":
            return s.get("codec_name", "").lower()
    return ""

def run_ffmpeg(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {p.stderr.decode(errors='ignore')}")
    return p

def ensure_audio_aac(input_path, output_dir=None, bitrate="128k"):
    """
    Ensures output_path has all audio streams in AAC inside an MP4 container,
    keeps original file name, handles multi-language audio, and works if no audio exists.
    """
    input_path = Path(input_path)
    output_dir = Path(output_dir) if output_dir else input_path.parent
    output_path = output_dir / f"{input_path.stem}.mp4"  # preserve original name

    # Probe audio streams
    info = ffprobe_streams(str(input_path))
    audio_streams = [s for s in info.get("streams", []) if s.get("codec_type") == "audio"]

    if not audio_streams:
        # No audio – just copy video
        cmd = [
            "ffmpeg", "-y", "-i", str(input_path),
            "-map", "0:v:0",
            "-c:v", "copy",
            "-movflags", "+faststart",
            str(output_path)
        ]
    else:
        # Map video + all audio streams
        cmd = [
            "ffmpeg", "-y", "-i", str(input_path),
            "-map", "0:v:0",
            "-map", "0:a",               # include all audio tracks
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", bitrate,
            "-movflags", "+faststart",
            str(output_path)
        ]

    run_ffmpeg(cmd)
    return str(output_path)
