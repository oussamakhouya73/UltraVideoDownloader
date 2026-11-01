"""UltraVideoDownloader: local app (Flask + yt-dlp).

Features: choose the save folder, pause / resume (also after the internet drops or the app is
closed), automatic best-quality detection, live progress, update check, anonymous statistics.

Environment variables (mostly for testing):
  PORT                 port to listen on (default 10000)
  UVD_HOST             host to bind (default 127.0.0.1, local only)
  UVD_DATA_DIR         where settings.json / jobs.json live
  UVD_DOWNLOAD_DIR     default save folder
  UVD_ALLOWED_ORIGINS  extra origins allowed to call this local API (normally none)
"""
import atexit
import hashlib
import json
import logging
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
import uuid
import webbrowser
from pathlib import Path
from urllib.parse import urlparse

import yt_dlp
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

import uvd_config as cfg
from uvd_version import VERSION

# A windowed Windows app has no console: stdout/stderr are None and printing would crash.
for _stream in ("stdout", "stderr"):
    if getattr(sys, _stream) is None:
        setattr(sys, _stream, open(os.devnull, "w"))

IS_WIN = sys.platform.startswith("win")
IS_MAC = sys.platform == "darwin"
FROZEN = getattr(sys, "frozen", False)  # True inside the packaged app
NO_WINDOW = 0x08000000 if IS_WIN else 0  # CREATE_NO_WINDOW

FRONTEND_DIR = Path(sys._MEIPASS) if FROZEN else Path(__file__).resolve().parent.parent
STARTED = time.time()
MAX_JOBS = 60


# ----------------------------------------------------------------------------- storage
def data_dir():
    if os.environ.get("UVD_DATA_DIR"):
        p = Path(os.environ["UVD_DATA_DIR"])
    elif IS_WIN:
        p = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming") / "UltraVideoDownloader"
    elif IS_MAC:
        p = Path.home() / "Library" / "Application Support" / "UltraVideoDownloader"
    else:
        p = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "UltraVideoDownloader"
    p.mkdir(parents=True, exist_ok=True)
    return p


DATA_DIR = data_dir()
SETTINGS_FILE = DATA_DIR / "settings.json"
JOBS_FILE = DATA_DIR / "jobs.json"
DEFAULT_DOWNLOADS = Path(os.environ.get("UVD_DOWNLOAD_DIR") or Path.home() / "Downloads" / "UltraVideoDownloader")

LANGS = {"en", "ar", "fr", "es"}
THEMES = {"system", "light", "dark"}
SETTINGS_LOCK = threading.Lock()
SETTINGS = {
    "download_dir": str(DEFAULT_DOWNLOADS),
    "language": None,
    "theme": "system",
    "stats": True,
    "install_id": None,
}


def write_json(path, obj):
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, path)


def read_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return default


def load_settings():
    saved = read_json(SETTINGS_FILE, {})
    with SETTINGS_LOCK:
        for k in SETTINGS:
            if k in saved:
                SETTINGS[k] = saved[k]
        if not SETTINGS["install_id"]:
            SETTINGS["install_id"] = str(uuid.uuid4())
        write_json(SETTINGS_FILE, SETTINGS)


def writable_dir(path_str):
    """Returns a Path if the folder exists (or can be created) and we can write in it."""
    try:
        p = Path(path_str).expanduser()
        if not p.is_absolute():
            return None
        p.mkdir(parents=True, exist_ok=True)
        probe = p / f".uvd-write-test-{uuid.uuid4().hex[:6]}"
        probe.write_text("x")
        probe.unlink()
        return p
    except Exception:  # noqa: BLE001
        return None


# ----------------------------------------------------------------------------- statistics (PostHog)
def uuid7():
    ts = int(time.time() * 1000)
    r = int.from_bytes(os.urandom(10), "big")
    value = (ts << 80) | (0x7 << 76) | (((r >> 68) & 0xFFF) << 64) | (0b10 << 62) | (r & ((1 << 62) - 1))
    return str(uuid.UUID(int=value))


SESSION_ID = uuid7()


