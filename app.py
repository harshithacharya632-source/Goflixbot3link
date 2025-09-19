from flask import Flask, request, send_from_directory, render_template_string
from pathlib import Path
from ffmpeg_utils import generate_hls

app = Flask(__name__)

# Base directories
DOWNLOAD_DIR = Path("downloads")   # where Telegram files are stored
HLS_DIR = Path("hls")              # where HLS outputs are stored
HLS_DIR.mkdir(exist_ok=True)

# HTML player template
PLAYER_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{{ filename }}</title>
</head>
<body style="margin:0;background:#000;display:flex;justify-content:center;align-items:center;height:100vh;">
  <video id="video" controls autoplay width="100%" height="auto" style="max-height:100vh;"></video>
  <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
  <script>
    if (Hls.isSupported()) {
      var video = document.getElementById('video');
      var hls = new Hls();
      hls.loadSource("{{ hls_url }}");
      hls.attachMedia(video);
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
      video.src = "{{ hls_url }}";
    }
  </script>
</body>
</html>
"""

@app.route("/watch/<file_id>/<filename>")
def watch(file_id, filename):
    input_file = DOWNLOAD_DIR / filename
    output_dir = HLS_DIR / file_id
    master_playlist = output_dir / "master.m3u8"

    # Generate HLS if not exists
    if not master_playlist.exists():
        generate_hls(input_file, output_dir)

    hls_url = f"/hls/{file_id}/master.m3u8"
    return render_template_string(PLAYER_TEMPLATE, filename=filename, hls_url=hls_url)

@app.route("/hls/<file_id>/<path:fname>")
def hls_files(file_id, fname):
    return send_from_directory(HLS_DIR / file_id, fname)

@app.route("/download/<file_id>/<filename>")
def download(file_id, filename):
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
