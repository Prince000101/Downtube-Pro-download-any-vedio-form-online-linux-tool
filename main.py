import sys
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

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
        traceback.print_exc()
        QMessageBox.critical(
            None, "DownTube - Error",
            f"DownTube encountered an error and could not start:\n\n{traceback.format_exc()}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