def _post_event(payload):
    try:
        req = urllib.request.Request(
            cfg.POSTHOG_HOST.rstrip("/") + "/capture/",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "User-Agent": "UltraVideoDownloader/" + VERSION},
        )
        urllib.request.urlopen(req, timeout=4).read()
    except Exception:  # noqa: BLE001
        pass


def stats_event(event, props=None, wait=False):
    """Anonymous usage statistics. Never sends links, titles or file names."""
    if not cfg.POSTHOG_KEY or not SETTINGS.get("stats") or not SETTINGS.get("install_id"):
        return
    base = {
        "$lib": "uvd-app",
        "$session_id": SESSION_ID,
        "app_version": VERSION,
        "os": platform.system(),
        "app_language": SETTINGS.get("language") or "auto",
    }
    payload = {
        "api_key": cfg.POSTHOG_KEY,
        "event": event,
        "distinct_id": SETTINGS["install_id"],
        "properties": {**base, **(props or {}), "$set": {"app_version": VERSION, "os": platform.system()}},
    }
    t = threading.Thread(target=_post_event, args=(payload,), daemon=True)
    t.start()
    if wait:
        t.join(3)


# ----------------------------------------------------------------------------- app + security
app = Flask(__name__)
if not os.environ.get("UVD_DEBUG"):
    logging.getLogger("werkzeug").setLevel(logging.WARNING)

# Only this app itself may call the local API. The public website must NOT be allowed here:
# ads run on that origin, and ad code is third party.
LOCAL_ORIGIN_RE = r"http://(localhost|127\.0\.0\.1)(:\d+)?"
EXTRA_ORIGINS = [o.strip() for o in os.environ.get("UVD_ALLOWED_ORIGINS", "").split(",") if o.strip()]
ALLOWED_ORIGINS = EXTRA_ORIGINS


def origin_allowed(origin):
    return bool(re.fullmatch(LOCAL_ORIGIN_RE, origin)) or origin in ALLOWED_ORIGINS


CSP = (
    "default-src 'self'; script-src 'self' 'unsafe-inline'; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; "
    f"img-src 'self' data: https:; connect-src 'self'; frame-src {cfg.SITE_URL}; "
    "object-src 'none'; base-uri 'none'; form-action 'self'"
)


@app.after_request
def security_headers(resp):
    resp.headers["Content-Security-Policy"] = CSP
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Cache-Control"] = "no-store"
    return resp


CORS(app, resources={r"/api/*": {"origins": [LOCAL_ORIGIN_RE] + ALLOWED_ORIGINS}})


@app.before_request
def check_origin():
    if not request.path.startswith("/api/"):
        return None
    origin = request.headers.get("Origin")
    if origin and not origin_allowed(origin):
        return jsonify({"error": "forbidden"}), 403
    if request.headers.get("Sec-Fetch-Site") in ("cross-site", "same-site"):
        return jsonify({"error": "forbidden"}), 403
    return None


def validate_url(value):
    if not isinstance(value, str) or len(value) > 2048:
        return False
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.hostname)


# ----------------------------------------------------------------------------- helpers
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


def is_online():
    flag = os.environ.get("UVD_OFFLINE_FLAG")  # test hook: the file's existence means "offline"
    if flag:
        return not Path(flag).exists()
    for host, port in (("1.1.1.1", 443), ("8.8.8.8", 53), ("www.google.com", 443)):
        try:
            socket.create_connection((host, port), timeout=3).close()
            return True
        except OSError:
            continue
    return False


NETWORK_HINTS = (
    "timed out", "timeout", "connection", "network", "name resolution", "getaddrinfo", "unreachable",
    "incompleteread", "remote end closed", "reset by peer", "ssl", "temporary failure", "http error 5",
    "http error 429", "bad gateway", "unable to download", "failed to resolve", "eof occurred",
    "read error", "broken pipe", "content too short", "retrying",
)


def classify(exc):
    """Turns a yt-dlp error into a short code the interface can translate."""
    msg = str(exc).lower()
    if "unsupported url" in msg:
        return "unsupported"
    if "private video" in msg or "members-only" in msg or "members only" in msg:
        return "private"
    if "confirm you" in msg and "bot" in msg:
        return "blocked"
    if "sign in" in msg or "login required" in msg:
        return "private"
    if "live event" in msg or "is live" in msg or "live stream" in msg:
        return "live"
    if "video unavailable" in msg or "has been removed" in msg or "not available" in msg or "does not exist" in msg:
        return "unavailable"
    if "ffmpeg" in msg or "ffprobe" in msg:
        return "ffmpeg"
    if "no space left" in msg or "disk full" in msg:
        return "disk"
    if any(h in msg for h in NETWORK_HINTS) or not is_online():
        return "network"
    return "failed"


