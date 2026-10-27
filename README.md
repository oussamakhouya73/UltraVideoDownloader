# UltraVideoDownloader

A responsive dark-mode frontend prototype for a video downloader, intended for deployment on Cloudflare Pages.

## Current status

This is currently **frontend only**. It validates the shape of a pasted URL and lets a user choose a target quality and format, but it does not fetch video metadata or download media yet. A real backend/download engine must be implemented and deployed before claiming support for 1080p/4K or long videos.

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
