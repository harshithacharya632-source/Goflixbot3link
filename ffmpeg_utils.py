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

def ensure_audio_aac(input_path, output_path, bitrate="128k"):
    """
    Ensures output_path has AAC audio inside an mp4 container.
    If input already has AAC audio and container is mp4, it will remux (copy audio).
    Otherwise it will transcode audio to AAC and copy video.
    """
    input_path = str(input_path)
    output_path = str(output_path)
    codec = first_audio_codec(input_path)
    out_suffix = Path(output_path).suffix.lower()
    # If already AAC and mp4-like, just remux (fast)
    if codec == "aac" and out_suffix in (".mp4", ".m4v"):
        cmd = ["ffmpeg", "-y", "-i", input_path, "-map", "0", "-c:v", "copy", "-c:a", "copy", output_path]
    else:
        # Force AAC audio
        cmd = ["ffmpeg", "-y", "-i", input_path, "-map", "0", "-c:v", "copy", "-c:a", "aac", "-b:a", bitrate, output_path]
    return run_ffmpeg(cmd)