def build_format(media_format, quality):
    if media_format == "mp3":
        return "bestaudio/best"
    if quality == "best":
        return "bv*+ba/b"
    h = int(quality)
    return f"bv*[height<={h}]+ba/b[height<={h}]/b"


def _fsize(f, duration):
    s = f.get("filesize") or f.get("filesize_approx")
    if s:
        return int(s)
    tbr = f.get("tbr")
    if tbr and duration:
        return int(tbr * 1000 / 8 * duration)
    return None


def compute_qualities(info):
    """The qualities this video really has, best first, with a size estimate."""
    duration = info.get("duration")
    fmts = info.get("formats") or []
    video = [f for f in fmts if f.get("vcodec") not in (None, "none") and f.get("height")]
    audio = [f for f in fmts if f.get("vcodec") in (None, "none") and f.get("acodec") not in (None, "none")]
    best_audio = max(audio, key=lambda f: (f.get("abr") or f.get("tbr") or 0), default=None)
    audio_size = _fsize(best_audio, duration) if best_audio else None
    by_height = {}
    for f in video:
        by_height.setdefault(f["height"], []).append(f)
    out = []
    for h in sorted(by_height, reverse=True):
        best = max(by_height[h], key=lambda f: (f.get("tbr") or 0))
        size = _fsize(best, duration)
        if size is not None and best.get("acodec") in (None, "none") and audio_size:
            size += audio_size
        out.append({"height": h, "res": min(h, best.get("width") or h), "size": size})
    return out


# ----------------------------------------------------------------------------- jobs
ACTIVE = {"queued", "downloading", "processing", "waiting"}
JOBS = {}
CTL = {}
JOBS_LOCK = threading.RLock()
SLOTS = threading.Semaphore(2)  # at most 2 downloads at the same time


class Stop(Exception):
    """Raised inside the progress hook to pause or cancel a download."""


def save_jobs():
    with JOBS_LOCK:
        items = sorted(JOBS.values(), key=lambda j: j["created"], reverse=True)[:MAX_JOBS]
        try:
            write_json(JOBS_FILE, items)
        except Exception:  # noqa: BLE001
            pass


def update_job(job_id, persist=False, **fields):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if job:
            job.update(fields)
            job["updated"] = time.time()
    if persist:
        save_jobs()


def tmp_dir_for(job):
    return Path(job["dir"]) / f".uvd-{job['id']}"


def unique_path(folder, name):
    dest = folder / name
    n = 1
    while dest.exists():
        dest = folder / f"{Path(name).stem} ({n}){Path(name).suffix}"
        n += 1
    return dest


