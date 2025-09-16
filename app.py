import os
import subprocess
from flask import Flask, Response, abort, send_file

app = Flask(__name__)

DOWNLOAD_DIR = "downloads"
TRANSCODE_DIR = "transcoded"  # Pre-transcoded files go here

# Ensure transcoded directory exists
os.makedirs(TRANSCODE_DIR, exist_ok=True)

def get_file_path(file_id, filename):
    return os.path.join(DOWNLOAD_DIR, f"{file_id}_{filename}")

def get_transcoded_path(file_id, filename):
    name, _ = os.path.splitext(filename)
    return os.path.join(TRANSCODE_DIR, f"{file_id}_{name}.mp4")

def pre_transcode(file_id, filename):
    """
    Transcode audio to AAC for browser playback.
    Returns path to transcoded file.
    """
    input_path = get_file_path(file_id, filename)
    output_path = get_transcoded_path(file_id, filename)

    if not os.path.exists(output_path):
        # FFmpeg command: copy video, convert audio to AAC
        command = [
            "ffmpeg",
            "-i", input_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-movflags", "+faststart",
            output_path
        ]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_path

@app.route("/")
def home():
    return "✅ Goflix Stream Server is running!"

@app.route("/watch/<file_id>/<filename>")
def watch(file_id, filename):
    """
    Serve pre-transcoded MP4 for streaming.
    """
    transcoded_path = pre_transcode(file_id, filename)
    if not os.path.exists(transcoded_path):
        return abort(404, "File not found")
    return send_file(transcoded_path, mimetype="video/mp4")

@app.route("/download/<file_id>/<filename>")
def download(file_id, filename):
    """
    Serve original file for download.
    """
    file_path = get_file_path(file_id, filename)
    if not os.path.exists(file_path):
        return abort(404, "File not found")
    return send_file(file_path, as_attachment=True, download_name=filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
