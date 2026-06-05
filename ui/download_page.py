import os
import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QPlainTextEdit, QCheckBox, QTextEdit, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer, QSize

from core.queue import (
    DownloadItem, STATUS_QUEUED, STATUS_DOWNLOADING,
    STATUS_COMPLETED, STATUS_ERROR, STATUS_CANCELLED
)
from core.engine import DownloadEngine
from core.history import HistoryManager
from core import resource_path


class DownloadPage(QWidget):
    def __init__(self, engine, queue, history, theme_manager, parent=None):
        super().__init__(parent)
        self.setObjectName("downloadPage")
        self.engine = engine
        self.queue = queue
        self.history = history
        self.theme_manager = theme_manager
        self._current_index = -1
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        heading = QLabel("DownTube")
        heading.setObjectName("heading")
        layout.addWidget(heading)

        subtitle = QLabel("YouTube video & audio downloader")
        subtitle.setObjectName("caption")
        layout.addWidget(subtitle)

        input_layout = QHBoxLayout()
        self.url_input = QPlainTextEdit()
        self.url_input.setPlaceholderText("Paste YouTube URLs (one per line)...")
        self.url_input.setMinimumHeight(60)
        self.url_input.setMaximumHeight(100)
        input_layout.addWidget(self.url_input, 1)

        self.add_btn = QPushButton()
        self.add_btn.setObjectName("icon")
        self.add_btn.setToolTip("Add all URLs to queue")
        self.add_btn.clicked.connect(self._add_to_queue)
        self.add_btn.setFixedSize(40, 40)
        input_layout.addWidget(self.add_btn)

        self.file_btn = QPushButton()
        self.file_btn.setObjectName("icon")
        self.file_btn.setToolTip("Load URLs from .txt file")
        self.file_btn.clicked.connect(self._load_url_file)
        self.file_btn.setFixedSize(40, 40)
        input_layout.addWidget(self.file_btn)
        layout.addLayout(input_layout)

        options_layout = QHBoxLayout()
        self.video_cb = QCheckBox("MP4 Video")
        self.video_cb.setChecked(True)
        options_layout.addWidget(self.video_cb)

        self.audio_cb = QCheckBox("MP3 Audio")
        self.audio_cb.setChecked(False)
        options_layout.addWidget(self.audio_cb)

        self.subfolder_cb = QCheckBox("Playlist subfolder")
        self.subfolder_cb.setChecked(False)
        options_layout.addWidget(self.subfolder_cb)

        options_layout.addStretch()
        layout.addLayout(options_layout)

        folder_layout = QHBoxLayout()
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Download folder...")
        folder_layout.addWidget(self.folder_input, 1)

        self.folder_btn = QPushButton()
        self.folder_btn.setObjectName("icon")
        self.folder_btn.setToolTip("Choose download folder")
        self.folder_btn.clicked.connect(self._select_folder)
        self.folder_btn.setFixedSize(40, 40)
        folder_layout.addWidget(self.folder_btn)
        layout.addLayout(folder_layout)

        action_layout = QHBoxLayout()
        self.download_btn = QPushButton("Download")
        self.download_btn.setMinimumHeight(44)
        self.download_btn.clicked.connect(self._start_download)
        action_layout.addWidget(self.download_btn)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setObjectName("secondary")
        self.clear_btn.clicked.connect(self._clear)
        action_layout.addWidget(self.clear_btn)

        self.cancel_btn = QPushButton()
        self.cancel_btn.setObjectName("secondary")
        self.cancel_btn.setToolTip("Cancel current download")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self._cancel_current)
        self.cancel_btn.setFixedSize(40, 40)
        action_layout.addWidget(self.cancel_btn)
        layout.addLayout(action_layout)

        log_header = QLabel("Log")
        log_header.setObjectName("subheading")
        layout.addWidget(log_header)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(220)
        layout.addWidget(self.log_output, 1)

        QTimer.singleShot(0, self._update_icons)

    def _update_icons(self):
        s = self.theme_manager
        self.add_btn.setIcon(s.icon("arrow_down", 20))
        self.add_btn.setIconSize(QSize(20, 20))
        self.file_btn.setIcon(s.icon("folder", 20))
        self.file_btn.setIconSize(QSize(20, 20))
        self.folder_btn.setIcon(s.icon("folder", 20))
        self.folder_btn.setIconSize(QSize(20, 20))
        self.cancel_btn.setIcon(s.icon("close", 20))
        self.cancel_btn.setIconSize(QSize(20, 20))

    def connect_signals(self):
        self.engine.progress_changed.connect(self._on_progress)
        self.engine.speed_changed.connect(self._on_speed)
        self.engine.eta_changed.connect(self._on_eta)
        self.engine.size_changed.connect(self._on_size)
        self.engine.log_line.connect(self.log_output.append)
        self.engine.finished.connect(self._on_download_finished)
        self.queue.all_completed.connect(self._on_all_completed)

    def _all_urls(self):
        return [line.strip() for line in self.url_input.toPlainText().split("\n")
                if line.strip().startswith("http")]

    def _build_args(self):
        download_video = self.video_cb.isChecked()
        download_audio = self.audio_cb.isChecked()
        use_subfolder = self.subfolder_cb.isChecked()
        if not download_video and not download_audio:
            download_video = True

        extra_args = []
        template = "%(title)s.%(ext)s"
        if use_subfolder:
            template = "%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s"
        output_template = os.path.join(self.folder_input.text().strip() or os.path.expanduser("~/Downloads"), template)

        if download_video and not download_audio:
            extra_args += ["-f", "bestvideo+bestaudio", "--merge-output-format", "mp4"]
        elif download_audio and not download_video:
            extra_args += [
                "-x", "--audio-format", "mp3", "--audio-quality", "0",
                "--embed-thumbnail", "--embed-metadata",
                "--convert-thumbnails", "jpg"
            ]
        else:
            extra_args += ["-f", "bestvideo+bestaudio", "--merge-output-format", "mp4"]

        if download_audio and not download_video:
            dtype = "mp3"
        elif use_subfolder:
            dtype = "playlist"
        else:
            dtype = "mp4"

        return output_template, extra_args, dtype

    def _queue_urls(self, urls, output_template, extra_args, dtype):
        titles = self.engine.fetch_titles(urls)
        count = 0
        for i, url in enumerate(urls):
            title = titles[i] if i < len(titles) and titles[i] else url
            item = DownloadItem(
                url=url, title=title,
                output_template=output_template,
                extra_args=list(extra_args),
            )
            item.download_type = dtype
            self.queue.add(item)
            count += 1
        return count

    def _add_to_queue(self):
        urls = self._all_urls()
        if not urls:
            return
        output_template, extra_args, dtype = self._build_args()
        count = self._queue_urls(urls, output_template, extra_args, dtype)
        self.log_output.append(f"Queued {count} URL(s).")

    def _start_download(self):
        urls = self._all_urls()
        if not urls:
            self.log_output.append("Please enter at least one URL.")
            return

        if not self.folder_input.text().strip():
            self.folder_input.setText(os.path.expanduser("~/Downloads"))

        output_template, extra_args, dtype = self._build_args()
        count = self._queue_urls(urls, output_template, extra_args, dtype)
        self.log_output.append(f"Queued {count} URL(s).")

        if not self.engine.is_running():
            self._process_queue()

    def _load_url_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open URL List", "", "Text Files (*.txt)")
        if not file_path:
            return
        with open(file_path, "r") as f:
            urls = [line.strip() for line in f if line.strip()]
        if not urls:
            return
        output_template, extra_args, dtype = self._build_args()
        count = self._queue_urls(urls, output_template, extra_args, dtype)
        self.log_output.append(f"Queued {count} URLs from file.")
        if not self.engine.is_running():
            self._process_queue()

    def _select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if folder:
            self.folder_input.setText(folder)

    def _process_queue(self):
        next_item = self.queue.next()
        if next_item:
            self._download_item(next_item)

    def _download_item(self, item):
        self._current_index = self.queue.current_index
        self.download_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.engine.start_download(item.url, item.output_template, item.extra_args)

    def _cancel_current(self):
        self.engine.cancel()

    def _on_progress(self, pct):
        if self._current_index >= 0:
            self.queue.update_item(self._current_index, progress=pct)

    def _on_speed(self, speed):
        if self._current_index >= 0:
            self.queue.update_item(self._current_index, speed=speed)

    def _on_eta(self, eta):
        if self._current_index >= 0:
            self.queue.update_item(self._current_index, eta=eta)

    def _on_size(self, size):
        if self._current_index >= 0:
            self.queue.update_item(self._current_index, total_size=size)

    def _on_download_finished(self, success, msg):
        self.cancel_btn.setEnabled(False)
        self.download_btn.setEnabled(True)
        if self._current_index >= 0:
            item = self.queue.get(self._current_index)
            if item:
                if success:
                    self.queue.update_item(self._current_index, status=STATUS_COMPLETED,
                                           progress=100, completed_time=time.time())
                    self.history.add_entry(
                        url=item.url, title=item.title,
                        format_id=item.format_id, status="completed"
                    )
                else:
                    self.queue.update_item(self._current_index, status=STATUS_ERROR)
                    self.history.add_entry(
                        url=item.url, title=item.title,
                        format_id=item.format_id, status="error"
                    )
        QTimer.singleShot(500, self._process_queue)

    def _on_all_completed(self):
        self.log_output.append("All downloads completed.")
        self.cancel_btn.setEnabled(False)

    def start_next_download(self):
        self._process_queue()

    def _clear(self):
        self.engine.cancel()
        self.queue.clear()
        self.url_input.setPlainText("")
        self.log_output.clear()
        self.cancel_btn.setEnabled(False)
        self.download_btn.setEnabled(True)