def build_options(job, tmp, ctl, hook):
    media_format = job["format"]
    opts = {
        "format": build_format(media_format, job["quality"]),
        "outtmpl": str(tmp / "%(title).120B-%(id)s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "windowsfilenames": True,
        "socket_timeout": 30,
        "retries": 5,
        "fragment_retries": 5,
        "extractor_retries": 3,
        "continuedl": True,
        "concurrent_fragment_downloads": 4,
        "progress_hooks": [hook],
        "merge_output_format": "mp4" if media_format == "mp4" else None,
        "postprocessors": (
            [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]
            if media_format == "mp3" else []
        ),
    }
    if media_format == "mp4":
        # Highest resolution first; among equals prefer H.264 + AAC (plays everywhere).
        opts["format_sort"] = ["res", "vcodec:h264", "acodec:aac"]
    ffmpeg = find_ffmpeg()
    if ffmpeg:
        opts["ffmpeg_location"] = ffmpeg
    return opts


def run_ytdlp(job, tmp, ctl):
    """One download attempt. Partial files stay in `tmp`, so the next attempt continues from there."""
    job_id = job["id"]
    finished_streams = [0]

    def hook(d):
        if ctl["pause"] or ctl["cancel"]:
            raise Stop()
        info = d.get("info_dict") or {}
        if d.get("status") == "downloading":
            expected = len(info.get("requested_formats") or []) or (2 if job["format"] == "mp4" else 1)
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            part = min((d.get("downloaded_bytes") or 0) / total, 1) if total else 0
            percent = (min(finished_streams[0], expected - 1) + part) / expected * 100
            fields = {"status": "downloading", "percent": round(percent, 1),
                      "speed": d.get("speed"), "eta": d.get("eta")}
            if not job.get("title") and info.get("title"):
                fields["title"] = info["title"]
            if not job.get("thumbnail") and info.get("thumbnail"):
                fields["thumbnail"] = info["thumbnail"]
            update_job(job_id, **fields)
        elif d.get("status") == "finished":
            finished_streams[0] += 1
            update_job(job_id, status="processing", speed=None, eta=None)

    with yt_dlp.YoutubeDL(build_options(job, tmp, ctl, hook)) as ydl:
        info = ydl.extract_info(job["url"], download=True)
    update_job(job_id, site=info.get("extractor_key") or job.get("site"))
    path = None
    for rd in info.get("requested_downloads") or []:
        if rd.get("filepath") and Path(rd["filepath"]).is_file():
            path = Path(rd["filepath"])
    if path is None:
        files = [p for p in tmp.iterdir() if p.is_file() and p.suffix not in {".part", ".ytdl", ".temp"}]
        if not files:
            raise RuntimeError("no output file")
        path = max(files, key=lambda p: p.stat().st_size)
    return path


def run_job(job_id):
    with JOBS_LOCK:
        job = JOBS[job_id]
    ctl = CTL[job_id]
    tmp = tmp_dir_for(job)

    def stopped():
        if ctl["cancel"]:
            shutil.rmtree(tmp, ignore_errors=True)
            with JOBS_LOCK:
                JOBS.pop(job_id, None)
            save_jobs()
            return True
        if ctl["pause"]:
            update_job(job_id, persist=True, status="paused", speed=None, eta=None)
            return True
        return False

    # wait for a free slot (max 2 at once)
    update_job(job_id, status="queued", speed=None, eta=None)
    while not SLOTS.acquire(timeout=0.5):
        if stopped():
            return
    started = time.time()
    try:
        failures = 0
        last_percent = -1
        while True:
            if stopped():
                return
            try:
                tmp.mkdir(parents=True, exist_ok=True)
                update_job(job_id, status="downloading", error=None)
                path = run_ytdlp(job, tmp, ctl)
                dest = unique_path(Path(job["dir"]), path.name)
                shutil.move(str(path), str(dest))
                shutil.rmtree(tmp, ignore_errors=True)
                update_job(job_id, persist=True, status="done", percent=100, speed=None, eta=None,
                           filename=dest.name, path=str(dest), size=dest.stat().st_size, error=None)
                stats_event("download_completed", {
                    "site": job.get("site"), "format": job["format"], "quality": job["quality"],
                    "seconds": int(time.time() - started), "size_mb": round(dest.stat().st_size / 1048576),
                })
                return
            except Exception as exc:  # noqa: BLE001
                if ctl["pause"] or ctl["cancel"] or isinstance(exc, Stop):
                    stopped()
                    return
                code = classify(exc)
                with JOBS_LOCK:
                    percent = JOBS.get(job_id, {}).get("percent", 0)
                if percent > last_percent:  # we made progress since the last failure: start counting again
                    failures = 0
                    last_percent = percent
                if code == "network":
                    failures += 1
                    if is_online() and failures > 8:
                        code = "failed"
                    else:
                        # No internet (or a hiccup): wait, then continue from the partial file.
                        update_job(job_id, status="waiting", speed=None, eta=None)
                        delay = 4 if not is_online() else min(30, 3 * 2 ** min(failures, 3))
                        for _ in range(int(delay * 2)):
                            if ctl["pause"] or ctl["cancel"]:
                                break
                            time.sleep(0.5)
                        continue
                update_job(job_id, persist=True, status="error", error=code, speed=None, eta=None)
                stats_event("download_failed", {"code": code, "site": job.get("site"), "format": job["format"]})
                return
    finally:
        SLOTS.release()


def start_thread(job_id):
    ctl = {"pause": False, "cancel": False}
    t = threading.Thread(target=run_job, args=(job_id,), daemon=True)
    ctl["thread"] = t
    CTL[job_id] = ctl
    t.start()


def public_job(j):
    keep = ("id", "url", "format", "quality", "dir", "title", "thumbnail", "duration", "site", "status",
            "percent", "speed", "eta", "filename", "size", "error", "created", "size_estimate")
    return {k: j.get(k) for k in keep}


def load_jobs():
    for j in read_json(JOBS_FILE, []):
        if not isinstance(j, dict) or "id" not in j:
            continue
        if j.get("status") in ACTIVE:
            j["status"] = "paused"  # the app was closed: let the user continue when ready
        JOBS[j["id"]] = j


def shutdown_state(send_event=True):
    if getattr(shutdown_state, "done", False):
        return
    shutdown_state.done = True
    with JOBS_LOCK:
        for j in JOBS.values():
            if j.get("status") in ACTIVE:
                j["status"] = "paused"
    save_jobs()
    if send_event:
        stats_event("app_closed", {"session_seconds": int(time.time() - STARTED)}, wait=True)


# ----------------------------------------------------------------------------- native helpers
def choose_folder(initial):
    """Opens the system 'choose folder' dialog. Returns (path, error_code)."""
    try:
        if IS_WIN:
            script = (
                "[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding $false;"
                "Add-Type -AssemblyName System.Windows.Forms;"
                "[System.Windows.Forms.Application]::EnableVisualStyles();"
                "$o = New-Object System.Windows.Forms.Form; $o.TopMost = $true; $o.ShowInTaskbar = $false;"
                "$o.StartPosition = 'CenterScreen'; $o.Opacity = 0; $o.Show();"
                "$f = New-Object System.Windows.Forms.FolderBrowserDialog;"
                "$f.SelectedPath = $env:UVD_INITIAL; $f.ShowNewFolderButton = $true;"
                "if ($f.ShowDialog($o) -eq 'OK') { Write-Output $f.SelectedPath }; $o.Close()"
            )
            r = subprocess.run(
                ["powershell", "-NoProfile", "-STA", "-WindowStyle", "Hidden", "-Command", script],
                capture_output=True, text=True, encoding="utf-8", timeout=900, creationflags=NO_WINDOW,
                env={**os.environ, "UVD_INITIAL": initial},
            )
        elif IS_MAC:
            r = subprocess.run(["osascript", "-e", "POSIX path of (choose folder)"],
                               capture_output=True, text=True, timeout=900)
        else:
            tool = shutil.which("zenity") or shutil.which("kdialog")
            if not tool:
                return None, "no_dialog"
            cmd = [tool, "--file-selection", "--directory"] if tool.endswith("zenity") else [tool, "--getexistingdirectory", initial]
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        path = (r.stdout or "").strip()
        return (path or None), None
    except Exception:  # noqa: BLE001
        return None, "no_dialog"


def reveal(path):
    path = Path(path)
    try:
        if IS_WIN:
            if path.is_file():
                subprocess.Popen(["explorer", "/select,", str(path)])
            else:
                os.startfile(str(path))  # noqa: S606
        elif IS_MAC:
            subprocess.Popen(["open", "-R", str(path)] if path.is_file() else ["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path.parent if path.is_file() else path)])
        return True
    except Exception:  # noqa: BLE001
        return False


# ----------------------------------------------------------------------------- updates
UA = {"User-Agent": "UltraVideoDownloader/" + VERSION, "Accept": "application/vnd.github+json"}
_LATEST = {"t": 0, "data": None}
UPDATE = {"state": "idle", "percent": 0, "error": None}


def parse_ver(s):
    nums = [int(x) for x in re.findall(r"\d+", s or "")][:3]
    return tuple(nums + [0] * (3 - len(nums)))


def latest_release():
    if _LATEST["data"] and time.time() - _LATEST["t"] < 3600:
        return _LATEST["data"]
    try:
        req = urllib.request.Request(f"https://api.github.com/repos/{cfg.GITHUB_REPO}/releases/latest", headers=UA)
        with urllib.request.urlopen(req, timeout=8) as r:
            j = json.load(r)
        data = {
            "tag": j.get("tag_name", ""),
            "url": j.get("html_url"),
            "assets": {a["name"]: {"url": a["browser_download_url"], "size": a.get("size"), "digest": a.get("digest")}
                       for a in j.get("assets", [])},
        }
        _LATEST.update(t=time.time(), data=data)
        return data
    except Exception:  # noqa: BLE001
        return _LATEST["data"]


def do_update():
    try:
        rel = latest_release()
        asset = (rel or {}).get("assets", {}).get("UltraVideoDownloader-Setup.exe")
        if not asset or not asset["url"].startswith(f"https://github.com/{cfg.GITHUB_REPO}/releases/download/"):
            raise RuntimeError("no installer")
        dest = Path(tempfile.gettempdir()) / "UltraVideoDownloader-Setup.exe"
        UPDATE.update(state="downloading", percent=0, error=None)
        sha, done, total = hashlib.sha256(), 0, asset.get("size") or 0
        with urllib.request.urlopen(urllib.request.Request(asset["url"], headers=UA), timeout=30) as r, open(dest, "wb") as f:
            while True:
                chunk = r.read(262144)
                if not chunk:
                    break
                f.write(chunk)
                sha.update(chunk)
                done += len(chunk)
                if total:
                    UPDATE["percent"] = round(done / total * 100)
        if total and done != total:
            raise RuntimeError("incomplete")
        digest = asset.get("digest") or ""
        if digest.startswith("sha256:") and digest[7:] != sha.hexdigest():
            raise RuntimeError("checksum mismatch")
        UPDATE.update(state="installing", percent=100)
        subprocess.Popen([str(dest), "/SILENT", "/CLOSEAPPLICATIONS", "/NORESTART"],
                         close_fds=True, creationflags=0x00000008 | 0x00000200)
        time.sleep(1.5)
        shutdown_state()
        os._exit(0)
    except Exception:  # noqa: BLE001
        UPDATE.update(state="error", error="update_failed")


# ----------------------------------------------------------------------------- routes
@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "app.html")


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "service": "UltraVideoDownloader", "version": VERSION})


