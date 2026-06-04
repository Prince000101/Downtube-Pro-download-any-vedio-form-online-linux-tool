import sqlite3
import os
import sys
import time
from PyQt5.QtCore import QObject


DB_NAME = "downtube_history.db"


def _default_db_path():
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    else:
        base = os.environ.get("XDG_DATA_HOME", os.path.join(os.path.expanduser("~"), ".local", "share"))
    app_dir = os.path.join(base, "DownTube")
    os.makedirs(app_dir, exist_ok=True)
    return os.path.join(app_dir, DB_NAME)


class HistoryManager(QObject):
    def __init__(self, db_path=None, parent=None):
        super().__init__(parent)
        self.db_path = db_path or _default_db_path()
        self._conn = None
        self._init_db()

    def _connect(self):
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _init_db(self):
        conn = self._connect()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT,
                thumbnail TEXT,
                duration INTEGER,
                uploader TEXT,
                format_id TEXT,
                format_note TEXT,
                file_path TEXT,
                status TEXT DEFAULT 'completed',
                added_time REAL,
                completed_time REAL
            )
        """)
        conn.commit()

    def add_entry(self, url, title=None, thumbnail=None, duration=None,
                  uploader=None, format_id=None, format_note=None,
                  file_path=None, status="completed"):
        conn = self._connect()
        now = time.time()
        conn.execute("""
            INSERT INTO history (url, title, thumbnail, duration, uploader,
                                 format_id, format_note, file_path, status,
                                 added_time, completed_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (url, title, thumbnail, duration, uploader, format_id,
              format_note, file_path, status, now, now))
        conn.commit()

    def get_history(self, limit=100, offset=0, status=None):
        conn = self._connect()
        if status:
            cur = conn.execute(
                "SELECT * FROM history WHERE status = ? ORDER BY completed_time DESC LIMIT ? OFFSET ?",
                (status, limit, offset)
            )
        else:
            cur = conn.execute(
                "SELECT * FROM history ORDER BY completed_time DESC LIMIT ? OFFSET ?",
                (limit, offset)
            )
        return [dict(r) for r in cur.fetchall()]

    def get_all(self):
        conn = self._connect()
        cur = conn.execute("SELECT * FROM history ORDER BY completed_time DESC")
        return [dict(r) for r in cur.fetchall()]

    def clear(self):
        conn = self._connect()
        conn.execute("DELETE FROM history")
        conn.commit()

    def delete_entry(self, entry_id):
        conn = self._connect()
        conn.execute("DELETE FROM history WHERE id = ?", (entry_id,))
        conn.commit()

    def count(self, status=None):
        conn = self._connect()
        if status:
            cur = conn.execute("SELECT COUNT(*) FROM history WHERE status = ?", (status,))
        else:
            cur = conn.execute("SELECT COUNT(*) FROM history")
        return cur.fetchone()[0]
