<p align="center">
  <img src="icon.png" alt="DownTube Icon" width="120">
</p>

<h1 align="center">DownTube</h1>

<p align="center">
  <strong>A modern PyQt5 GUI for yt-dlp</strong><br>
  Download YouTube videos, audio, and playlists with a clean Material Design 3 interface.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue" alt="Python">
  <img src="https://img.shields.io/badge/platform-linux-success" alt="Linux">
  <img src="https://img.shields.io/badge/license-MIT-yellow" alt="License">
</p>

---

## Features

- **Download videos** as MP4 with best video + audio merging
- **Extract audio** as MP3 with embedded metadata and thumbnails
- **Playlist support** — download full playlists with optional subfolder organization
- **Format selection** — interactive dialog to choose specific video/audio formats
- **Download queue** — batch multiple downloads with progress tracking
- **YouTube search** — search directly within the app via yt-dlp's search
- **Batch URLs** — load multiple URLs from a `.txt` file
- **Download history** — persistent SQLite database with status filtering
- **Cookies support** — login-protected downloads via exported browser cookies
- **4 color schemes** — Ocean, Forest, Lavender, Ember (Dark & Light modes)
- **Material Design 3** — fully styled UI with ~370 lines of QSS
- **Programmatic icons** — 16 SVG-like icons rendered with QPainter
- **Single-file executable** — build with PyInstaller
- **Cross-platform** — Linux primary, Windows supported

---

## Screenshots

<p align="center">
  <img src="screenshot/screenshot1.png" alt="Screenshot 1" width="45%">
  <img src="screenshot/screenshot2.png" alt="Screenshot 2" width="45%">
</p>

---

## Quick Start

### Prerequisites

- Python 3.10+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) binary in the project root (or in PATH)

### Run from source

```bash
# Clone
git clone https://github.com/Prince000101/Downtube-Pro-download-any-vedio-form-online-linux-tool.git
cd DownTube

# Virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

### Cookies (for restricted content)

1. Install [Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookies-txt/) browser extension
2. Log into YouTube, export cookies to `cookies.txt`
3. Place `cookies.txt` in the project root

---

## Usage

### Download a video

1. **Paste a URL** — the app auto-fetches video info (800ms debounce)
2. **Choose format** — toggle MP4/MP3, or open the Format dialog for advanced selection
3. **Pick a folder** — defaults to `~/Downloads`
4. **Click Download** — progress, speed, and ETA shown in real-time

### Download a playlist

- Paste a playlist URL, check **"Playlist subfolder"** to organize into `PlaylistName/N - Title.ext`

### Search YouTube

- Click the search icon next to the URL bar, type your query, and select a result

### Batch downloads

- Click the folder icon next to the URL bar, select a `.txt` file with one URL per line

### Themes

- **Settings → Theme** — choose between Dark/Light mode and 4 color schemes (Ocean, Forest, Lavender, Ember)

---

## Build standalone executable

### Linux (AppImage)

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --icon=icon.png \
  --add-data "yt-dlp:." \
  --add-data "cookies.txt:." \
  --add-data "icon.png:." \
  main.py
```

### Windows (exe)

```cmd
pip install pyinstaller
pyinstaller --onefile --noconsole --icon=icon.png ^
  --add-data "yt-dlp;." ^
  --add-data "cookies.txt;." ^
  --add-data "icon.png;." ^
  main.py
```

The executable appears in `dist/`.

---

## Project structure

```
DownTube/
├── main.py                 # Application entry point
├── requirements.txt        # PyQt5>=5.15.0
├── cookies.txt             # Browser cookies placeholder
├── icon.png                # Application icon
├── yt-dlp                  # Bundled yt-dlp binary
│
├── core/                   # Backend logic
│   ├── engine.py           # yt-dlp QProcess wrapper
│   ├── queue.py            # Download queue + item model
│   └── history.py          # SQLite history persistence
│
├── ui/                     # User interface
│   ├── main_window.py      # Main window + sidebar navigation
│   ├── download_page.py    # Primary download interface
│   ├── history_page.py     # Download history table
│   ├── settings_page.py    # Theme & preferences
│   ├── format_dialog.py    # Advanced format selection
│   ├── search_dialog.py    # YouTube search
│   └── widgets.py          # VideoCard, PreviewWidget, utilities
│
├── theme/                  # Material Design 3 theming
│   ├── manager.py          # Theme engine + QSS generation
│   ├── colors.py           # 4 color schemes x Dark/Light
│   └── icons.py            # 16 programmatic icons (QPainter)
│
└── screenshot/             # Screenshots
```

---

## Theming

DownTube includes a full Material Design 3 theming engine:

| Theme    | Seed Color | Vibe    |
|----------|------------|---------|
| Ocean    | `#1565C0`  | Blue    |
| Forest   | `#2E7D32`  | Green   |
| Lavender | `#7B1FA2`  | Purple  |
| Ember    | `#D84315`  | Red/Orange |

Each scheme has **Light** and **Dark** modes with ~30 color tokens applied via QPalette and a comprehensive QSS stylesheet.

Icons are rendered programmatically using QPainter — no external icon assets needed.

---

## Technical highlights

- **Download engine** wraps yt-dlp in a `QProcess` with real-time stdout parsing for progress/speed/ETA
- **Debounced URL fetch** (800ms) prevents excessive API calls while typing
- **Queue system** processes one download at a time with automatic advancement and retry support
- **History** stored in SQLite with status-based filtering (All/Completed/Error/Cancelled)
- **Format dialog** presents a sortable table with ID, extension, resolution, codec, filesize
- **Resource resolution** supports both development and PyInstaller-bundled modes

---

## License

This project uses [yt-dlp](https://github.com/yt-dlp/yt-dlp) and respects its license. Use responsibly.

<p align="center">
  <sub>Made with passion. Happy downloading!</sub>
</p>
