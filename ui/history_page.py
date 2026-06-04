import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QAbstractItemView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from ui.widgets import format_duration


STATUS_COLORS = {
    "completed": "#4CAF50",
    "error": "#F44336",
    "cancelled": "#FF9800",
}


class HistoryPage(QWidget):
    def __init__(self, history, parent=None):
        super().__init__(parent)
        self.setObjectName("historyPage")
        self.history = history
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        header = QLabel("Download History")
        header.setObjectName("heading")
        layout.addWidget(header)

        filter_layout = QHBoxLayout()
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Completed", "Error", "Cancelled"])
        self.filter_combo.currentTextChanged.connect(self._reload)
        filter_layout.addWidget(QLabel("Filter:"))
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addStretch()

        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.setObjectName("secondary")
        self.clear_btn.clicked.connect(self._clear_history)
        filter_layout.addWidget(self.clear_btn)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setObjectName("secondary")
        self.refresh_btn.clicked.connect(self._reload)
        filter_layout.addWidget(self.refresh_btn)
        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Title", "URL", "Format", "Status", "Date", ""
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table, 1)

        self._reload()

    def _reload(self):
        self.table.setRowCount(0)
        filter_text = self.filter_combo.currentText().lower()
        entries = self.history.get_all()

        for entry in entries:
            if filter_text != "all" and entry["status"] != filter_text:
                continue

            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 40)

            title = entry.get("title", "Unknown")
            self.table.setItem(row, 0, QTableWidgetItem(title[:80]))
            self.table.setItem(row, 1, QTableWidgetItem(entry.get("url", "")))

            fmt = entry.get("format_id", "") or entry.get("format_note", "") or "-"
            self.table.setItem(row, 2, QTableWidgetItem(fmt))

            status = entry.get("status", "unknown")
            status_item = QTableWidgetItem(status)
            color = STATUS_COLORS.get(status, "#888888")
            status_item.setForeground(QColor(color))
            self.table.setItem(row, 3, status_item)

            ct = entry.get("completed_time", 0)
            date_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(ct)) if ct else "-"
            self.table.setItem(row, 4, QTableWidgetItem(date_str))

    def _clear_history(self):
        self.history.clear()
        self._reload()
