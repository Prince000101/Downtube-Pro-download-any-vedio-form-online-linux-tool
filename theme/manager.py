import os
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QPalette, QColor, QIcon

from .colors import get_palette, THEMES, THEME_NAMES, DEFAULT_THEME
from .icons import icon as make_icon


QSS_TEMPLATE = """
QWidget {
    font-family: "Segoe UI", "Ubuntu", "Noto Sans", sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: %(background)s;
}

QLabel {
    color: %(on_surface)s;
    background: transparent;
    border: none;
    padding: 2px 0;
}
QLabel#heading {
    font-size: 22px;
    font-weight: 700;
    color: %(on_surface)s;
    padding: 8px 0;
}
QLabel#subheading {
    font-size: 14px;
    font-weight: 600;
    color: %(on_surface_variant)s;
    padding: 4px 0;
}
QLabel#caption {
    font-size: 11px;
    color: %(on_surface_variant)s;
}

QLineEdit {
    background-color: %(surface_container)s;
    color: %(on_surface)s;
    border: 1px solid %(outline)s;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    selection-background-color: %(primary)s;
    selection-color: %(on_primary)s;
}
QLineEdit:focus {
    border: 2px solid %(primary)s;
    padding: 7px 11px;
}
QLineEdit:disabled {
    background-color: %(surface)s;
    color: %(on_surface_variant)s;
    border-color: %(outline_variant)s;
}

QPushButton {
    background-color: %(primary)s;
    color: %(on_primary)s;
    border: none;
    border-radius: 20px;
    padding: 8px 24px;
    font-size: 13px;
    font-weight: 600;
    min-height: 36px;
}
QPushButton:hover {
    background-color: %(primary_hover)s;
}
QPushButton:pressed {
    background-color: %(primary_pressed)s;
}
QPushButton:disabled {
    background-color: %(surface_container)s;
    color: %(on_surface_variant)s;
}

QPushButton#secondary {
    background-color: transparent;
    color: %(primary)s;
    border: 1px solid %(outline)s;
    border-radius: 20px;
    padding: 8px 20px;
    font-size: 13px;
    min-height: 36px;
}
QPushButton#secondary:hover {
    background-color: %(primary_container)s;
}
QPushButton#secondary:pressed {
    background-color: %(surface_container_high)s;
}

QPushButton#text {
    background-color: transparent;
    color: %(primary)s;
    border: none;
    padding: 8px 12px;
}
QPushButton#text:hover {
    background-color: %(primary_container)s;
    border-radius: 20px;
}

QPushButton#nav {
    background-color: transparent;
    color: %(on_surface_variant)s;
    border: none;
    border-left: 3px solid transparent;
    border-radius: 0px;
    padding: 0px;
    font-size: 10px;
    min-height: 48px;
    max-height: 48px;
}
QPushButton#nav:hover {
    background-color: %(surface_container)s;
}
QPushButton#nav:checked {
    background-color: %(primary_container)s;
    border-left: 3px solid %(primary)s;
    color: %(primary)s;
}
QPushButton#nav:pressed {
    background-color: %(primary)s;
    color: %(on_primary)s;
}

QPushButton#icon {
    background-color: transparent;
    color: %(on_surface_variant)s;
    border: none;
    border-radius: 20px;
    padding: 0px;
    font-size: 13px;
}
QPushButton#icon:hover {
    background-color: %(surface_container_high)s;
}
QPushButton#icon:pressed {
    background-color: %(surface_variant)s;
}
QPushButton#icon:hover {
    background-color: %(surface_container)s;
}
QPushButton#icon:pressed {
    background-color: %(surface_container_high)s;
}

QComboBox {
    background-color: %(surface_container)s;
    color: %(on_surface)s;
    border: 1px solid %(outline)s;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 13px;
    min-width: 120px;
}
QComboBox:hover {
    border: 1px solid %(primary)s;
}
QComboBox::drop-down {
    border: none;
    width: 30px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid %(on_surface)s;
    margin-right: 8px;
}
QComboBox QAbstractItemView {
    background-color: %(surface)s;
    color: %(on_surface)s;
    border: 1px solid %(outline_variant)s;
    border-radius: 8px;
    selection-background-color: %(primary_container)s;
    selection-color: %(on_primary_container)s;
    padding: 4px;
    outline: none;
}

QCheckBox {
    color: %(on_surface)s;
    spacing: 8px;
    font-size: 13px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid %(on_surface_variant)s;
    border-radius: 4px;
    background: transparent;
}
QCheckBox::indicator:checked {
    background-color: %(primary)s;
    border-color: %(primary)s;
}
QCheckBox::indicator:hover {
    border-color: %(primary)s;
}

QProgressBar {
    background-color: %(surface_container)s;
    border: none;
    border-radius: 4px;
    text-align: center;
    height: 8px;
    font-size: 10px;
    color: transparent;
}
QProgressBar::chunk {
    background-color: %(primary)s;
    border-radius: 4px;
}

QTextEdit, QPlainTextEdit {
    background-color: %(surface_container)s;
    color: %(on_surface)s;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 8px;
    font-family: "Consolas", "Ubuntu Mono", "Noto Sans Mono", monospace;
    font-size: 12px;
    selection-background-color: %(primary)s;
    selection-color: %(on_primary)s;
}

QListWidget {
    background-color: transparent;
    border: none;
    outline: none;
    padding: 4px;
}
QListWidget::item {
    background-color: %(surface)s;
    border: 1px solid %(outline_variant)s;
    border-radius: 12px;
    padding: 0px;
    margin: 4px 0px;
}
QListWidget::item:selected {
    background-color: %(primary_container)s;
    border-color: %(primary)s;
}
QListWidget::item:hover {
    background-color: %(surface_container)s;
}

QTableWidget {
    background-color: %(surface)s;
    color: %(on_surface)s;
    border: 1px solid %(outline_variant)s;
    border-radius: 8px;
    gridline-color: %(outline_variant)s;
    selection-background-color: %(primary_container)s;
    selection-color: %(on_primary_container)s;
}
QTableWidget::item {
    padding: 6px 8px;
}
QHeaderView::section {
    background-color: %(surface_container)s;
    color: %(on_surface)s;
    border: none;
    border-bottom: 1px solid %(outline_variant)s;
    padding: 8px;
    font-weight: 600;
}

QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: %(outline_variant)s;
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: %(outline)s;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background: transparent;
    height: 6px;
}
QScrollBar::handle:horizontal {
    background: %(outline_variant)s;
    border-radius: 3px;
    min-width: 30px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}

QTabWidget::pane {
    background: transparent;
    border: none;
}
QTabBar::tab {
    background: transparent;
    color: %(on_surface_variant)s;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 500;
    min-width: 80px;
}
QTabBar::tab:selected {
    color: %(primary)s;
    border-bottom: 2px solid %(primary)s;
}
QTabBar::tab:hover {
    color: %(on_surface)s;
}

QGroupBox {
    color: %(on_surface)s;
    font-weight: 600;
    font-size: 13px;
    border: 1px solid %(outline_variant)s;
    border-radius: 12px;
    margin-top: 12px;
    padding: 16px 16px 12px;
    padding-top: 20px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    padding: 0 8px;
    color: %(primary)s;
}

QDialog {
    background-color: %(surface)s;
}

QToolTip {
    background-color: %(inverse_surface)s;
    color: %(inverse_on_surface)s;
    border: none;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
}

QSplitter::handle {
    background-color: %(outline_variant)s;
    height: 1px;
}

QFrame#navBar {
    background-color: %(surface)s;
    border-right: 1px solid %(outline_variant)s;
}

QFrame#videoCard {
    background-color: %(surface)s;
    border: 1px solid %(outline_variant)s;
    border-radius: 12px;
}

QFrame#previewWidget {
    background-color: %(surface_container)s;
    border: 1px solid %(outline_variant)s;
    border-radius: 12px;
}
"""


