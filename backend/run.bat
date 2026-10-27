@echo off
REM Starts UltraVideoDownloader locally. Requires Python 3 and ffmpeg.
cd /d "%~dp0"
if not exist .venv python -m venv .venv
call .venv\Scripts\activate
pip install -q -r requirements.txt
pip install -q -U yt-dlp
python app.py
