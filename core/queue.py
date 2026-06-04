import time
from PyQt5.QtCore import QObject, pyqtSignal


STATUS_QUEUED = "queued"
STATUS_DOWNLOADING = "downloading"
STATUS_PAUSED = "paused"
STATUS_COMPLETED = "completed"
STATUS_ERROR = "error"
STATUS_CANCELLED = "cancelled"


class DownloadItem:
    def __init__(self, url, title=None, thumbnail=None, duration=None,
                 uploader=None, format_id=None, output_template=None,
                 extra_args=None, playlist_title=None, playlist_index=None):
        self.url = url
        self.title = title or url
        self.thumbnail = thumbnail
        self.duration = duration
        self.uploader = uploader
        self.format_id = format_id
        self.output_template = output_template
        self.extra_args = extra_args or []
        self.playlist_title = playlist_title
        self.playlist_index = playlist_index

        self.status = STATUS_QUEUED
        self.progress = 0
        self.speed = ""
        self.eta = ""
        self.error_msg = ""
        self.file_path = ""
        self.added_time = time.time()
        self.completed_time = None

    def to_dict(self):
        return {
            "url": self.url,
            "title": self.title,
            "thumbnail": self.thumbnail,
            "duration": self.duration,
            "uploader": self.uploader,
            "format_id": self.format_id,
            "status": self.status,
            "progress": self.progress,
            "file_path": self.file_path,
            "added_time": self.added_time,
            "completed_time": self.completed_time,
        }


class DownloadQueue(QObject):
    item_added = pyqtSignal(int)
    item_removed = pyqtSignal(int)
    item_changed = pyqtSignal(int)
    current_changed = pyqtSignal(object)
    all_completed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items = []
        self._current_index = -1

    @property
    def items(self):
        return list(self._items)

    @property
    def current(self):
        if 0 <= self._current_index < len(self._items):
            return self._items[self._current_index]
        return None

    @property
    def current_index(self):
        return self._current_index

    @property
    def count(self):
        return len(self._items)

    def add(self, item):
        self._items.append(item)
        idx = len(self._items) - 1
        self.item_added.emit(idx)
        return idx

    def add_multiple(self, items):
        for item in items:
            self.add(item)

    def remove(self, index):
        if 0 <= index < len(self._items):
            was_current = index == self._current_index
            self._items.pop(index)
            self.item_removed.emit(index)
            if was_current:
                self._current_index = -1
                self.current_changed.emit(None)
            elif index < self._current_index:
                self._current_index -= 1

    def clear(self):
        self._items.clear()
        self._current_index = -1
        self.current_changed.emit(None)

    def get(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def set_current(self, index):
        old = self.current
        if old and old.status == STATUS_DOWNLOADING:
            old.status = STATUS_QUEUED
            old.progress = 0
        self._current_index = index
        if self.current:
            self.current.status = STATUS_DOWNLOADING
        self.current_changed.emit(self.current)

    def next(self):
        if self._current_index < len(self._items) - 1:
            self.set_current(self._current_index + 1)
            return self.current
        self._current_index = -1
        self.current_changed.emit(None)
        self.all_completed.emit()
        return None

    def update_item(self, index, **kwargs):
        if 0 <= index < len(self._items):
            item = self._items[index]
            for k, v in kwargs.items():
                setattr(item, k, v)
            self.item_changed.emit(index)

    def remove_completed(self):
        self._items = [i for i in self._items if i.status not in (STATUS_COMPLETED, STATUS_CANCELLED, STATUS_ERROR)]

    def has_pending(self):
        return any(i.status in (STATUS_QUEUED, STATUS_DOWNLOADING, STATUS_PAUSED) for i in self._items)
