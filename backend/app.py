"""UltraVideoDownloader API.

Designed for long and large videos: downloads run as background jobs
(no request timeout), with live progress, no file-size cap by default,
and files saved to a local folder.

Environment variables:
  PORT                  port to listen on (default 10000)
  UVD_HOST              host to bind (default 127.0.0.1, local only)
  UVD_DOWNLOAD_DIR      where files are saved (default ./downloads)
  UVD_MAX_FILESIZE_MB   0 = unlimited (default)
  UVD_ALLOWED_ORIGINS   extra website origins allowed to talk to this local app,
                        comma-separated (e.g. https://mydomain.com)
"""
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
import uuid
import webbrowser
from pathlib import Path
from urllib.parse import urlparse

import yt_dlp
from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS

FROZEN = getattr(sys, "frozen", False)  # True inside the packaged app

# A windowed Windows app has no console: stdout/stderr are None and printing would crash.
for _stream in ("stdout", "stderr"):
    if getattr(sys, _stream) is None:
        setattr(sys, _stream, open(os.devnull, "w"))

if FROZEN:
    # Packaged app: index.html is bundled; save files in the user's Downloads folder.
    FRONTEND_DIR = Path(sys._MEIPASS)
    DEFAULT_DOWNLOADS = Path.home() / "Downloads" / "UltraVideoDownloader"
else:
    BASE_DIR = Path(__file__).resolve().parent
    FRONTEND_DIR = BASE_DIR.parent
    DEFAULT_DOWNLOADS = BASE_DIR / "downloads"
DOWNLOAD_DIR = Path(os.environ.get("UVD_DOWNLOAD_DIR", DEFAULT_DOWNLOADS)).resolve()
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_FILESIZE_MB = int(os.environ.get("UVD_MAX_FILESIZE_MB", "0"))

app = Flask(__name__)

# Websites allowed to control this local app. Anything else is rejected, so a random
# website you visit cannot start downloads on your computer.
LOCAL_ORIGIN_RE = r"http://(localhost|127\.0\.0\.1)(:\d+)?"
SITE_ORIGINS = ["https://ultravideodownloader.oussamakhouya73.workers.dev"]  # your site (add a custom domain here if you get one)
EXTRA_ORIGINS = [o.strip() for o in os.environ.get("UVD_ALLOWED_ORIGINS", "").split(",") if o.strip()]
ALLOWED_ORIGINS = SITE_ORIGINS + EXTRA_ORIGINS


def origin_allowed(origin):
    return bool(re.fullmatch(LOCAL_ORIGIN_RE, origin)) or origin in ALLOWED_ORIGINS


# Registered BEFORE CORS() so it runs after flask-cors and has the final say on this header.
@app.after_request
def allow_private_network(resp):
    # Lets a public HTTPS website reach this app on localhost (Chrome/Edge requirement).
    if request.headers.get("Access-Control-Request-Private-Network") == "true":
        resp.headers["Access-Control-Allow-Private-Network"] = "true"
    return resp


CORS(app, resources={r"/api/*": {"origins": [LOCAL_ORIGIN_RE] + ALLOWED_ORIGINS}})


@app.before_request
def check_origin():
    if request.path.startswith("/api/"):
        origin = request.headers.get("Origin")
        if origin and not origin_allowed(origin):
            return jsonify({"error": "Origin not allowed."}), 403


app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

ALLOWED_SCHEMES = {"http", "https"}
BLOCKED_HOSTS = {"localhost", "127.0.0.1", "::1"}
QUALITIES = {"best", "2160", "1440", "1080", "720", "480", "360"}

JOBS = {}
JOBS_LOCK = threading.Lock()


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


def find_ffmpeg():
    """Use the system ffmpeg if present, else the one bundled by imageio-ffmpeg."""
    if os.environ.get("UVD_FFMPEG"):
        return os.environ["UVD_FFMPEG"]
    if shutil.which("ffmpeg"):
        return None  # yt-dlp finds it on PATH
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:  # noqa: BLE001
        return None


def build_options(job_dir, media_format, quality, on_progress):
    if media_format == "mp3":
        selector = "bestaudio/best"
    elif quality == "best":
        selector = "bestvideo*+bestaudio/best"
    else:
        selector = f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best"

    options = {
        "format": selector,
        "outtmpl": str(job_dir / "%(title).120B-%(id)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "socket_timeout": 30,
        "retries": 10,
        "fragment_retries": 10,
        "continuedl": True,
        "concurrent_fragment_downloads": 4,
        "progress_hooks": [on_progress],
        "merge_output_format": "mp4" if media_format == "mp4" else None,
        "postprocessors": (
            [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]
            if media_format == "mp3" else []
        ),
    }
    ffmpeg = find_ffmpeg()
    if ffmpeg:
        options["ffmpeg_location"] = ffmpeg
    if MAX_FILESIZE_MB > 0:
        options["max_filesize"] = MAX_FILESIZE_MB * 1024 * 1024
    return options


def update_job(job_id, **fields):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if job:
            job.update(fields)


def run_job(job_id, url, media_format, quality):
    job_dir = DOWNLOAD_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    expected_streams = 2 if media_format == "mp4" else 1
    seen_streams = []

    def on_progress(d):
        if d.get("status") == "downloading":
            name = d.get("filename")
            if name not in seen_streams:
                seen_streams.append(name)
            index = min(seen_streams.index(name), expected_streams - 1)
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            done = d.get("downloaded_bytes") or 0
            part = (done / total) if total else 0
            overall = (index + min(part, 1)) / expected_streams * 100
            update_job(
                job_id,
                status="downloading",
                percent=round(overall, 1),
                speed=d.get("speed"),
                eta=d.get("eta"),
            )
        elif d.get("status") == "finished":
            update_job(job_id, status="processing")

    try:
        with yt_dlp.YoutubeDL(build_options(job_dir, media_format, quality, on_progress)) as ydl:
            ydl.extract_info(url, download=True)

        files = [p for p in job_dir.iterdir() if p.is_file() and p.suffix not in {".part", ".ytdl"}]
        if not files:
            raise RuntimeError("no output file")
        result = max(files, key=lambda p: p.stat().st_size)
        dest = DOWNLOAD_DIR / result.name
        n = 1
        while dest.exists():
            dest = DOWNLOAD_DIR / f"{result.stem} ({n}){result.suffix}"
            n += 1
        shutil.move(str(result), str(dest))
        shutil.rmtree(job_dir, ignore_errors=True)
        update_job(
            job_id,
            status="done",
            percent=100,
            filename=dest.name,
            size=dest.stat().st_size,
        )
    except Exception as exc:  # noqa: BLE001
        message = str(exc)
        if "Unsupported URL" in message:
            message = "This video source is not supported."
        elif "max-filesize" in message or "larger than" in message:
            message = "The file is larger than the configured size limit."
        else:
            message = "Download failed. The source may block downloads or the selected quality may be unavailable."
        update_job(job_id, status="error", error=message)
        shutil.rmtree(job_dir, ignore_errors=True)


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "app.html")