@app.get("/api/settings")
def get_settings():
    with SETTINGS_LOCK:
        return jsonify({k: SETTINGS[k] for k in ("download_dir", "language", "theme", "stats")} | {"version": VERSION})


@app.post("/api/settings")
def set_settings():
    p = request.get_json(silent=True) or {}
    with SETTINGS_LOCK:
        if "download_dir" in p:
            folder = writable_dir(str(p["download_dir"]))
            if not folder:
                return jsonify({"error": "folder"}), 400
            SETTINGS["download_dir"] = str(folder)
        if "language" in p:
            if p["language"] not in LANGS | {None}:
                return jsonify({"error": "invalid"}), 400
            SETTINGS["language"] = p["language"]
        if "theme" in p:
            if p["theme"] not in THEMES:
                return jsonify({"error": "invalid"}), 400
            SETTINGS["theme"] = p["theme"]
        if "stats" in p:
            SETTINGS["stats"] = bool(p["stats"])
        write_json(SETTINGS_FILE, SETTINGS)
    return get_settings()


@app.post("/api/choose-folder")
def api_choose_folder():
    with SETTINGS_LOCK:
        initial = SETTINGS["download_dir"]
    path, err = choose_folder(initial)
    if err:
        return jsonify({"error": err}), 501
    if not path:
        return jsonify({"cancelled": True})
    folder = writable_dir(path)
    if not folder:
        return jsonify({"error": "folder"}), 400
    with SETTINGS_LOCK:
        SETTINGS["download_dir"] = str(folder)
        write_json(SETTINGS_FILE, SETTINGS)
    return jsonify({"path": str(folder)})


