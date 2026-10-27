"""Builds a single-file app with PyInstaller (run from the repo root or backend/)."""
import os
from pathlib import Path

import PyInstaller.__main__

root = Path(__file__).resolve().parent.parent
PyInstaller.__main__.run([
    str(root / "backend" / "app.py"),
    "--onefile",
    "--name", "UltraVideoDownloader",
    "--add-data", f"{root / 'index.html'}{os.pathsep}.",
    "--collect-all", "yt_dlp",
    "--collect-all", "imageio_ffmpeg",
    "--distpath", str(root / "dist"),
    "--workpath", str(root / "build"),
    "--specpath", str(root / "build"),
    "--noconfirm",
])
