import os
import asyncio


async def ensure_multi_audio_mp4(input_path: str, output_path: str) -> str:
    """
    Convert any video to MP4 (H.264) while keeping ALL audio and subtitle tracks.
    Makes output faststart-enabled for streaming.
    """

    try:
        # Remove old output if exists
        if os.path.exists(output_path):
            os.remove(output_path)

        # ffmpeg command
        cmd = [
            "ffmpeg",
            "-y",                     # overwrite if exists
            "-i", input_path,         # input file
            "-map", "0",              # include ALL streams (video+audio+subs)
            "-c:v", "libx264",        # re-encode video for compatibility
            "-c:a", "copy",           # copy ALL audio tracks without loss
            "-c:s", "copy",           # copy ALL subtitle tracks
            "-movflags", "+faststart",# streamable file
            "-preset", "veryfast",    # speed up encoding
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


# Standalone test runner
if __name__ == "__main__":
    import sys
    import asyncio

    if len(sys.argv) < 3:
        print("Usage: python ffmpeg_utils.py input.mkv output.mp4")
        sys.exit(1)

    in_file = sys.argv[1]
    out_file = sys.argv[2]

    asyncio.run(ensure_multi_audio_mp4(in_file, out_file))
    print(f"✅ Done: {out_file}")
