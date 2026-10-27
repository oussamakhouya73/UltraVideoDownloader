# UltraVideoDownloader API

A small Flask + yt-dlp backend intended for personal downloads where the user has permission.

## Deploy on Render

1. Open Render and choose **New → Blueprint**.
2. Connect the `oussamakhouya73/UltraVideoDownloader` repository.
3. Review the service from `render.yaml` and deploy.
4. When deployment finishes, test `https://YOUR-SERVICE.onrender.com/api/health`.

The service may be slow to start on a free instance and has resource, request-duration, and temporary-storage limits. Large files and long videos may fail. This is a starter implementation, not a guarantee of 4K or universal source support. YouTube and other providers may change or block extraction; keep yt-dlp updated.

## API

- `GET /api/health`
- `POST /api/jobs` JSON body: `{"url":"https://...","format":"mp4","quality":"1080"}` → `{"id":"..."}`
- `GET /api/jobs/<id>` → status, percent, speed, eta
- `GET /api/jobs/<id>/file` → the finished file (supports resume)

Supported format values: `mp4`, `mp3`. Quality values: `best`, `2160`, `1440`, `1080`, `720`, `480`, `360`.

Before making this public, add per-IP rate limits, abuse controls, stronger SSRF protection (including DNS/IP checks), a source allowlist, and cleanup of temporary files. Only download content you own or have permission to save. Do not bypass DRM or access controls.