@app.post("/api/info")
def api_info():
    url = ((request.get_json(silent=True) or {}).get("url") or "").strip()
    if not validate_url(url):
        return jsonify({"error": "invalid_url"}), 400
    opts = {"quiet": True, "no_warnings": True, "noplaylist": True, "skip_download": True,
            "socket_timeout": 20, "extractor_retries": 2}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": classify(exc)}), 502
    if not info:
        return jsonify({"error": "failed"}), 502
    if info.get("_type") == "playlist":
        return jsonify({"error": "playlist"}), 422
    if info.get("is_live"):
        return jsonify({"error": "live"}), 422
    qualities = compute_qualities(info)
    return jsonify({
        "title": info.get("title") or "",
        "thumbnail": info.get("thumbnail") or "",
        "duration": info.get("duration"),
        "uploader": info.get("uploader") or info.get("channel") or "",
        "site": info.get("extractor_key") or "",
        "qualities": qualities,
        "best": qualities[0]["height"] if qualities else None,
    })


def clip(value, n):
    return value[:n] if isinstance(value, str) else ""


@app.post("/api/jobs")
def create_job():
    p = request.get_json(silent=True) or {}
    url = (p.get("url") or "").strip()
    media_format = p.get("format", "mp4")
    quality = str(p.get("quality", "best"))
    if not validate_url(url):
        return jsonify({"error": "invalid_url"}), 400
    if media_format not in {"mp4", "mp3"}:
        return jsonify({"error": "invalid"}), 400
    if not (quality == "best" or (quality.isdigit() and 100 <= int(quality) <= 8640)):
        return jsonify({"error": "invalid"}), 400
    with SETTINGS_LOCK:
        folder = writable_dir(SETTINGS["download_dir"])
    if not folder:
        return jsonify({"error": "folder"}), 400
    job_id = uuid.uuid4().hex[:12]
    size_estimate = p.get("size_estimate")
    job = {
        "id": job_id, "url": url, "format": media_format, "quality": quality, "dir": str(folder),
        "title": clip(p.get("title"), 300), "thumbnail": clip(p.get("thumbnail"), 1000),
        "duration": p.get("duration") if isinstance(p.get("duration"), (int, float)) else None,
        "site": clip(p.get("site"), 60),
        "size_estimate": size_estimate if isinstance(size_estimate, int) else None,
        "status": "queued", "percent": 0, "speed": None, "eta": None, "filename": None, "size": None,
        "error": None, "created": time.time(), "updated": time.time(),
    }
    with JOBS_LOCK:
        JOBS[job_id] = job
    save_jobs()
    stats_event("download_started", {"site": job["site"], "format": media_format, "quality": quality})
    start_thread(job_id)
    return jsonify({"id": job_id}), 202


