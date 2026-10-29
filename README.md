# UltraVideoDownloader

Download videos in HD / 4K with **no size or length limit**. The app runs on your own device, with your own internet connection.

- **Website** (`index.html`): a landing page hosted on Cloudflare, with download buttons.
- **Windows app**: opens in its own window (no console, no Python, no setup).
- **macOS / Linux**: the same app, opens in your browser at `http://127.0.0.1:10000`.
- **Android**: use a free open-source app such as [YTDLnis](https://github.com/deniscerri/ytdlnis) or [Seal](https://github.com/JunkFood02/Seal).

Use only for videos you own or have permission to download. Source-site terms still apply.

## For users

Go to the **Releases** page, download the zip for your system, unzip it and open `UltraVideoDownloader`.
Files are saved in `Downloads/UltraVideoDownloader`. On Windows, if SmartScreen warns, choose *More info → Run anyway* (the app is not code-signed).

## For the owner

- `index.html` is the public landing page (deployed by Cloudflare on every push). Its download buttons use `releases/latest/download/UltraVideoDownloader-<windows|macos|linux>.zip`.
- `app.html` is the downloader UI. It is bundled inside the app and served by it, so the page and the API are on the same origin.
- `backend/app.py` is the local Flask + yt-dlp server. Downloads run as background jobs with live progress.
- On Windows the app uses [pywebview](https://pywebview.flowrl.com/) (Edge WebView2, built into Windows 10/11). If a window cannot be opened it falls back to the default browser.

### Publish a new version

GitHub → **Actions → Build apps → Run workflow**, enter a tag such as `v1.1.0`. Windows, macOS and Linux apps are built and attached to the release.

### Run from source

```
pip install -r backend/requirements.txt
python backend/app.py        # then open http://127.0.0.1:10000
```

Needs ffmpeg on PATH, or the bundled one from `imageio-ffmpeg` is used.

Environment variables: `PORT`, `UVD_DOWNLOAD_DIR`, `UVD_MAX_FILESIZE_MB` (0 = unlimited), `UVD_ALLOWED_ORIGINS`.
