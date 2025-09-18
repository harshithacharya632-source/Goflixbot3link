# ffmpeg_utils.py
import subprocess, json
from pathlib import Path

def ffprobe_streams(path):
    """Return ffprobe stream info as a dict."""
    cmd = ["ffprobe", "-v", "error", "-show_streams", "-print_format", "json", str(path)]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {p.stderr.decode(errors='ignore')}")
    return json.loads(p.stdout or b"{}")

def run_ffmpeg(cmd):
    """Run ffmpeg command and raise error if fails."""
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {p.stderr.decode(errors='ignore')}")
    return p

def ensure_multi_audio_mp4(input_path, output_dir=None, bitrate="128k"):
    """
    Converts input video to MP4 with all audio tracks in AAC.
    - Keeps original filename (changes only extension to .mp4)
    - Supports multi-language audio
    - Handles videos without audio
    """
    input_path = Path(input_path)
    output_dir = Path(output_dir) if output_dir else input_path.parent
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{input_path.stem}.mp4"

    info = ffprobe_streams(str(input_path))
    audio_streams = [s for s in info.get("streams", []) if s["codec_type"] == "audio"]

    cmd = ["ffmpeg", "-y", "-i", str(input_path)]
    cmd += ["-map", "0:v:0", "-c:v", "copy"]  # copy first video stream

    if audio_streams:
        # Map each audio track individually and transcode to AAC
        for idx, _ in enumerate(audio_streams):
            cmd += ["-map", f"0:a:{idx}", f"-c:a:{idx}", "aac", f"-b:a:{idx}", bitrate]
    # If no audio, just video will be copied

    cmd += ["-movflags", "+faststart", str(output_path)]

    run_ffmpeg(cmd)
    return str(output_path)