@app.get("/api/jobs")
def list_jobs():
    with JOBS_LOCK:
        items = sorted(JOBS.values(), key=lambda j: j["created"], reverse=True)
        return jsonify([public_job(j) for j in items])


def _get_job(job_id):
    with JOBS_LOCK:
        return JOBS.get(job_id)


@app.post("/api/jobs/<job_id>/pause")
def job_pause(job_id):
    job, ctl = _get_job(job_id), CTL.get(job_id)
    if not job:
        return jsonify({"error": "not_found"}), 404
    if job["status"] in ACTIVE and ctl and ctl["thread"].is_alive():
        ctl["pause"] = True
        ctl["thread"].join(5)
    return jsonify(public_job(job))


@app.post("/api/jobs/<job_id>/resume")
def job_resume(job_id):
    job, ctl = _get_job(job_id), CTL.get(job_id)
    if not job:
        return jsonify({"error": "not_found"}), 404
    if ctl and ctl["thread"].is_alive():
        return jsonify(public_job(job))
    if job["status"] in {"paused", "error"}:
        update_job(job_id, persist=True, status="queued", error=None)
        start_thread(job_id)
    return jsonify(public_job(job))


@app.post("/api/jobs/<job_id>/cancel")
def job_cancel(job_id):
    """Stops the download, deletes the partial files and removes it from the list."""
    job, ctl = _get_job(job_id), CTL.get(job_id)
    if not job:
        return jsonify({"ok": True})
    if ctl and ctl["thread"].is_alive():
        ctl["cancel"] = True
        ctl["thread"].join(5)
    shutil.rmtree(tmp_dir_for(job), ignore_errors=True)
    with JOBS_LOCK:
        JOBS.pop(job_id, None)
    save_jobs()
    return jsonify({"ok": True})


@app.post("/api/jobs/<job_id>/remove")
def job_remove(job_id):
    """Removes a finished download from the list (the file stays on disk)."""
    job = _get_job(job_id)
    if job and job["status"] == "done":
        with JOBS_LOCK:
            JOBS.pop(job_id, None)
        save_jobs()
    return jsonify({"ok": True})