class ThemeManager:
    def __init__(self):
        self.settings = QSettings("DownTube", "DownTube")
        self.theme_id = self.settings.value("theme_id", DEFAULT_THEME)
        self.dark_mode = self.settings.value("theme_mode", "dark") == "dark"
        self._current_set = None

    def set_theme(self, theme_id):
        if theme_id in THEMES:
            self.theme_id = theme_id
            self.settings.setValue("theme_id", theme_id)

    def set_dark(self, dark: bool):
        self.dark_mode = dark
        self.settings.setValue("theme_mode", "dark" if dark else "light")

    def get_palette(self):
        return get_palette(self.theme_id, self.dark_mode)

    def get_colors(self):
        p = self.get_palette()
        d = p.to_dict()
        from .colors import THEMES
        seed = THEMES.get(self.theme_id, {}).get("seed", "#1565C0")
        d["primary_hover"] = self._adjust(seed, 1.15) if self.dark_mode else self._adjust(seed, 0.85)
        d["primary_pressed"] = self._adjust(seed, 1.3) if self.dark_mode else self._adjust(seed, 0.7)
        d["surface_container"] = d.get("surface_container", self._adjust(d["surface"], 1.05 if self.dark_mode else 0.95))
        d["surface_container_high"] = d.get("surface_container_high", self._adjust(d["surface"], 1.1 if self.dark_mode else 0.9))
        d["primary_container"] = d.get("primary_container", self._adjust(d["primary"], 1.4))
        if self.dark_mode:
            d["on_primary"] = d.get("on_primary", "#003258")
            if d.get("primary_hover") == d["primary"]:
                d["primary_hover"] = self._adjust(d["primary"], 0.85)
        return d

    def generate_qss(self):
        return QSS_TEMPLATE % self.get_colors()

    def apply(self, app_or_widget):
        colors = self.get_colors()
        qss = QSS_TEMPLATE % colors
        app_or_widget.setStyleSheet(qss)

        if self.dark_mode:
            palette = QPalette()
            bg = QColor(colors["background"])
            surface = QColor(colors["surface"])
            on_surface = QColor(colors["on_surface"])
            primary = QColor(colors["primary"])
            palette.setColor(QPalette.Window, bg)
            palette.setColor(QPalette.WindowText, on_surface)
            palette.setColor(QPalette.Base, surface)
            palette.setColor(QPalette.AlternateBase, QColor(colors["surface_container"]))
            palette.setColor(QPalette.Text, on_surface)
            palette.setColor(QPalette.Button, QColor(colors["surface_container"]))
            palette.setColor(QPalette.ButtonText, on_surface)
            palette.setColor(QPalette.Highlight, primary)
            palette.setColor(QPalette.HighlightedText, QColor(colors["on_primary"]))
            palette.setColor(QPalette.ToolTipBase, QColor(colors["inverse_surface"]))
            palette.setColor(QPalette.ToolTipText, QColor(colors["inverse_on_surface"]))
            palette.setColor(QPalette.Link, primary)
            app_or_widget.setPalette(palette)
        else:
            app_or_widget.setPalette(QApplication.style().standardPalette())

        self._current_set = colors

    def icon(self, name, size=24):
        colors = self._current_set or self.get_colors()
        return make_icon(name, colors.get("on_surface", "#1C1B1F"), size)

    @staticmethod
    def _adjust(hex_color, factor):
        c = QColor(hex_color)
        h = c.hueF()
        s = c.saturationF()
        l = c.lightnessF()
        new_l = max(0.0, min(1.0, l * factor))
        if h < 0:
            h = 0
        c2 = QColor.fromHslF(h, s, new_l)
        return c2.name()
