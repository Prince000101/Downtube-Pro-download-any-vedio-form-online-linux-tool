from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QListWidget, QListWidgetItem, QWidget
)
from PyQt5.QtCore import Qt, QTimer


class SearchDialog(QDialog):
    def __init__(self, search_fn, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Search YouTube")
        self.setMinimumSize(500, 400)
        self.search_fn = search_fn
        self.results = []
        self.selected_url = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Search")
        title.setObjectName("heading")
        layout.addWidget(title)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search YouTube...")
        self.search_input.returnPressed.connect(self.do_search)
        search_layout.addWidget(self.search_input)

        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.do_search)
        search_layout.addWidget(self.search_btn)
        layout.addLayout(search_layout)

        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.accept_selection)
        layout.addWidget(self.results_list, 1)

        btn_layout = QHBoxLayout()
        self.download_btn = QPushButton("Download Selected")
        self.download_btn.clicked.connect(self.accept_selection)
        self.download_btn.setEnabled(False)
        btn_layout.addStretch()
        btn_layout.addWidget(self.download_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setObjectName("secondary")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.results_list.itemSelectionChanged.connect(
            lambda: self.download_btn.setEnabled(len(self.results_list.selectedItems()) > 0)
        )

    def do_search(self):
        query = self.search_input.text().strip()
        if not query:
            return
        self.search_btn.setEnabled(False)
        self.search_btn.setText("Searching...")
        self.results_list.clear()

        results = self.search_fn(query)
        self.results = results

        for r in results:
            title = r.get("title", "Unknown")
            uploader = r.get("uploader", r.get("channel", ""))
            duration = r.get("duration", 0)
            url = r.get("url") or r.get("webpage_url", "")
            m, s = divmod(int(duration), 60)
            h, m = divmod(m, 60)
            dur_str = f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

            text = f"{title}\n👤 {uploader}  ⏱ {dur_str}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, url)
            item.setData(Qt.UserRole + 1, title)
            item.setData(Qt.UserRole + 2, r.get("thumbnail", ""))
            item.setData(Qt.UserRole + 3, uploader)
            item.setData(Qt.UserRole + 4, duration)
            self.results_list.addItem(item)

        self.search_btn.setEnabled(True)
        self.search_btn.setText("Search")

    def accept_selection(self):
        items = self.results_list.selectedItems()
        if items:
            item = items[0]
            self.selected_url = item.data(Qt.UserRole)
            self.selected_title = item.data(Qt.UserRole + 1)
            self.selected_thumbnail = item.data(Qt.UserRole + 2)
            self.selected_uploader = item.data(Qt.UserRole + 3)
            self.selected_duration = item.data(Qt.UserRole + 4)
            self.accept()
