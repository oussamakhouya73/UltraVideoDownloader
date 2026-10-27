#!/usr/bin/env bash
# Starts UltraVideoDownloader locally. Requires Python 3 and ffmpeg.
set -e
cd "$(dirname "$0")"
[ -d .venv ] || python3 -m venv .venv
. .venv/bin/activate
pip install -q -r requirements.txt
pip install -q -U yt-dlp
python app.py
