import os
import re
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

ALLOWED_SCHEMES = {"http", "https"}
BLOCKED_HOSTS = {"localhost", "127.0.0.1", "::1"}


def validate_url(value):
    if not isinstance(value, str) or len(value) > 2048:
        return False
    parsed = urlparse(value.strip())
    return (
        parsed.scheme in ALLOWED_SCHEMES
        and bool(parsed.hostname)
        and parsed.hostname.lower() not in BLOCKED_HOSTS
        and "." in parsed.hostname
    )


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "service": "UltraVideoDownloader API"})


@app.post("/api/download")
def download():
    payload = request.get_json(silent=True) or {}
    url = (payload.get("url") or "").strip()
    media_format = payload.get("format", "mp4")
    quality = payload.get("quality", "best")

    if not validate_url(url):
        return jsonify({"error": "Enter a valid public video URL."}), 400
    if media_format not in {"mp4", "mp3"}:
        return jsonify({"error": "Format must be mp4 or mp3."}), 400
    if quality not in {"best", "2160", "1440", "1080", "720", "480", "360"}:
        return jsonify({"error": "Unsupported quality."}), 400

    # This endpoint is intended for personal downloads where the user has permission.
    temp_dir = tempfile.mkdtemp(prefix="uvd-")
    output_template = str(Path(temp_dir) / "%(title).120B-%(id)s.%(ext)s")
    if media_format == "mp3":
        format_selector = "bestaudio/best"
    elif quality == "best":
        format_selector = "bestvideo*+bestaudio/best"
    else:
        format_selector = f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best"

    options = {
        "format": format_selector,
        "outtmpl": output_template,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "max_filesize": 500 * 1024 * 1024,
        "socket_timeout": 20,
        "retries": 2,
        "merge_output_format": "mp4" if media_format == "mp4" else None,
        "postprocessors": (
            [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]
            if media_format == "mp3" else []
        ),
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = Path(ydl.prepare_filename(info))
            if media_format == "mp3":
                file_path = file_path.with_suffix(".mp3")
            elif not file_path.exists():
                candidates = list(Path(temp_dir).glob("*"))
                candidates = [p for p in candidates if p.is_file()]
                if candidates:
                    file_path = candidates[0]

        if not file_path.exists() or not file_path.is_file():
            return jsonify({"error": "The source did not produce a downloadable file."}), 502

        return send_file(
            file_path,
            as_attachment=True,
            download_name=re.sub(r"[^\w. -]", "_", file_path.name)[:180],
            mimetype="audio/mpeg" if media_format == "mp3" else "video/mp4",
        )
    except Exception as exc:
        # Avoid returning internal paths or stack traces to visitors.
        message = str(exc)
        if "Unsupported URL" in message:
            message = "This video source is not supported."
        else:
            message = "Download failed. The source may block downloads or the selected quality may be unavailable."
        return jsonify({"error": message}), 502


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
