import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QLabel, QFrame,
    QApplication, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

from theme import ThemeManager
from core.engine import DownloadEngine
from core.queue import DownloadQueue
from core.history import HistoryManager
from core import resource_path
from ui.download_page import DownloadPage
from ui.history_page import HistoryPage
from ui.settings_page import SettingsPage


PAGES = [
    ("download", "download", "Downloads", "Download videos & audio"),
    ("history", "history", "History", "View download history"),
    ("settings", "settings", "Settings", "Configure preferences"),
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DownTube")
        self.setMinimumSize(800, 600)
        self.resize(960, 700)

        icon_path = resource_path("icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.theme_manager = ThemeManager()
        self.engine = DownloadEngine(self)
        self.queue = DownloadQueue(self)
        self.history = HistoryManager()

        self._setup_ui()

        self.theme_manager.apply(QApplication.instance())
        self._update_nav_icons()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.nav_bar = QFrame()
        self.nav_bar.setObjectName("navBar")
        self.nav_bar.setFixedWidth(72)
        nav_layout = QVBoxLayout(self.nav_bar)
        nav_layout.setContentsMargins(8, 20, 8, 12)
        nav_layout.setSpacing(4)

        self.nav_buttons = []
        for page_id, icon_name, label, tooltip in PAGES:
            btn = QPushButton()
            btn.setObjectName("nav")
            btn.setCheckable(True)
            btn.setFixedHeight(48)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setToolTip(f"<b>{label}</b><br>{tooltip}")
            btn.setProperty("page_id", page_id)
            btn.setProperty("icon_name", icon_name)
            btn.clicked.connect(lambda checked, pid=page_id: self._switch_page(pid))
            nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        nav_layout.addStretch()

        version_label = QLabel("v2")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("font-size: 10px; color: palette(mid); padding: 6px 0;")
        nav_layout.addWidget(version_label)

        main_layout.addWidget(self.nav_bar)

        self.stack = QStackedWidget()
        self.download_page = DownloadPage(self.engine, self.queue, self.history, self.theme_manager)
        self.history_page = HistoryPage(self.history)
        self.settings_page = SettingsPage(self.theme_manager)

        self.stack.addWidget(self.download_page)
        self.stack.addWidget(self.history_page)
        self.stack.addWidget(self.settings_page)

        main_layout.addWidget(self.stack, 1)

        if self.nav_buttons:
            self.nav_buttons[0].setChecked(True)

    def _switch_page(self, page_id):
        for btn in self.nav_buttons:
            btn.setChecked(btn.property("page_id") == page_id)
        idx = next(i for i, (pid, _, _, _) in enumerate(PAGES) if pid == page_id)
        self.stack.setCurrentIndex(idx)

    def _update_nav_icons(self):
        for btn in self.nav_buttons:
            icon_name = btn.property("icon_name")
            if icon_name:
                ico = self.theme_manager.icon(icon_name, 22)
                btn.setIcon(ico)
                btn.setIconSize(QSize(22, 22))
