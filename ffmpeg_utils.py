import subprocess
from pathlib import Path
import json

def ffprobe_streams(path):
    """Get streams info as JSON"""
    cmd = ["ffprobe", "-v", "error", "-show_streams", "-print_format", "json", str(path)]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {p.stderr.decode(errors='ignore')}")
    return json.loads(p.stdout or b"{}")


def ensure_multi_audio_mp4(input_path, output_dir="converted"):
    """
    Convert input video/audio to MP4 and **preserve all audio streams** in AAC.
    Output is saved in output_dir.
    Returns output file path.
    """
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"{input_path.stem}_multi_audio.mp4"

    info = ffprobe_streams(input_path)
    has_audio = any(s.get("codec_type") == "audio" for s in info.get("streams", []))

    if has_audio:
        # Map all streams: video + all audio + subtitles if present
        cmd = [
            "ffmpeg", "-y", "-i", str(input_path),
            "-map", "0",  # map all streams
            "-c:v", "copy",
            "-c:a", "aac",  # convert all audio streams to AAC
            "-c:s", "copy", # copy subtitles if any
            "-movflags", "+faststart",
            str(output_path)
        ]
    else:
        # No audio: just copy video
        cmd = [
            "ffmpeg", "-y", "-i", str(input_path),
            "-c:v", "copy",
            "-movflags", "+faststart",
            str(output_path)
        ]

    print("Running FFmpeg:", " ".join(cmd))
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {result.stderr.decode(errors='ignore')}")

    return str(output_path)
