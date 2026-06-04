from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QPainterPath

_ICON_CACHE = {}


def _make_icon(draw_fn, color, size):
    key = (draw_fn.__name__, color, size)
    if key in _ICON_CACHE:
        return _ICON_CACHE[key]
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setViewport(0, 0, size, size)
    painter.setWindow(0, 0, 24, 24)
    c = QColor(color)
    draw_fn(painter, 24, c)
    painter.end()
    icon = QIcon(pixmap)
    _ICON_CACHE[key] = icon
    return icon


def _p(w, color):
    pen = QPen(color, w)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    return pen


def _draw_download(p, s, c):
    p.setPen(_p(2.5, c))
    p.setBrush(Qt.NoBrush)
    path = QPainterPath()
    path.moveTo(12, 3); path.lineTo(12, 18)
    path.moveTo(5, 11); path.lineTo(12, 18); path.lineTo(19, 11)
    path.moveTo(4, 21); path.lineTo(20, 21)
    p.drawPath(path)


def _draw_history(p, s, c):
    p.setPen(_p(2, c))
    p.setBrush(Qt.NoBrush)
    p.drawEllipse(QPointF(12, 12), 9, 9)
    path = QPainterPath()
    path.moveTo(12, 6); path.lineTo(12, 13); path.lineTo(17, 16)
    p.drawPath(path)
    p.setBrush(c); p.setPen(Qt.NoPen)
    p.drawEllipse(QPointF(12, 12), 1.5, 1.5)


def _draw_settings(p, s, c):
    p.setPen(_p(2, c))
    p.setBrush(Qt.NoBrush)
    center = 12; ri = 6.5; ro = 9.5
    import math
    path = QPainterPath()
    for i in range(8):
        a = math.radians(i * 45 - 22.5)
        x1 = center + ri * math.cos(a)
        y1 = center + ri * math.sin(a)
        x2 = center + ro * math.cos(a)
        y2 = center + ro * math.sin(a)
        if i == 0: path.moveTo(x1, y1)
        else: path.lineTo(x1, y1)
        path.lineTo(x2, y2)
        a2 = math.radians(i * 45 + 22.5)
        x3 = center + ro * math.cos(a2)
        y3 = center + ro * math.sin(a2)
        path.lineTo(x3, y3)
    path.closeSubpath()
    p.drawPath(path)
    p.drawEllipse(QPointF(center, center), ri - 1.5, ri - 1.5)


def _draw_search(p, s, c):
    p.setPen(_p(2.5, c))
    p.setBrush(Qt.NoBrush)
    p.drawEllipse(QPointF(9, 9), 6, 6)
    p.drawLine(QPointF(13.5, 13.5), QPointF(21, 21))


def _draw_folder(p, s, c):
    p.setPen(_p(2.2, c))
    p.setBrush(Qt.NoBrush)
    path = QPainterPath()
    path.moveTo(3, 9); path.lineTo(3, 20); path.lineTo(21, 20)
    path.lineTo(21, 9); path.lineTo(13, 9); path.lineTo(10, 6)
    path.lineTo(3, 6); path.closeSubpath()
    p.drawPath(path)


def _draw_close(p, s, c):
    p.setPen(_p(2.5, c))
    p.setBrush(Qt.NoBrush)
    p.drawLine(QPointF(5, 5), QPointF(19, 19))
    p.drawLine(QPointF(19, 5), QPointF(5, 19))


def _draw_clear(p, s, c):
    p.setPen(_p(2, c))
    p.setBrush(Qt.NoBrush)
    path = QPainterPath()
    path.moveTo(9, 4); path.lineTo(9, 2); path.lineTo(15, 2)
    path.lineTo(15, 4); path.moveTo(4, 4); path.lineTo(20, 4)
    path.moveTo(6, 4); path.lineTo(7, 21); path.lineTo(17, 21); path.lineTo(18, 4)
    p.drawPath(path)
    p.drawLine(QPointF(10, 8), QPointF(10, 18))
    p.drawLine(QPointF(14, 8), QPointF(14, 18))


def _draw_retry(p, s, c):
    p.setPen(_p(2.3, c))
    p.setBrush(Qt.NoBrush)
    path = QPainterPath()
    path.arcMoveTo(3, 3, 18, 18, 45)
    path.arcTo(3, 3, 18, 18, 45, 270)
    p.drawPath(path)
    ax = 3 + 9 * 0.707; ay = 3 + 9 * 0.707
    p.drawLine(QPointF(ax + 4, ay - 2), QPointF(ax, ay))
    p.drawLine(QPointF(ax - 2, ay + 4), QPointF(ax, ay))


def _draw_check(p, s, c):
    p.setPen(_p(3, c))
    p.setBrush(Qt.NoBrush)
    path = QPainterPath()
    path.moveTo(4, 13); path.lineTo(10, 19); path.lineTo(20, 5)
    p.drawPath(path)


def _draw_music(p, s, c):
    p.setPen(_p(1.8, c))
    p.setBrush(Qt.NoBrush)
    p.drawLine(QPointF(15, 4), QPointF(15, 17))
    p.setBrush(c); p.setPen(Qt.NoPen)
    flag = QPainterPath()
    flag.moveTo(15, 4); flag.lineTo(7, 9); flag.lineTo(15, 14); flag.closeSubpath()
    p.drawPath(flag)
    p.drawEllipse(QPointF(15, 19), 3.5, 3.5)


def _draw_play(p, s, c):
    p.setPen(Qt.NoPen); p.setBrush(c)
    path = QPainterPath()
    path.moveTo(7, 4); path.lineTo(7, 20); path.lineTo(19, 12); path.closeSubpath()
    p.drawPath(path)


def _draw_pause(p, s, c):
    p.setBrush(c); p.setPen(Qt.NoPen)
    p.drawRect(7, 4, 3, 16); p.drawRect(14, 4, 3, 16)


def _draw_queue(p, s, c):
    p.setPen(_p(2, c))
    p.setBrush(Qt.NoBrush)
    for y in (7, 12, 17):
        p.drawLine(QPointF(3, y), QPointF(14, y))
    p.drawLine(QPointF(18, 8), QPointF(18, 16))
    p.drawLine(QPointF(14, 12), QPointF(22, 12))


def _draw_arrow_down(p, s, c):
    p.setPen(_p(2.5, c))
    p.setBrush(Qt.NoBrush)
    path = QPainterPath()
    path.moveTo(12, 2); path.lineTo(12, 18)
    path.moveTo(5, 11); path.lineTo(12, 18); path.lineTo(19, 11)
    p.drawPath(path)


DRAW_FUNCS = {
    "download": _draw_download, "history": _draw_history,
    "settings": _draw_settings, "search": _draw_search,
    "folder": _draw_folder, "close": _draw_close,
    "clear": _draw_clear, "retry": _draw_retry,
    "play": _draw_play, "check": _draw_check,
    "music": _draw_music, "video": _draw_play,
    "arrow_down": _draw_arrow_down, "pause": _draw_pause,
    "queue": _draw_queue,
}


def icon(name, color="#1C1B1F", size=24):
    draw_fn = DRAW_FUNCS.get(name)
    if draw_fn is None:
        return QIcon()
    return _make_icon(draw_fn, color, size)
