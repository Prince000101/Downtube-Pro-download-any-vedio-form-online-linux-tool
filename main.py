import sys
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox


def _log_crash(exc_type, exc_value, exc_tb):
    msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    with open("/tmp/downtube_crash.log", "w") as f:
        f.write(msg)
    print(msg, file=sys.stderr)


sys.excepthook = _log_crash

from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("DownTube")
    app.setOrganizationName("DownTube")

    try:
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception:
        _log_crash(*sys.exc_info())
        QMessageBox.critical(
            None, "DownTube - Error",
            f"DownTube encountered an error:\n\n{traceback.format_exc()}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
