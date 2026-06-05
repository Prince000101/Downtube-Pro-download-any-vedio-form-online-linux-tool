import re
import os
import sys
import json
import shutil
from PyQt5.QtCore import QObject, QProcess, pyqtSignal


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class DownloadEngine(QObject):
    progress_changed = pyqtSignal(int)
    speed_changed = pyqtSignal(str)
    eta_changed = pyqtSignal(str)
    size_changed = pyqtSignal(str)
    log_line = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    video_info_ready = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self._on_stdout)
        self.process.readyReadStandardError.connect(self._on_stderr)
        self.process.finished.connect(self._on_finished)
        self.process.errorOccurred.connect(self._on_process_error)
        self._running = False
        self._cancelled = False
        self._progress_pattern = re.compile(
            r"\[download\]\s+(\d+\.\d)%\s+(?:of\s+~?([\d.]+[KMG]?i?B))?\s*(?:at\s+([\d.]+[KMG]?i?B/s))?\s*(?:ETA\s+(\S+))?"
        )
        self._ytdlp_path = None

    @staticmethod
    def _find_ytdlp():
        name = "yt-dlp.exe" if sys.platform == "win32" else "yt-dlp"
        exe_dir = os.path.dirname(os.path.realpath(sys.executable))
        candidates = [
            os.path.join(exe_dir, name),
            resource_path(name),
        ]
        for p in candidates:
            if os.path.exists(p):
                return os.path.realpath(p)
        which = shutil.which(name)
        if which:
            return os.path.realpath(which)
        return resource_path(name)

    @property
    def ytdlp_path(self):
        if self._ytdlp_path:
            return self._ytdlp_path
        return self._find_ytdlp()

    @ytdlp_path.setter
    def ytdlp_path(self, path):
        self._ytdlp_path = path

    def fetch_info(self, url):
        p = QProcess(self)
        args = [
            self.ytdlp_path, "--dump-json", "--no-download", "--quiet",
            "--no-warnings", url
        ]
        p.start(args[0], args[1:])
        p.waitForFinished(30000)
        out = p.readAllStandardOutput().data().decode().strip()
        err = p.readAllStandardError().data().decode().strip()
        if out:
            try:
                info = json.loads(out.split("\n")[0])
                self.video_info_ready.emit(info)
                return info
            except json.JSONDecodeError:
                self.log_line.emit(f"Failed to parse video info: {err}")
        else:
            self.log_line.emit(f"Failed to fetch video info: {err}")
        return None

    def fetch_formats(self, url):
        p = QProcess(self)
        args = [
            self.ytdlp_path, "--dump-json", "--no-download", "--quiet",
            "--no-warnings", url
        ]
        p.start(args[0], args[1:])
        p.waitForFinished(30000)
        out = p.readAllStandardOutput().data().decode().strip()
        if out:
            try:
                info = json.loads(out.split("\n")[0])
                return info.get("formats", [])
            except json.JSONDecodeError:
                pass
        return []

    def fetch_playlist(self, url):
        p = QProcess(self)
        args = [
            self.ytdlp_path, "--dump-json", "--flat-playlist", "--quiet",
            "--no-warnings", url
        ]
        p.start(args[0], args[1:])
        p.waitForFinished(30000)
        out = p.readAllStandardOutput().data().decode().strip()
        entries = []
        if out:
            for line in out.split("\n"):
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        return entries

    def fetch_titles(self, urls):
        p = QProcess(self)
        args = [self.ytdlp_path, "--print", "title", "--ignore-errors", "--no-warnings"] + urls
        p.start(args[0], args[1:])
        p.waitForFinished(60000)
        out = p.readAllStandardOutput().data().decode().strip()
        if not out:
            return []
        return [line.strip() for line in out.split("\n") if line.strip()]

    def search(self, query, limit=10):
        search_url = f"ytsearch{limit}:{query}"
        p = QProcess(self)
        args = [
            self.ytdlp_path, "--dump-json", "--flat-playlist", "--quiet",
            "--no-warnings", search_url
        ]
        p.start(args[0], args[1:])
        p.waitForFinished(30000)
        out = p.readAllStandardOutput().data().decode().strip()
        results = []
        if out:
            for line in out.split("\n"):
                line = line.strip()
                if line:
                    try:
                        results.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        return results

    @staticmethod
    def _find_node():
        path = shutil.which("node")
        if path:
            return os.path.realpath(path)
        nvm_dir = os.path.expanduser("~/.nvm/versions/node")
        if os.path.isdir(nvm_dir):
            for d in sorted(os.listdir(nvm_dir), reverse=True):
                p = os.path.join(nvm_dir, d, "bin", "node")
                if os.path.exists(p):
                    return os.path.realpath(p)
        return None

    def start_download(self, url, output_template, extra_args=None):
        if self._running:
            self.log_line.emit("Already downloading. Queue this instead.")
            return

        self._running = True
        self._cancelled = False

        cmd = [self.ytdlp_path, url, "-o", output_template, "--newline"]

        node_path = self._find_node()
        if node_path:
            cmd.extend(["--js-runtimes", f"node:{node_path}"])
        cmd.extend(["--remote-components", "ejs:github"])

        if extra_args:
            cmd.extend(extra_args)

        cookies = resource_path("cookies.txt")
        if os.path.exists(cookies):
            cmd.extend(["--cookies", cookies])
        else:
            self.log_line.emit("No cookies.txt found — login-protected content may fail.")

        self.log_line.emit(f"Starting: {url}")
        self.log_line.emit(f"Command: {' '.join(cmd)}")
        self.process.start(cmd[0], cmd[1:])
        if not self.process.waitForStarted(5000):
            self._running = False
            self.log_line.emit(f"Failed to start yt-dlp. Binary not found: {cmd[0]}")
            self.finished.emit(False, f"yt-dlp not found at {cmd[0]}")

    def _on_process_error(self, error):
        self._running = False
        msg = self.process.errorString()
        self.log_line.emit(f"[ERROR] Process error: {msg}")
        self.finished.emit(False, f"process error: {msg}")

    def cancel(self):
        if self._running and self.process.state() == QProcess.Running:
            self._cancelled = True
            self.process.kill()
            self.log_line.emit("Cancelled.")

    def is_running(self):
        return self._running

    def _on_stdout(self):
        try:
            data = self.process.readAllStandardOutput().data().decode()
            for line in data.split("\n"):
                line = line.strip()
                if not line:
                    continue
                self.log_line.emit(line)

                m = self._progress_pattern.search(line)
                if m:
                    pct = float(m.group(1))
                    self.progress_changed.emit(int(pct))
                    if m.group(2):
                        self.size_changed.emit(m.group(2))
                    if m.group(3):
                        self.speed_changed.emit(m.group(3))
                    if m.group(4):
                        self.eta_changed.emit(m.group(4))

                if "has already been downloaded" in line:
                    self.progress_changed.emit(100)
        except Exception as e:
            self.log_line.emit(f"[ERROR] stdout handler: {e}")

    def _on_stderr(self):
        try:
            data = self.process.readAllStandardError().data().decode()
            for line in data.split("\n"):
                line = line.strip()
                if not line:
                    continue
                if "sign in" in line.lower() or "cookie" in line.lower():
                    self.log_line.emit(f"[COOKIE] {line}")
                else:
                    self.log_line.emit(line)
        except Exception as e:
            self.log_line.emit(f"[ERROR] stderr handler: {e}")

    def _on_finished(self, exit_code, exit_status):
        self._running = False
        success = exit_code == 0 and not self._cancelled
        msg = "finished" if success else ("cancelled" if self._cancelled else f"failed (exit {exit_code})")
        self.finished.emit(success, msg)
