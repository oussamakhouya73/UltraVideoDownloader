# UltraVideoDownloader

A responsive dark-mode frontend prototype for a video downloader, intended for deployment on Cloudflare Pages.

## Current status

The page is now connected to the backend. Downloads run as **background jobs** with live progress (percent, speed, ETA), **no file-size cap** and **no request timeout**, so long and large videos work when you run the server on your own computer.

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