@app.post("/api/quit")
def quit_app():
    """Stops the helper (used by the Quit button when there is no app window)."""
    threading.Timer(0.3, lambda: os._exit(0)).start()
    return jsonify({"ok": True})


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "service": "UltraVideoDownloader API", "folder": str(DOWNLOAD_DIR)})


@app.post("/api/open-folder")
def open_folder():
    """Opens the downloads folder in the OS file manager (local use)."""
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(DOWNLOAD_DIR))  # noqa: S606
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(DOWNLOAD_DIR)])
        else:
            subprocess.Popen(["xdg-open", str(DOWNLOAD_DIR)])
    except Exception:  # noqa: BLE001
        return jsonify({"error": "Could not open the folder."}), 500
    return jsonify({"ok": True})


@app.post("/api/jobs")
def create_job():
    payload = request.get_json(silent=True) or {}
    url = (payload.get("url") or "").strip()
    media_format = payload.get("format", "mp4")
    quality = str(payload.get("quality", "best"))

    if not validate_url(url):
        return jsonify({"error": "Enter a valid public video URL."}), 400
    if media_format not in {"mp4", "mp3"}:
        return jsonify({"error": "Format must be mp4 or mp3."}), 400
    if quality not in QUALITIES:
        return jsonify({"error": "Unsupported quality."}), 400

    job_id = uuid.uuid4().hex[:12]
    with JOBS_LOCK:
        JOBS[job_id] = {
            "id": job_id,
            "status": "queued",
            "percent": 0,
            "speed": None,
            "eta": None,
            "filename": None,
            "size": None,
            "error": None,
            "created": time.time(),
        }
    threading.Thread(
        target=run_job, args=(job_id, url, media_format, quality), daemon=True
    ).start()
    return jsonify({"id": job_id}), 202


@app.get("/api/jobs/<job_id>")
def job_status(job_id):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if not job:
            return jsonify({"error": "Job not found."}), 404
        return jsonify(job)


@app.get("/api/jobs/<job_id>/file")
def job_file(job_id):
    with JOBS_LOCK:
        job = dict(JOBS.get(job_id) or {})
    if job.get("status") != "done":
        return jsonify({"error": "File is not ready."}), 409
    path = DOWNLOAD_DIR / job["filename"]
    if not path.is_file():
        return jsonify({"error": "File no longer exists."}), 410
    return send_file(
        path,
        as_attachment=True,
        download_name=re.sub(r"[^\w. -]", "_", path.name)[:180],
        conditional=True,  # supports resume / range requests for big files
    )


def port_in_use(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def open_window(url):
    """Shows the app in its own window (Windows). Returns False if that is not possible."""
    if not (FROZEN and sys.platform.startswith("win")):
        return False
    try:
        import webview  # pywebview, uses the Edge WebView2 runtime built into Windows

        webview.create_window("UltraVideoDownloader", url, width=1000, height=820, min_size=(420, 600))
        webview.start()  # blocks until the window is closed
        return True
    except Exception:  # noqa: BLE001
        return False


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    host = os.environ.get("UVD_HOST", "127.0.0.1")
    url = f"http://127.0.0.1:{port}"
    auto_open = os.environ.get("UVD_OPEN_BROWSER", "1" if FROZEN else "0") == "1"

    if port_in_use(host, port):
        # The app is already running: just show it again.
        if auto_open:
            webbrowser.open(url)
        sys.exit(0)

    print(f"UltraVideoDownloader running on {url}")
    print(f"Files are saved in: {DOWNLOAD_DIR}")

    if not auto_open:
        app.run(host=host, port=port, threaded=True)
    else:
        threading.Thread(
            target=lambda: app.run(host=host, port=port, threaded=True), daemon=True
        ).start()
        time.sleep(1.0)
        if open_window(url):
            sys.exit(0)  # window closed -> quit
        # No window available (macOS/Linux, or WebView2 missing): use the default browser.
        webbrowser.open(url)
        while True:  # keep serving until the Quit button / Ctrl+C
            time.sleep(3600)
