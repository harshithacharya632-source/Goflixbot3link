def ensure_audio_aac(input_path, output_path, bitrate="128k"):
    """
    Ensures output_path has AAC audio in an MP4 container.
    If input already has AAC audio + MP4, remux fast.
    Otherwise, transcode audio to AAC and copy video.
    If no audio, just copy video into MP4.
    """
    input_path = str(input_path)
    # Always force .mp4 output for compatibility
    output_path = str(Path(output_path).with_suffix(".mp4"))

    codec = first_audio_codec(input_path)

    if codec == "aac":
        # Already AAC – just remux (fast)
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-map", "0:v:0", "-map", "0:a:0?",
            "-c:v", "copy", "-c:a", "copy",
            "-movflags", "+faststart",
            output_path
        ]
    elif codec:  
        # Has audio but not AAC – transcode only audio
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-map", "0:v:0", "-map", "0:a:0",
            "-c:v", "copy", "-c:a", "aac", "-b:a", bitrate,
            "-movflags", "+faststart",
            output_path
        ]
    else:
        # No audio stream – just copy video into mp4
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-map", "0:v:0",
            "-c:v", "copy",
            "-movflags", "+faststart",
            output_path
        ]

    return run_ffmpeg(cmd)
