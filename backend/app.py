"""UltraVideoDownloader API.

Designed for long and large videos: downloads run as background jobs
(no request timeout), with live progress, no file-size cap by default,
and files saved to a local folder.

Environment variables:
  PORT                  port to listen on (default 10000)
  UVD_HOST              host to bind (default 127.0.0.1, local only)
  UVD_DOWNLOAD_DIR      where files are saved (default ./downloads)
  UVD_MAX_FILESIZE_MB   0 = unlimited (default)
  UVD_CORS_ORIGINS      allowed origins (default: localhost only)
"""
import os
import re
import shutil
import threading
import time
import uuid
from pathlib import Path
from urllib.parse import urlparse

import yt_dlp
from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent
DOWNLOAD_DIR = Path(os.environ.get("UVD_DOWNLOAD_DIR", BASE_DIR / "downloads")).resolve()
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_FILESIZE_MB = int(os.environ.get("UVD_MAX_FILESIZE_MB", "0"))

app = Flask(__name__)
CORS(
    app,
    resources={r"/api/*": {"origins": os.environ.get(
        "UVD_CORS_ORIGINS", r"http://(localhost|127\.0\.0\.1)(:\d+)?")}},
)
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
        update_job(
            job_id,
            status="done",
            percent=100,
            filename=result.name,
            size=result.stat().st_size,
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
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "service": "UltraVideoDownloader API"})


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
    path = DOWNLOAD_DIR / job_id / job["filename"]
    if not path.is_file():
        return jsonify({"error": "File no longer exists."}), 410
    return send_file(
        path,
        as_attachment=True,
        download_name=re.sub(r"[^\w. -]", "_", path.name)[:180],
        conditional=True,  # supports resume / range requests for big files
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    host = os.environ.get("UVD_HOST", "127.0.0.1")
    print(f"UltraVideoDownloader running on http://{host}:{port}")
    print(f"Files are saved in: {DOWNLOAD_DIR}")
    app.run(host=host, port=port, threaded=True)
