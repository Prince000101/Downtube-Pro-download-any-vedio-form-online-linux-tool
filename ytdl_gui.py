import sys
import os
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFileDialog, QCheckBox, QTextEdit,
    QProgressBar
)
from PyQt5.QtCore import Qt, QProcess
from PyQt5.QtGui import QPalette, QColor, QIcon

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller bundle """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class YTDLPGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ytdl-GUI")
        self.setMinimumSize(700, 480)

        icon_path = resource_path("icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.download_queue = []

        # URL input + file button
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste YouTube or playlist URL")

        self.file_button = QPushButton("📄")
        self.file_button.setFixedWidth(30)
        self.file_button.setToolTip("Select .txt file with links")
        self.file_button.clicked.connect(self.load_url_file)

        url_layout = QHBoxLayout()
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.file_button)

        # Checkboxes
        self.video_checkbox = QCheckBox("Download Video (MP4)")
        self.video_checkbox.setChecked(True)

        self.audio_checkbox = QCheckBox("Download Audio (MP3)")
        self.audio_checkbox.setChecked(False)

        self.subfolder_checkbox = QCheckBox("Create Subfolder by Playlist")
        self.subfolder_checkbox.setChecked(False)

        # Folder selection
        self.folder_input = QLineEdit()
        self.folder_button = QPushButton("Choose Folder")
        self.folder_button.clicked.connect(self.select_folder)

        # Theme toggle
        self.theme_toggle = QCheckBox("🌞 Dark Mode")
        self.theme_toggle.setChecked(True)
        self.theme_toggle.stateChanged.connect(self.toggle_theme)

        # Download and clear buttons
        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.prepare_download)

        self.clear_button = QPushButton("Clear All")
        self.clear_button.clicked.connect(self.clear_all_fields)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(QLabel("YouTube URL or Playlist:"))
        layout.addLayout(url_layout)
        layout.addWidget(self.video_checkbox)
        layout.addWidget(self.audio_checkbox)

        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(self.folder_button)
        layout.addWidget(QLabel("Download Folder:"))
        layout.addLayout(folder_layout)

        layout.addWidget(self.subfolder_checkbox)
        layout.addWidget(self.theme_toggle)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.clear_button)
        layout.addLayout(button_layout)

        layout.addWidget(self.progress_bar)
        layout.addWidget(QLabel("Output Log:"))
        layout.addWidget(self.log_output)

        self.setLayout(layout)

        # Process setup
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)

        self.apply_theme(self.theme_toggle.isChecked())

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if folder:
            self.folder_input.setText(folder)

    def load_url_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open URL list", "", "Text Files (*.txt)")
        if file_path:
            with open(file_path, "r") as f:
                links = [line.strip() for line in f if line.strip()]
            if links:
                self.download_queue = links
                self.log_output.append(f"📝 Loaded {len(links)} URLs from file.")
                self.url_input.setText(links[0])

    def prepare_download(self):
        self.download_button.setEnabled(False)
        self.clear_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_output.clear()

        url_text = self.url_input.text().strip()
        if self.download_queue:
            self.urls_to_download = self.download_queue[:]
        elif url_text:
            self.urls_to_download = [url_text]
        else:
            self.log_output.append("❌ No URL or file provided.")
            self.download_button.setEnabled(True)
            self.clear_button.setEnabled(True)
            return

        self.download_next_url()

    def download_next_url(self):
        if not self.urls_to_download:
            self.download_button.setEnabled(True)
            self.clear_button.setEnabled(True)
            self.progress_bar.setValue(100)
            self.log_output.append("✅ All downloads completed.")
            self.download_queue.clear()
            return

        url = self.urls_to_download.pop(0)
        self.log_output.append(f"➡️ Starting download: {url}")
        self.run_download(url)

    def run_download(self, url):
        output_folder = self.folder_input.text().strip()
        download_audio = self.audio_checkbox.isChecked()
        download_video = self.video_checkbox.isChecked()
        use_subfolder = self.subfolder_checkbox.isChecked()

        if not output_folder or not (download_audio or download_video):
            self.log_output.append("❌ Please select a format and output folder.")
            self.download_button.setEnabled(True)
            self.clear_button.setEnabled(True)
            return

        yt_dlp_path = resource_path("yt-dlp.exe" if sys.platform == "win32" else "yt-dlp")
        cookies_path = resource_path("cookies.txt")

        template = "%(title)s.%(ext)s"
        if use_subfolder:
            template = "%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s"
        output_template = os.path.join(output_folder, template)

        cmd = [yt_dlp_path, url, "-o", output_template]

        if download_audio:
            cmd += [
                "-x", "--audio-format", "mp3", "--audio-quality", "0",
                "--embed-thumbnail", "--embed-metadata",
                "--convert-thumbnails", "jpg"
            ]
        elif download_video:
            cmd += ["-f", "bestvideo+bestaudio", "--merge-output-format", "mp4"]

        if os.path.exists(cookies_path):
            cmd += ["--cookies", cookies_path]

        # Removed: cmd += ["--download-archive", archive_path]
        # Removed because it was causing a problem with overlapig downloading both mp3 and mp4 at the same time.couldnot bother to fix it.
        self.process.start(cmd[0], cmd[1:])

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode()
        self.log_output.append(data.strip())
        match = re.search(r"(\d{1,3}\.\d)%", data)
        if match:
            percent = float(match.group(1))
            self.progress_bar.setValue(int(percent))

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode()
        self.log_output.append(data.strip())

    def process_finished(self):
        self.progress_bar.setValue(100)
        self.log_output.append("✅ Download finished.")
        self.download_next_url()

    def toggle_theme(self):
        self.apply_theme(self.theme_toggle.isChecked())

    def apply_theme(self, dark_mode: bool):
        palette = QPalette()
        if dark_mode:
            palette.setColor(QPalette.Window, QColor(30, 30, 30))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(20, 20, 20))
            palette.setColor(QPalette.AlternateBase, QColor(30, 30, 30))
            palette.setColor(QPalette.ToolTipBase, Qt.white)
            palette.setColor(QPalette.ToolTipText, Qt.white)
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(45, 45, 45))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, Qt.black)
        else:
            palette = QApplication.style().standardPalette()
        QApplication.instance().setPalette(palette)

    def clear_all_fields(self):
        self.url_input.clear()
        self.folder_input.clear()
        self.video_checkbox.setChecked(True)
        self.audio_checkbox.setChecked(False)
        self.subfolder_checkbox.setChecked(False)
        self.theme_toggle.setChecked(True)
        self.log_output.clear()
        self.progress_bar.setValue(0)
        self.download_queue.clear()
        self.apply_theme(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YTDLPGUI()
    window.show()
    sys.exit(app.exec_())
