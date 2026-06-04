#!/usr/bin/env bash
set -euo pipefail

pip3 install --user --break-system-packages pyinstaller PyQt5 2>/dev/null || true

pyinstaller --onefile --windowed \
    --name "DownTube" \
    --add-data "core:core" \
    --add-data "ui:ui" \
    --add-data "theme:theme" \
    --add-data "icon.png:." \
    --hidden-import "core.engine" \
    --hidden-import "core.queue" \
    --hidden-import "core.history" \
    --hidden-import "ui.main_window" \
    --hidden-import "ui.download_page" \
    --hidden-import "ui.history_page" \
    --hidden-import "ui.settings_page" \
    --hidden-import "ui.widgets" \
    --hidden-import "ui.format_dialog" \
    --hidden-import "ui.search_dialog" \
    --hidden-import "theme.manager" \
    --hidden-import "theme.colors" \
    --hidden-import "theme.icons" \
    main.py

echo ""
echo "Done! Executable at: dist/DownTube"
echo ""
echo "To deploy:"
echo "  cp dist/DownTube ~/Desktop/"
echo ""
echo "Note: Place a yt-dlp binary next to the executable"
echo "      for full functionality."
