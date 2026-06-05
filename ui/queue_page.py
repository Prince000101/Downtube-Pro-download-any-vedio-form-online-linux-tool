from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QStyledItemDelegate, QMenu, QMessageBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QFont

from core.queue import (
    DownloadItem, STATUS_QUEUED, STATUS_DOWNLOADING,
    STATUS_COMPLETED, STATUS_ERROR, STATUS_CANCELLED
)

STATUS_ICONS = {
    STATUS_QUEUED: "⏳",
    STATUS_DOWNLOADING: "⬇️",
    STATUS_COMPLETED: "✅",
    STATUS_ERROR: "❌",
    STATUS_CANCELLED: "⛔",
}
STATUS_ORDER = {
    STATUS_DOWNLOADING: 0,
    STATUS_QUEUED: 1,
    STATUS_COMPLETED: 2,
    STATUS_ERROR: 3,
    STATUS_CANCELLED: 4,
}


class ProgressDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        value = index.data(Qt.DisplayRole)
        if not value:
            return
        try:
            pct = int(value.rstrip("%"))
        except (ValueError, AttributeError):
            return
        if pct <= 0:
            return
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        rect = option.rect.adjusted(6, 5, -6, -5)
        bar_w = int(rect.width() * min(pct, 100) / 100)
        bg = option.palette.color(option.palette.Window).darker(135)
        painter.setPen(Qt.NoPen)
        painter.setBrush(bg)
        painter.drawRoundedRect(rect, 3, 3)
        if bar_w > 0:
            color = QColor("#43A047") if pct >= 100 else option.palette.color(option.palette.Highlight)
            painter.setBrush(color)
            painter.drawRoundedRect(rect.adjusted(0, 0, -(rect.width() - bar_w), 0), 3, 3)
        painter.setPen(option.palette.color(option.palette.Text))
        f = QFont(option.font)
        f.setPointSize(f.pointSize() - 1)
        painter.setFont(f)
        painter.drawText(option.rect, Qt.AlignCenter, f"{pct}%")
        painter.restore()


class QueuePage(QWidget):
    COLUMNS = ["", "Name", "Quality", "Type", "Size", "Progress", "Speed", "ETA"]

    def __init__(self, engine, queue, theme_manager, start_download_fn=None, parent=None):
        super().__init__(parent)
        self.setObjectName("queuePage")
        self.engine = engine
        self.queue = queue
        self.theme_manager = theme_manager
        self._start_download_fn = start_download_fn
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        heading = QLabel("Queue")
        heading.setObjectName("heading")
        layout.addWidget(heading)

        toolbar = QHBoxLayout()
        self.clear_completed_btn = QPushButton("Clear Completed")
        self.clear_completed_btn.setObjectName("secondary")
        self.clear_completed_btn.clicked.connect(self._clear_completed)
        toolbar.addWidget(self.clear_completed_btn)

        self.clear_all_btn = QPushButton("Clear All")
        self.clear_all_btn.setObjectName("secondary")
        self.clear_all_btn.clicked.connect(self._clear_all)
        toolbar.addWidget(self.clear_all_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels(self.COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._context_menu)

        self.table.setColumnWidth(0, 32)
        self.table.setColumnWidth(2, 90)
        self.table.setColumnWidth(3, 50)
        self.table.setColumnWidth(4, 75)
        self.table.setColumnWidth(5, 110)
        self.table.setColumnWidth(6, 85)
        self.table.setColumnWidth(7, 70)

        self.table.setItemDelegateForColumn(5, ProgressDelegate(self.table))

        layout.addWidget(self.table, 1)

    def connect_signals(self):
        self.queue.item_added.connect(lambda _: self._rebuild_all())
        self.queue.item_removed.connect(lambda _: self._rebuild_all())
        self.queue.item_changed.connect(self._on_item_changed)

    def _on_item_changed(self, index):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.data(Qt.UserRole) == index:
                self._update_row(row, index)
                return

    def _rebuild_all(self):
        self.table.setRowCount(0)
        indices = sorted(
            range(len(self.queue.items)),
            key=lambda i: STATUS_ORDER.get(self.queue.items[i].status, 99)
        )
        for idx in indices:
            self._insert_row(idx)

    def _insert_row(self, idx):
        item = self.queue.get(idx)
        if item is None:
            return
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setRowHeight(row, 40)
        self._fill_row(row, idx, item)

    def _fill_row(self, row, idx, item):
        status = QTableWidgetItem(STATUS_ICONS.get(item.status, ""))
        status.setTextAlignment(Qt.AlignCenter)
        status.setData(Qt.UserRole, idx)
        self.table.setItem(row, 0, status)

        name = QTableWidgetItem(item.title)
        name.setToolTip(item.title)
        self.table.setItem(row, 1, name)

        quality = item.format_note or item.format_id or "-"
        q = QTableWidgetItem(quality)
        q.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 2, q)

        dtype = QTableWidgetItem(item.download_type.upper())
        dtype.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 3, dtype)

        size_val = item.total_size or ("" if item.status != STATUS_ERROR else "-")
        s = QTableWidgetItem(size_val)
        s.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table.setItem(row, 4, s)

        prog = QTableWidgetItem(f"{item.progress}%")
        prog.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 5, prog)

        speed = QTableWidgetItem(item.speed or "-")
        speed.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 6, speed)

        eta = QTableWidgetItem(item.eta or "-")
        eta.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, 7, eta)

    def _update_row(self, row, idx):
        item = self.queue.get(idx)
        if item is None:
            return
        self._fill_row(row, idx, item)

    def _context_menu(self, pos):
        row = self.table.rowAt(pos.y())
        if row < 0:
            return
        idx = self.table.item(row, 0).data(Qt.UserRole)
        item = self.queue.get(idx)
        if item is None:
            return
        menu = QMenu(self)
        if item.status in (STATUS_DOWNLOADING, STATUS_QUEUED):
            act_cancel = menu.addAction("Cancel")
        else:
            act_cancel = None
        if item.status in (STATUS_ERROR, STATUS_CANCELLED):
            act_retry = menu.addAction("Retry")
        else:
            act_retry = None
        act_remove = menu.addAction("Remove")
        act = menu.exec_(self.table.viewport().mapToGlobal(pos))
        if act == act_cancel:
            self._cancel(idx)
        elif act == act_retry:
            self._retry(idx)
        elif act == act_remove:
            self._remove(idx)

    def _cancel(self, idx):
        cur = self.queue.current
        if cur and self.queue.current_index == idx:
            self.engine.cancel()
        else:
            self.queue.update_item(idx, status=STATUS_CANCELLED)

    def _retry(self, idx):
        item = self.queue.get(idx)
        if item:
            self.queue.update_item(idx, status=STATUS_QUEUED, progress=0, error_msg="")
            if not self.engine.is_running() and self._start_download_fn:
                self._start_download_fn()

    def _remove(self, idx):
        item = self.queue.get(idx)
        if item and item.status == STATUS_DOWNLOADING:
            self.engine.cancel()
        self.queue.remove(idx)

    def _clear_completed(self):
        for i in range(len(self.queue.items) - 1, -1, -1):
            item = self.queue.items[i]
            if item.status in (STATUS_COMPLETED, STATUS_ERROR, STATUS_CANCELLED):
                self.queue.remove(i)

    def _clear_all(self):
        self.engine.cancel()
        self.queue.clear()
