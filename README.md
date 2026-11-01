# UltraVideoDownloader

Download videos in HD / 4K with **no size or length limit**. The app runs on your own device, with your own internet connection.

- **Website** (`index.html`): a landing page hosted on Cloudflare, with download buttons.
- **Windows app**: opens in its own window (no console, no Python, no setup).
- **macOS / Linux**: the same app, opens in your browser at `http://127.0.0.1:10000`.
- **Android**: our own app is planned; meanwhile use a free open-source app such as [YTDLnis](https://github.com/deniscerri/ytdlnis) or [Seal](https://github.com/JunkFood02/Seal).

Use only for videos you own or have permission to download. Source-site terms still apply.

## For users

Go to the **Releases** page. On Windows download `UltraVideoDownloader-Setup.exe` and run it: it adds a desktop shortcut and a Start menu entry (no admin rights needed), and the app updates itself. A portable zip is also attached, and zips for macOS / Linux.
On Windows, if SmartScreen warns, choose *More info → Run anyway* (the app is not code-signed).

Features: link check with preview (thumbnail, title, length), automatic best available quality (only the qualities the video really has are listed), **Save to…** folder picker, pause / resume, automatic resume after internet loss or after closing the app, light / dark / auto theme, English / Arabic / French / Spanish, update banner.

## For the owner

- `index.html` + `privacy.html` are the public site (deployed by Cloudflare on every push). `site.js` holds the translations and the anonymous visit statistics, `site-config.js` the PostHog key.
- `app.html` is the downloader UI, bundled inside the app and served by it (same origin as the API).
- `backend/app.py` is the local Flask + yt-dlp server (jobs, pause/resume, settings, update, statistics).
- On Windows the app uses [pywebview](https://pywebview.flowrl.com/) (Edge WebView2). If a window cannot be opened it falls back to the default browser.
- `installer/UltraVideoDownloader.iss` builds the Windows installer (Inno Setup), `assets/` holds the icon.

### Publish a new version

GitHub → **Actions → Build apps → Run workflow**, enter a tag such as `v1.2.0`. The workflow writes the version into the app, builds Windows (installer + zip), macOS and Linux, and attaches them to the release. Every installed app checks the latest release and shows an **Update** button (Windows installs it by itself).

### Statistics (PostHog)

1. Create a free account at posthog.com (choose the EU region), create a project, copy the **Project API key** (`phc_...`).
2. Paste it in `backend/uvd_config.py` (`POSTHOG_KEY`) for the app and in `site-config.js` for the website, push, and publish a new release.
3. In PostHog you see: users (unique install ids), sessions and their length, countries, versions and languages, downloads started / completed / failed, website visits and download-button clicks.

The app sends only: random install id, version, OS, language, session length and download counts/outcomes. Never links, titles or file names. Users can switch it off in Settings; `privacy.html` describes it. While the key is empty nothing is sent.

### Ads

Ad code is third-party, so it never runs inside the app page. Instead the website hosts two tiny frames and both the website and the app embed them:

- `ads/banner.html`: desktop banner (728x90)
- `ads/banner-small.html`: phone banner (320x50)

Paste the banner code from your ad network inside the `#ad` div of each file and push. The change is live on the website **and inside the app at once, with no new release**. While a frame is empty, its slot stays collapsed and invisible.

Slots: two on the website (under the device list, above the footer) and one in the app (under the download box).

Rules to keep your account safe: banners only inside these frames (no popunder or social bar in the app), never click your own ads or ask others to, keep the number of ads low, and add your contact details to `privacy.html` before applying to a network. Visitors from the EU/UK may need a consent banner: check your network's requirements.

The app only accepts API calls from itself (`127.0.0.1`), and its Content-Security-Policy only allows a frame from `SITE_URL` in `backend/app.py`. If you move to a custom domain, change `SITE_URL` (and the `SITE` constant in `app.html`) and publish a new release.

### Run from source

```
pip install -r backend/requirements.txt
python backend/app.py        # then open http://127.0.0.1:10000
```

Needs ffmpeg on PATH, or the bundled one from `imageio-ffmpeg` is used.

Environment variables: `PORT`, `UVD_DOWNLOAD_DIR`, `UVD_MAX_FILESIZE_MB` (0 = unlimited), `UVD_ALLOWED_ORIGINS`.
