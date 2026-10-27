# UltraVideoDownloader

A responsive dark-mode frontend prototype for a video downloader, intended for deployment on Cloudflare Pages.

## Current status

The page is now connected to the backend. Downloads run as **background jobs** with live progress (percent, speed, ETA), **no file-size cap** and **no request timeout**, so long and large videos work when you run the server on your own computer.

## How it works (website + local helper)

- The **website** (`index.html`) is hosted on Cloudflare Pages and is the same for everyone.
- Each user runs the small **helper app** on their own device. It does the real downloading, with their own internet connection, so there is no size or length limit and no server cost for you.
- The website talks to the helper at `http://localhost:10000`. It shows a green box when connected, or a download link when the helper is not running.
- The helper **only accepts requests from this website** (and from localhost), so other websites cannot control it.

**Important setup for you (the owner):** in `backend/app.py`, `SITE_ORIGINS` is set to `https://ultravideodownloader.oussamakhouya73.workers.dev`. If you add a custom domain, add it there, then publish a new release so users get the updated helper. You can also allow extra domains without rebuilding via the `UVD_ALLOWED_ORIGINS` environment variable.

**Browser notes:** Chrome and Edge may ask to allow access to devices on the local network the first time: choose *Allow*. Safari blocks a public site from talking to localhost; in Safari, open `http://localhost:10000` instead (the helper serves the same page).

## Ready-made apps (no Python, no ffmpeg needed)

Open the **Releases** page of this repo and download the zip for your system:

- **Windows**: `UltraVideoDownloader-windows.zip` → unzip → double-click `UltraVideoDownloader.exe`. If SmartScreen warns, choose *More info → Run anyway* (the app is not code-signed).
- **macOS**: `UltraVideoDownloader-macos.zip` → unzip → right-click the file → *Open* (first time only).
- **Linux**: `UltraVideoDownloader-linux.zip` → unzip → `chmod +x UltraVideoDownloader` → run it.

A black window opens and your browser opens on the page. Files are saved in `Downloads/UltraVideoDownloader`. Keep the black window open while downloading.

**How the apps are built:** GitHub Actions builds them (`.github/workflows/build.yml`). To publish a new version, go to **Actions → Build apps → Run workflow** and enter a tag such as `v1.0.0`.

### Android

Android cannot run this server directly. Use a free open-source yt-dlp app instead, for example **YTDLnis** or **Seal** (from their GitHub releases or F-Droid). They run on your phone's own connection, with no size or length limits.

## Run locally (recommended for long / large videos)

Requirements: Python 3 and [ffmpeg](https://ffmpeg.org/) installed.

- Linux / macOS: `bash backend/run.sh`
- Windows: double-click `backend\run.bat`

Then open **http://localhost:10000**. Files are saved in `backend/downloads/`.

Optional environment variables: `UVD_DOWNLOAD_DIR`, `UVD_MAX_FILESIZE_MB` (0 = unlimited), `PORT`.

## Deploy on Cloudflare Pages

1. Open Cloudflare Dashboard → **Workers & Pages** → **Create** → **Pages** → **Connect to Git**.
2. Select `oussamakhouya73/UltraVideoDownloader`.
3. Framework preset: **None**.
4. Build command: leave empty.
5. Build output directory: `/` (repository root).
6. Deploy. The page is served from `index.html`.

Every push to the connected branch can trigger a new deployment.

## Next implementation steps

- Add a backend endpoint that retrieves metadata for sources the operator is authorized to support.
- Implement quality selection using actual available formats, not hard-coded promises.
- For separate video/audio streams, merge them with FFmpeg on an appropriate server or provide a user-side workflow.
- Add job limits, rate limiting, timeouts, file-size limits, and cleanup.
- Do not use Cloudflare Pages alone as a long-running video-processing server. Workers have execution/resource limits; large and long downloads need an architecture designed for them.

## Scope

Use only for videos you own or have permission to download. Source-site terms and access restrictions still apply.
