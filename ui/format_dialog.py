from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt


class FormatDialog(QDialog):
    def __init__(self, formats, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Format")
        self.setMinimumSize(600, 400)
        self.selected_format = None
        self.formats = formats
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Choose a format to download")
        title.setObjectName("heading")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Extension", "Resolution", "Codec", "Filesize", "Note", ""
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)

        self.populate_table()

        layout.addWidget(self.table)

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

        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.table.cellDoubleClicked.connect(self.accept_selection)

    def populate_table(self):
        best = None
        best_audio = None
        for i, fmt in enumerate(self.formats):
            ext = fmt.get("ext", "")
            resolution = fmt.get("resolution", "")
            if not resolution:
                w = fmt.get("width")
                h = fmt.get("height")
                if w and h:
                    resolution = f"{w}x{h}"
                else:
                    resolution = "audio only"
            codec = fmt.get("vcodec", "none")
            if codec == "none":
                codec = fmt.get("acodec", "none")
            filesize = fmt.get("filesize") or fmt.get("filesize_approx", 0)
            filesize_str = self._format_size(filesize) if filesize else "~"
            note = fmt.get("format_note", "")
            fmt_id = fmt.get("format_id", "")
            # Determine if video format
            is_video = fmt.get("vcodec") and fmt.get("vcodec") != "none"
            is_audio = fmt.get("acodec") and fmt.get("acodec") != "none" and (not fmt.get("vcodec") or fmt.get("vcodec") == "none")

            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(fmt_id))
            self.table.setItem(row, 1, QTableWidgetItem(ext))
            self.table.setItem(row, 2, QTableWidgetItem(resolution))
            self.table.setItem(row, 3, QTableWidgetItem(codec))
            self.table.setItem(row, 4, QTableWidgetItem(filesize_str))
            self.table.setItem(row, 5, QTableWidgetItem(note))
            self.table.setItem(row, 6, QTableWidgetItem("✓" if is_video else "" if is_audio else ""))

            self.table.setRowHeight(row, 36)

            if is_video:
                best = fmt
            elif is_audio and not best_audio:
                best_audio = fmt

        if self.table.rowCount() > 0:
            self.table.selectRow(0)

    def _on_selection_changed(self):
        self.download_btn.setEnabled(len(self.table.selectedItems()) > 0)

    def accept_selection(self):
        row = self.table.currentRow()
        if row >= 0:
            fmt_id = self.table.item(row, 0).text()
            for fmt in self.formats:
                if fmt.get("format_id") == fmt_id:
                    self.selected_format = fmt
                    break
            self.accept()

    @staticmethod
    def _format_size(n):
        for unit in ("B", "KB", "MB", "GB"):
            if n < 1024:
                return f"{n:.1f}{unit}"
            n /= 1024
        return f"{n:.1f}TB"
