import os
import asyncio
import ffmpeg


async def ensure_multi_audio_mp4(input_path: str, output_path: str) -> str:
    """
    Convert any video to MP4 (H.264) while keeping ALL audio/subtitle tracks.
    Output will be faststart enabled for streaming.

    :param input_path: Path to input video file
    :param output_path: Path where converted video will be saved
    :return: Path to the converted file
    """
    try:
        # Remove old output file if exists
        if os.path.exists(output_path):
            os.remove(output_path)

        # Build ffmpeg command
        cmd = [
            "ffmpeg",
            "-y",                     # overwrite if file exists
            "-i", input_path,         # input file
            "-map", "0:v",            # include all video tracks
            "-map", "0:a?",           # include all audio tracks
            "-map", "0:s?",           # include all subtitle tracks
            "-c:v", "libx264",        # re-encode video to H.264 for compatibility
            "-c:a", "aac",            # convert audio to AAC
            "-c:s", "copy",           # keep subtitles as is
            "-movflags", "+faststart",# make file streamable
            "-preset", "veryfast",    # faster conversion
            output_path
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(f"ffmpeg error: {stderr.decode()}")

        return output_path

    except Exception as e:
        raise RuntimeError(f"Failed to convert file: {e}")


# For quick testing
if __name__ == "__main__":
    import sys
    import asyncio

    if len(sys.argv) < 3:
        print("Usage: python ffmpeg_utils.py input.mp4 output.mp4")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    asyncio.run(ensure_multi_audio_mp4(input_file, output_file))
    print(f"✅ Conversion complete: {output_file}")
