# app.py
import os
import subprocess
from flask import Flask, Response, abort, send_file

app = Flask(__name__)
DOWNLOAD_DIR = "downloads"

def get_file_path(file_id, filename):
    return os.path.join(DOWNLOAD_DIR, f"{file_id}_{filename}")

@app.route("/watch/<file_id>/<filename>")
def watch(file_id, filename):
    file_path = get_file_path(file_id, filename)
    if not os.path.exists(file_path):
        return abort(404, "File not found")
    command = [
        "ffmpeg",
        "-i", file_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-f", "mp4",
        "pipe:1"
    ]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return Response(process.stdout, mimetype="video/mp4", direct_passthrough=True)

@app.route("/download/<file_id>/<filename>")
def download(file_id, filename):
    file_path = get_file_path(file_id, filename)
    if not os.path.exists(file_path):
        return abort(404, "File not found")
    return send_file(file_path, as_attachment=True, download_name=filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
