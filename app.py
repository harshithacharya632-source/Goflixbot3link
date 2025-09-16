import os
import subprocess
from flask import Flask, Response, abort, send_file

app = Flask(__name__)

# Folder where your bot stores files from Telegram
DOWNLOAD_DIR = "downloads"

def get_file_path(file_id, filename):
    """
    Build the local path for a file using file_id and filename.
    """
    return os.path.join(DOWNLOAD_DIR, f"{file_id}_{filename}")

@app.route("/")
def home():
    return "✅ Goflix Stream Server is running!"

@app.route("/watch/<file_id>/<filename>")
def watch(file_id, filename):
    """
    Stream video with audio transcoded to AAC for browser compatibility.
    """
    file_path = get_file_path(file_id, filename)

    if not os.path.exists(file_path):
        return abort(404, "File not found")

    # FFmpeg command:
    # - Copy video (keep original)
    # - Transcode audio to AAC
    # - Output to MP4 container for HTML5 browser playback
    command = [
        "ffmpeg",
        "-i", file_path,
        "-c:v", "copy",      # keep original video stream
        "-c:a", "aac",       # convert audio to AAC
        "-b:a", "192k",      # set audio bitrate
        "-movflags", "+faststart",
        "-f", "mp4",
        "pipe:1"             # output to stdout
    ]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    return Response(process.stdout, mimetype="video/mp4", direct_passthrough=True)

@app.route("/download/<file_id>/<filename>")
def download(file_id, filename):
    """
    Direct file download without transcoding.
    """
    file_path = get_file_path(file_id, filename)

    if not os.path.exists(file_path):
        return abort(404, "File not found")

    return send_file(file_path, as_attachment=True, download_name=filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
