# ffmpeg_utils.py
import subprocess
from pathlib import Path
import json

def ffprobe_streams(path):
    """
    Returns the streams information of a media file as a JSON dict.
    """
    cmd = ["ffprobe", "-v", "error", "-show_streams", "-print_format", "json", str(path)]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {p.stderr.decode(errors='ignore')}")
    return json.loads(p.stdout or b"{}")

def has_audio_stream(path):
    info = ffprobe_streams(path)
    return any(s.get("codec_type") == "audio" for s in info.get("streams", []))

def ensure_multi_audio_mp4(input_path, bitrate="128k"):
    """
    Converts input media to MP4, keeping all video and audio streams.
    Audio will be transcoded to AAC if not already.
    Returns the output file path.
    """
    input_path = str(input_path)
    output_path = str(Path(input_path).with_suffix(".mp4"))

    # ffprobe info
    info = ffprobe_streams(input_path)
    streams = info.get("streams", [])
    audio_streams = [s for s in streams if s.get("codec_type") == "audio"]

    if not audio_streams:
        # No audio, just copy video
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-c:v", "copy",
            "-movflags", "+faststart",
            output_path
        ]
    else:
        # Map all streams
        cmd = ["ffmpeg", "-y", "-i", input_path]

        # Map all streams explicitly
        cmd += ["-map", "0"]

        # Video: copy
        cmd += ["-c:v", "copy"]

        # Audio: transcode to AAC for compatibility
        cmd += ["-c:a", "aac", "-b:a", bitrate]

        # Faststart for streaming
        cmd += ["-movflags", "+faststart"]

        # Output path
        cmd += [output_path]

    # Run ffmpeg
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {p.stderr.decode(errors='ignore')}")

    return output_path
