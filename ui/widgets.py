import os
import json
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QProgressBar, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QPixmap, QFont, QIcon

from core.queue import (
    DownloadItem, STATUS_QUEUED, STATUS_DOWNLOADING,
    STATUS_COMPLETED, STATUS_ERROR, STATUS_CANCELLED
)


def format_duration(seconds):
    if not seconds:
        return ""
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def format_bytes(n):
    if not n:
        return ""
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"


class VideoCard(QFrame):
    def __init__(self, item, index, theme_manager, parent=None):
        super().__init__(parent)
        self.item = item
        self.index = index
        self.theme_manager = theme_manager
        self.setObjectName("videoCard")
        self.setup_ui()

    def setup_ui(self):
        self.setMinimumHeight(76)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        self.thumb_label = QLabel("🎬")
        self.thumb_label.setFixedSize(72, 48)
        self.thumb_label.setAlignment(Qt.AlignCenter)
        self.thumb_label.setStyleSheet("font-size: 22px; border-radius: 6px;")
        layout.addWidget(self.thumb_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        self.title_label = QLabel(self.item.title)
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("font-weight: 600; font-size: 13px;")
        self.title_label.setMaximumHeight(36)
        info_layout.addWidget(self.title_label)

        meta_row = QHBoxLayout()
        self.status_icon = QLabel()
        self.status_icon.setFixedWidth(16)
        meta_row.addWidget(self.status_icon)
        self._update_status_icon()

        self.meta_label = QLabel()
        self.meta_label.setStyleSheet("color: palette(mid); font-size: 11px;")
        meta_row.addWidget(self.meta_label)
        meta_row.addStretch()
        info_layout.addLayout(meta_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setValue(self.item.progress)
        self.progress_bar.setVisible(self.item.status == STATUS_DOWNLOADING)
        info_layout.addWidget(self.progress_bar)

        self.speed_label = QLabel()
        self.speed_label.setStyleSheet("color: palette(mid); font-size: 10px;")
        info_layout.addWidget(self.speed_label)

        layout.addLayout(info_layout, 1)

        self.cancel_btn = None
        self.retry_btn = None

        if self.item.status in (STATUS_DOWNLOADING, STATUS_QUEUED):
            self.cancel_btn = QPushButton()
            self.cancel_btn.setObjectName("icon")
            self.cancel_btn.setFixedSize(32, 32)
            self.cancel_btn.setToolTip("Cancel")
            layout.addWidget(self.cancel_btn)

        if self.item.status == STATUS_ERROR:
            self.retry_btn = QPushButton()
            self.retry_btn.setObjectName("icon")
            self.retry_btn.setFixedSize(32, 32)
            self.retry_btn.setToolTip("Retry")
            layout.addWidget(self.retry_btn)

        QTimer.singleShot(0, self._set_icons)

    def _set_icons(self):
        s = self.theme_manager
        if self.cancel_btn:
            self.cancel_btn.setIcon(s.icon("close", 16))
            self.cancel_btn.setIconSize(QSize(16, 16))
        if self.retry_btn:
            self.retry_btn.setIcon(s.icon("retry", 16))
            self.retry_btn.setIconSize(QSize(16, 16))

    def _update_status_icon(self):
        icons = {
            STATUS_QUEUED: "⏳",
            STATUS_DOWNLOADING: "⬇️",
            STATUS_COMPLETED: "✅",
            STATUS_ERROR: "❌",
            STATUS_CANCELLED: "⛔",
        }
        self.status_icon.setText(icons.get(self.item.status, ""))

    def update_progress(self, progress):
        self.item.progress = progress
        self.progress_bar.setValue(progress)
        self.progress_bar.setVisible(True)
        self.meta_label.setText(f"{progress}%")

    def update_speed(self, speed):
        self.item.speed = speed
        if speed:
            self.speed_label.setText(speed)

    def update_eta(self, eta):
        self.item.eta = eta
        meta = self.meta_label.text()
        if meta.endswith("%") and eta:
            self.meta_label.setText(f"{meta} • ETA {eta}")

    def update_status(self, status):
        self.item.status = status
        self._update_status_icon()


class PreviewWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("previewWidget")
        self.setMinimumHeight(140)
        self.info = None
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(16)

        self.thumb_label = QLabel("🎬")
        self.thumb_label.setFixedSize(140, 88)
        self.thumb_label.setAlignment(Qt.AlignCenter)
        self.thumb_label.setStyleSheet("font-size: 32px; border-radius: 8px;")
        layout.addWidget(self.thumb_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        self.title_label = QLabel("No video selected")
        self.title_label.setObjectName("subheading")
        self.title_label.setWordWrap(True)
        info_layout.addWidget(self.title_label)

        self.meta_label = QLabel("Paste a URL to see details")
        self.meta_label.setStyleSheet("color: palette(mid); font-size: 12px;")
        self.meta_label.setWordWrap(True)
        info_layout.addWidget(self.meta_label)

        self.format_btn = QPushButton("Select Format")
        self.format_btn.setObjectName("secondary")
        self.format_btn.setVisible(False)
        info_layout.addWidget(self.format_btn)

        info_layout.addStretch()
        layout.addLayout(info_layout, 1)

    def set_info(self, info):
        self.info = info
        title = info.get("title", "Unknown")
        self.title_label.setText(title)

        uploader = info.get("uploader", info.get("channel", ""))
        duration = format_duration(info.get("duration"))
        views = info.get("view_count", 0)
        parts = []
        if uploader:
            parts.append(f"👤 {uploader}")
        if duration:
            parts.append(f"⏱ {duration}")
        if views:
            parts.append(f"👁 {views:,}")
        self.meta_label.setText("  •  ".join(parts) if parts else "No metadata")

        thumb_url = info.get("thumbnail")
        if thumb_url:
            self.thumb_label.setText("📺")
            self.thumb_label.setToolTip(thumb_url)

        self.format_btn.setVisible(True)
