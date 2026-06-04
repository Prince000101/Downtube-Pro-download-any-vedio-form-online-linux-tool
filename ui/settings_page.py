from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QFileDialog, QGroupBox, QFrame
)
from PyQt5.QtCore import Qt, QSize, QSettings, QTimer
from PyQt5.QtGui import QColor

from theme import THEMES, THEME_NAMES, DEFAULT_THEME


class SettingsPage(QWidget):
    def __init__(self, theme_manager, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsPage")
        self.theme_manager = theme_manager
        self.setup_ui()
        QTimer.singleShot(0, self._update_icons)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        header = QLabel("Settings")
        header.setObjectName("heading")
        layout.addWidget(header)

        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout(theme_group)
        theme_layout.setSpacing(8)

        mode_row = QHBoxLayout()
        mode_row.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Dark", "Light"])
        self.mode_combo.setCurrentText("Dark" if self.theme_manager.dark_mode else "Light")
        self.mode_combo.currentTextChanged.connect(self._on_mode_changed)
        mode_row.addWidget(self.mode_combo)
        mode_row.addStretch()
        theme_layout.addLayout(mode_row)

        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("Color scheme:"))
        self.preset_combo = QComboBox()
        for tid in THEME_NAMES:
            self.preset_combo.addItem(THEMES[tid]["name"], tid)
        idx = self.preset_combo.findData(self.theme_manager.theme_id)
        if idx >= 0:
            self.preset_combo.setCurrentIndex(idx)
        self.preset_combo.currentIndexChanged.connect(self._on_preset_changed)
        preset_row.addWidget(self.preset_combo, 1)
        theme_layout.addLayout(preset_row)

        preview_row = QHBoxLayout()
        preview_row.setSpacing(4)
        for tid in THEME_NAMES:
            seed = THEMES[tid]["seed"]
            swatch = QFrame()
            swatch.setFixedSize(28, 28)
            swatch.setStyleSheet(
                f"background: {seed}; border-radius: 14px; border: 2px solid palette(mid);"
            )
            swatch.setToolTip(THEMES[tid]["name"])
            preview_row.addWidget(swatch)
        preview_row.addStretch()
        theme_layout.addLayout(preview_row)

        layout.addWidget(theme_group)

        dl_group = QGroupBox("Downloads")
        dl_layout = QVBoxLayout(dl_group)
        dl_layout.setSpacing(8)

        folder_row = QHBoxLayout()
        folder_row.addWidget(QLabel("Default folder:"))
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("~/Downloads")
        folder_row.addWidget(self.folder_input, 1)

        self.folder_btn = QPushButton()
        self.folder_btn.setObjectName("icon")
        self.folder_btn.setToolTip("Choose folder")
        self.folder_btn.setFixedSize(40, 40)
        self.folder_btn.clicked.connect(self._pick_folder)
        folder_row.addWidget(self.folder_btn)
        dl_layout.addLayout(folder_row)

        layout.addWidget(dl_group)

        about_group = QGroupBox("About")
        about_layout = QVBoxLayout(about_group)
        about_layout.setSpacing(4)
        about_layout.addWidget(QLabel("DownTube v2.0"))
        about_layout.addWidget(QLabel("yt-dlp GUI for Linux"))
        about_layout.addWidget(QLabel("Design inspired by Seal (Material Design 3)"))
        about_layout.addWidget(QLabel("DownTube - yt-dlp GUI"))
        layout.addWidget(about_group)

        layout.addStretch()

    def _update_icons(self):
        s = self.theme_manager
        self.folder_btn.setIcon(s.icon("folder", 20))
        self.folder_btn.setIconSize(QSize(20, 20))

    def _on_mode_changed(self, mode):
        dark = mode == "Dark"
        self.theme_manager.set_dark(dark)
        self._reapply_theme()

    def _on_preset_changed(self, idx):
        tid = self.preset_combo.itemData(idx)
        if tid:
            self.theme_manager.set_theme(tid)
            self._reapply_theme()

    def _reapply_theme(self):
        app = self.window()
        if app:
            self.theme_manager.apply(app)
            from ui.main_window import MainWindow
            if isinstance(app, MainWindow):
                app._update_nav_icons()

    def _pick_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Default Download Folder")
        if folder:
            self.folder_input.setText(folder)
            s = QSettings("DownTube", "DownTube")
            s.setValue("default_folder", folder)

    def showEvent(self, event):
        super().showEvent(event)
        s = QSettings("DownTube", "DownTube")
        folder = s.value("default_folder", "")
        if folder and not self.folder_input.text():
            self.folder_input.setText(folder)
