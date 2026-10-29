"""Builds a single-file app with PyInstaller (run from the repo root or backend/)."""
import os
import sys
from pathlib import Path

import PyInstaller.__main__

root = Path(__file__).resolve().parent.parent

args = [
    str(root / "backend" / "app.py"),
    "--onefile",
    "--name", "UltraVideoDownloader",
    "--add-data", f"{root / 'app.html'}{os.pathsep}.",
    "--collect-all", "yt_dlp",
    "--collect-all", "imageio_ffmpeg",
    "--distpath", str(root / "dist"),
    "--workpath", str(root / "build"),
    "--specpath", str(root / "build"),
    "--noconfirm",
]

if sys.platform.startswith("win"):
    # Windows: no black console window; the app opens its own window (pywebview / WebView2).
    args += [
        "--noconsole",
        "--collect-all", "webview",
        "--collect-all", "pythonnet",
        "--collect-all", "clr_loader",
    ]

PyInstaller.__main__.run(args)
