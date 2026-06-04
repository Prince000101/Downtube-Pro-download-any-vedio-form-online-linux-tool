import os
import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QCheckBox, QTextEdit, QListWidget,
    QListWidgetItem, QFileDialog, QSplitter
)
from PyQt5.QtCore import Qt, QTimer, QSize

from core.queue import (
    DownloadItem, STATUS_QUEUED, STATUS_DOWNLOADING,
    STATUS_COMPLETED, STATUS_ERROR, STATUS_CANCELLED
)
from core.engine import DownloadEngine
from core.history import HistoryManager
from core import resource_path
from ui.widgets import VideoCard, PreviewWidget, format_duration
from ui.format_dialog import FormatDialog
from ui.search_dialog import SearchDialog


class DownloadPage(QWidget):
    def __init__(self, engine, queue, history, theme_manager, parent=None):
        super().__init__(parent)
        self.setObjectName("downloadPage")
        self.engine = engine
        self.queue = queue
        self.history = history
        self.theme_manager = theme_manager
        self._current_info = None
        self._current_formats = []
        self._current_index = -1
        self._last_url = ""
        self._fetch_timer = QTimer()
        self._fetch_timer.setSingleShot(True)
        self._fetch_timer.timeout.connect(self._do_fetch_info)
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
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube URL, playlist URL...")
        self.url_input.textChanged.connect(self._on_url_changed)
        input_layout.addWidget(self.url_input, 1)

        self.search_btn = QPushButton()
        self.search_btn.setObjectName("icon")
        self.search_btn.setToolTip("Search YouTube")
        self.search_btn.clicked.connect(self._open_search)
        self.search_btn.setFixedSize(40, 40)
        input_layout.addWidget(self.search_btn)

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

        self.format_btn = QPushButton("Format")
        self.format_btn.setObjectName("secondary")
        self.format_btn.setEnabled(False)
        self.format_btn.clicked.connect(self._select_format)
        options_layout.addWidget(self.format_btn)

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

        self.preview = PreviewWidget()
        self.preview.format_btn.clicked.connect(self._select_format)
        self.preview.setVisible(False)
        layout.addWidget(self.preview)

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

        splitter = QSplitter(Qt.Vertical)

        queue_widget = QWidget()
        queue_layout = QVBoxLayout(queue_widget)
        queue_layout.setContentsMargins(0, 0, 0, 0)
        queue_layout.setSpacing(4)

        queue_header = QLabel("Queue")
        queue_header.setObjectName("subheading")
        queue_layout.addWidget(queue_header)

        self.queue_list = QListWidget()
        self.queue_list.setMinimumHeight(120)
        self.queue_list.setAlternatingRowColors(False)
        queue_layout.addWidget(self.queue_list, 1)
        splitter.addWidget(queue_widget)

        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        log_layout.setContentsMargins(0, 0, 0, 0)
        log_layout.setSpacing(4)

        log_header = QLabel("Log")
        log_header.setObjectName("subheading")
        log_layout.addWidget(log_header)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMinimumHeight(100)
        log_layout.addWidget(self.log_output)
        splitter.addWidget(log_widget)

        layout.addWidget(splitter, 1)

        QTimer.singleShot(0, self._update_icons)

    def _update_icons(self):
        s = self.theme_manager
        self.search_btn.setIcon(s.icon("search", 20))
        self.search_btn.setIconSize(QSize(20, 20))
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
        self.engine.log_line.connect(self.log_output.append)
        self.engine.finished.connect(self._on_download_finished)
        self.engine.video_info_ready.connect(self._on_info_ready)
        self.queue.item_added.connect(self._rebuild_queue)
        self.queue.item_removed.connect(self._rebuild_queue)
        self.queue.item_changed.connect(self._on_item_changed)
        self.queue.current_changed.connect(self._on_current_changed)
        self.queue.all_completed.connect(self._on_all_completed)

    def _on_url_changed(self, url):
        url = url.strip()
        if url and url != self._last_url and url.startswith("http"):
            self._last_url = url
            self._fetch_timer.start(800)

    def _do_fetch_info(self):
        url = self._last_url
        if not url or not url.startswith("http"):
            return
        self._current_info = None
        self._current_formats = []
        self.format_btn.setEnabled(False)
        self.preview.setVisible(False)

        info = self.engine.fetch_info(url)
        if info:
            self._current_info = info
            formats = info.get("formats", [])
            if formats:
                self._current_formats = formats
                self.format_btn.setEnabled(True)
            self.preview.set_info(info)
            self.preview.setVisible(True)

    def _open_search(self):
        dialog = SearchDialog(self.engine.search, self)
        if dialog.exec() == SearchDialog.Accepted and dialog.selected_url:
            self.url_input.setText(dialog.selected_url)
            self._last_url = ""

    def _load_url_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open URL List", "", "Text Files (*.txt)")
        if not file_path:
            return
        with open(file_path, "r") as f:
            urls = [line.strip() for line in f if line.strip()]
        if not urls:
            return
        items = [DownloadItem(url) for url in urls]
        self.queue.add_multiple(items)
        self.log_output.append(f"Loaded {len(urls)} URLs from file.")

    def _select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if folder:
            self.folder_input.setText(folder)

    def _select_format(self):
        if not self._current_formats:
            return
        formats = self._current_formats
        dialog = FormatDialog(formats, self)
        if dialog.exec() == FormatDialog.Accepted and dialog.selected_format:
            fmt = dialog.selected_format
            self.log_output.append(
                f"Selected format: {fmt.get('format_id')} - "
                f"{fmt.get('resolution', '')} ({fmt.get('ext', '')})"
            )

    def _start_download(self):
        url = self.url_input.text().strip()
        if not url:
            self.log_output.append("Please enter a URL.")
            return

        output_folder = self.folder_input.text().strip()
        if not output_folder:
            output_folder = os.path.expanduser("~/Downloads")
            self.folder_input.setText(output_folder)

        download_video = self.video_cb.isChecked()
        download_audio = self.audio_cb.isChecked()
        use_subfolder = self.subfolder_cb.isChecked()

        if not download_video and not download_audio:
            download_video = True

        extra_args = []
        template = "%(title)s.%(ext)s"
        if use_subfolder:
            template = "%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s"
        output_template = os.path.join(output_folder, template)

        if download_video and not download_audio:
            extra_args += ["-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]", "--merge-output-format", "mp4"]
        elif download_audio and not download_video:
            extra_args += [
                "-x", "--audio-format", "mp3", "--audio-quality", "0",
                "--embed-thumbnail", "--embed-metadata",
                "--convert-thumbnails", "jpg"
            ]
        else:
            extra_args += ["-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]", "--merge-output-format", "mp4"]

        info = self._current_info
        item = DownloadItem(
            url=url,
            title=info.get("title", url) if info else url,
            thumbnail=info.get("thumbnail", "") if info else "",
            duration=info.get("duration") if info else None,
            uploader=info.get("uploader", info.get("channel", "")) if info else "",
            output_template=output_template,
            extra_args=extra_args,
        )
        self.queue.add(item)

        if not self.engine.is_running():
            self._process_queue()

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
                        url=item.url, title=item.title, thumbnail=item.thumbnail,
                        duration=item.duration, uploader=item.uploader,
                        format_id=item.format_id, status="completed"
                    )
                else:
                    self.queue.update_item(self._current_index, status=STATUS_ERROR)
                    self.history.add_entry(
                        url=item.url, title=item.title,
                        format_id=item.format_id, status="error"
                    )
        QTimer.singleShot(500, self._process_queue)

    def _on_info_ready(self, info):
        pass

    def _on_item_changed(self, index):
        self._rebuild_queue()

    def _on_current_changed(self, item):
        pass

    def _on_all_completed(self):
        self.log_output.append("All downloads completed.")
        self.cancel_btn.setEnabled(False)

    def _rebuild_queue(self):
        self.queue_list.clear()
        for i, item in enumerate(self.queue.items):
            card = VideoCard(item, i, self.theme_manager)
            if hasattr(card, "cancel_btn"):
                card.cancel_btn.clicked.connect(lambda checked, idx=i: self._remove_item(idx))
            if hasattr(card, "retry_btn"):
                card.retry_btn.clicked.connect(lambda checked, idx=i: self._retry_item(idx))
            widget_item = QListWidgetItem(self.queue_list)
            widget_item.setSizeHint(card.sizeHint())
            self.queue_list.addItem(widget_item)
            self.queue_list.setItemWidget(widget_item, card)

    def _remove_item(self, index):
        item = self.queue.get(index)
        if item and item.status == STATUS_DOWNLOADING:
            self.engine.cancel()
        self.queue.remove(index)

    def _retry_item(self, index):
        item = self.queue.get(index)
        if item:
            self.queue.update_item(index, status=STATUS_QUEUED, progress=0, error_msg="")
            if not self.engine.is_running():
                self._process_queue()

    def _clear(self):
        self.engine.cancel()
        self.queue.clear()
        self.url_input.clear()
        self.log_output.clear()
        self.preview.setVisible(False)
        self._current_info = None
        self._current_formats = []
        self.format_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.download_btn.setEnabled(True)