@app.post("/api/jobs/<job_id>/reveal")
def job_reveal(job_id):
    job = _get_job(job_id)
    if not job:
        return jsonify({"error": "not_found"}), 404
    target = job.get("path") if job["status"] == "done" and job.get("path") else job["dir"]
    return jsonify({"ok": reveal(target)})


@app.post("/api/open-folder")
def open_folder():
    with SETTINGS_LOCK:
        target = SETTINGS["download_dir"]
    return jsonify({"ok": reveal(target)})


@app.post("/api/open-url")
def open_url():
    url = (request.get_json(silent=True) or {}).get("url") or ""
    allowed = (cfg.SITE_URL + "/", f"https://github.com/{cfg.GITHUB_REPO}/")
    if not url.startswith(allowed):
        return jsonify({"error": "forbidden"}), 403
    webbrowser.open(url)
    return jsonify({"ok": True})


@app.get("/api/version")
def api_version():
    rel = latest_release()
    available = bool(rel) and VERSION != "dev" and parse_ver(rel["tag"]) > parse_ver(VERSION)
    return jsonify({
        "current": VERSION, "latest": (rel or {}).get("tag", "").lstrip("v"), "update_available": available,
        "can_auto_update": bool(IS_WIN and FROZEN), "update": dict(UPDATE),
    })


@app.post("/api/update")
def api_update():
    rel = latest_release()
    if not rel:
        return jsonify({"error": "update_failed"}), 502
    if not (IS_WIN and FROZEN):
        webbrowser.open(rel["url"])
        return jsonify({"opened": True})
    if UPDATE["state"] not in {"downloading", "installing"}:
        threading.Thread(target=do_update, daemon=True).start()
    return jsonify({"started": True})


@app.post("/api/quit")
def quit_app():
    """Stops the app (used by the Quit button when there is no app window)."""
    def bye():
        shutdown_state()
        os._exit(0)

    threading.Timer(0.3, bye).start()
    return jsonify({"ok": True})


# ----------------------------------------------------------------------------- startup
def port_in_use(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def open_window(url):
    """Shows the app in its own window (Windows). Returns False if that is not possible."""
    if not (FROZEN and IS_WIN):
        return False
    try:
        import webview  # pywebview, uses the Edge WebView2 runtime built into Windows

        webview.create_window("UltraVideoDownloader", url, width=1040, height=860, min_size=(420, 600))
        webview.start()  # blocks until the window is closed
        return True
    except Exception:  # noqa: BLE001
        return False


def heartbeat():
    while True:
        time.sleep(300)
        with JOBS_LOCK:
            active = sum(1 for j in JOBS.values() if j.get("status") in ACTIVE)
        stats_event("app_heartbeat", {"active_downloads": active, "session_seconds": int(time.time() - STARTED)})


def main():
    port = int(os.environ.get("PORT", "10000"))
    host = os.environ.get("UVD_HOST", "127.0.0.1")
    url = f"http://127.0.0.1:{port}"
    auto_open = os.environ.get("UVD_OPEN_BROWSER", "1" if FROZEN else "0") == "1"

    if port_in_use(host, port):
        # The app is already running: just show it again.
        if auto_open:
            webbrowser.open(url)
        sys.exit(0)

    load_settings()
    load_jobs()
    atexit.register(shutdown_state)
    stats_event("app_started", {"first_run": not JOBS_FILE.exists()})
    threading.Thread(target=heartbeat, daemon=True).start()
    print(f"UltraVideoDownloader {VERSION} running on {url}")

    if not auto_open:
        app.run(host=host, port=port, threaded=True)
        return
    threading.Thread(target=lambda: app.run(host=host, port=port, threaded=True), daemon=True).start()
    time.sleep(1.0)
    if open_window(url):
        shutdown_state()
        sys.exit(0)  # window closed -> quit
    # No window available (macOS/Linux, or WebView2 missing): use the default browser.
    webbrowser.open(url)
    while True:  # keep serving until the Quit button / Ctrl+C
        time.sleep(3600)


if __name__ == "__main__":
    main()
