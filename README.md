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
  <img src="https://img.shields.io/badge/platform-linux-windows-success" alt="Linux">
  <img src="https://img.shields.io/badge/license-MIT-yellow" alt="License">
</p>

---

## 📥 Download

### Pre-built executable (no Python required)

| Platform | File | How to get it |
|----------|------|---------------|
| 🐧 Linux | `DownTube` | Run `./build.sh` → `dist/DownTube` |
| 🪟 Windows | `DownTube.exe` | Run `setup_windows.bat` → desktop shortcut created automatically |
| 🍎 macOS | `DownTube` | Run `./build.sh` → `dist/DownTube` |

### Run from source

```bash
git clone https://github.com/Prince000101/Downtube-Pro-download-any-vedio-form-online-linux-tool.git
cd DownTube
pip install PyQt5
python main.py
```

📌 **yt-dlp binary** must be placed next to the executable (or in your PATH) for downloads to work.

---

## 🚀 Setup

### 🐧 Linux

```bash
# 1. Clone
git clone https://github.com/Prince000101/Downtube-Pro-download-any-vedio-form-online-linux-tool.git
cd DownTube

# 2. Build standalone executable
./build.sh

# 3. Copy to desktop
cp dist/DownTube ~/Desktop/

# 4. Download yt-dlp and place next to executable
#    https://github.com/yt-dlp/yt-dlp/releases

# 5. Create desktop launcher
cat > ~/Desktop/downtube.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=DownTube
Comment=YouTube video & audio downloader
Exec=/home/$USER/Desktop/DownTube
Icon=/home/$USER/Desktop/icon.png
Terminal=false
Categories=AudioVideo;Utility;
EOF

chmod +x ~/Desktop/downtube.desktop
gio set ~/Desktop/downtube.desktop metadata::trusted true
```

### 🪟 Windows

```cmd
:: 1. Clone the repo (or download ZIP from GitHub)
git clone https://github.com/Prince000101/Downtube-Pro-download-any-vedio-form-online-linux-tool.git
cd DownTube

:: 2. Double-click setup_windows.bat — it does everything:
::    - Checks Python & Git are installed
::    - Installs dependencies (PyQt5, pyinstaller)
::    - Builds DownTube.exe
::    - Copies it to your desktop

:: 3. Download yt-dlp.exe and place next to the executable:
::    https://github.com/yt-dlp/yt-dlp/releases
```

### 🍎 macOS

```bash
# Clone & build
git clone https://github.com/Prince000101/Downtube-Pro-download-any-vedio-form-online-linux-tool.git
cd DownTube
./build.sh

# Copy to desktop
cp dist/DownTube ~/Desktop/

# Download yt-dlp and place next to executable
# https://github.com/yt-dlp/yt-dlp/releases
```

---

## 🍪 Cookies for restricted content

Some YouTube videos (age-restricted, private, or unlisted) require you to be signed in.

### Export cookies from your browser

1. Install the [Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookies-txt/) Chrome extension, or use the [Firefox version](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)
2. Log into YouTube in your browser
3. Click the extension icon → **Export** → save as `cookies.txt`
4. Place `cookies.txt` next to the executable (or in the project root)

### Auto-export from Firefox (Linux)

```bash
yt-dlp --cookies-from-browser firefox --cookies cookies.txt
```

### Troubleshooting

- **"Sign in to confirm you're not a bot"** → Your cookies are expired or missing. Export fresh ones.
- **Cookies expire** every few months — re-export when downloads stop working.
- The app logs `[COOKIE]` warnings when it detects cookie-related errors.
- No cookies are needed for public videos.

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

## Project structure

```
DownTube/
├── main.py                 # Application entry point
├── requirements.txt        # PyQt5>=5.15.0
├── icon.png                # Application icon
├── build.sh                # Linux/macOS build script
├── setup_windows.bat       # Windows setup script
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
└── theme/                  # Material Design 3 theming
    ├── manager.py          # Theme engine + QSS generation
    ├── colors.py           # 4 color schemes x Dark/Light
    └── icons.py            # 16 programmatic icons (QPainter)
```

---

## Theming

DownTube includes a full Material Design 3 theming engine:

| Theme    | Seed Color | Vibe        |
|----------|------------|-------------|
| Ocean    | `#1565C0`  | Blue        |
| Forest   | `#2E7D32`  | Green       |
| Lavender | `#7B1FA2`  | Purple      |
| Ember    | `#D84315`  | Red/Orange  |
| Grey     | `#616161`  | Monochrome  |

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
