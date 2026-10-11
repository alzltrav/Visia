from pathlib import Path

from PySide6.QtCore import QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPalette, QPixmap
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QLabel, QLineEdit, QSizePolicy, QWidget

from . import theme as t


def repolish(w):
    w.style().unpolish(w)
    w.style().polish(w)
    w.update()


def label(text="", family=t.BODY, px=14, weight=400, color=t.INK, spacing=None, wrap=False, upper=False):
    lbl = QLabel(text.upper() if upper else text)
    lbl.setFont(t.font(family, px, weight, spacing))
    lbl.setStyleSheet(f"color: {color}; background: transparent;")
    lbl.setWordWrap(wrap)
    return lbl


def set_color(lbl, color):
    lbl.setStyleSheet(f"color: {color}; background: transparent;")


def amount_html(value, symbol_px, cents_px, muted=t.INK2):
    whole, cents = f"{abs(value):,.2f}".split(".")
    sign = "-" if value < 0 else ""
    return (f'{sign}<span style="font-size:{symbol_px}px; color:{muted};">₱</span>{whole}'
            f'<span style="font-size:{cents_px}px; color:{muted};">.{cents}</span>')


def placeholder_color(widget, color=t.FAINT):
    pal = widget.palette()
    pal.setColor(QPalette.ColorRole.PlaceholderText, QColor(color))
    widget.setPalette(pal)


def shadow(widget, blur=16, dy=2, alpha=13):
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur)
    effect.setOffset(0, dy)
    effect.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(effect)


def hline(name="divider"):
    line = QFrame()
    line.setObjectName(name)
    line.setFixedHeight(1)
    return line


class LogoMark(QWidget):
    def __init__(self, size=32, bg=t.INK, fg="#FFFFFF", parent=None):
        super().__init__(parent)
        self._bg, self._fg, self._size = QColor(bg), QColor(fg), size
        self.setFixedSize(size, size)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(self._bg)
        r = self._size * 0.25
        p.drawRoundedRect(QRectF(0, 0, self._size, self._size), r, r)
        p.setPen(self._fg)
        p.setFont(t.font(t.DISPLAY, round(self._size * 0.52), 700, -0.03))
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "V")


def logo_pixmap(size=64):
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    mark = LogoMark(size)
    mark.render(pm)
    return pm


class Avatar(QWidget):
    def __init__(self, size=32, bg="#2A2A28", fg="#C8C8C4", px=12, weight=600, parent=None):
        super().__init__(parent)
        self._size, self._bg, self._fg, self._px, self._weight = size, QColor(bg), QColor(fg), px, weight
        self._initials, self._photo = "", None
        self.setFixedSize(size, size)

    def set_user(self, user):
        self._initials = user.initials if user else ""
        self._photo = None
        if user and user.photo_path and Path(user.photo_path).exists():
            pm = QPixmap(user.photo_path)
            if not pm.isNull():
                self._photo = pm
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        path = QPainterPath()
        path.addEllipse(QRectF(0, 0, self._size, self._size))
        if self._photo:
            p.setClipPath(path)
            scaled = self._photo.scaled(QSize(self._size, self._size) * self.devicePixelRatioF(),
                                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                        Qt.TransformationMode.SmoothTransformation)
            scaled.setDevicePixelRatio(self.devicePixelRatioF())
            sw = scaled.width() / self.devicePixelRatioF()
            sh = scaled.height() / self.devicePixelRatioF()
            p.drawPixmap(QRectF((self._size - sw) / 2, (self._size - sh) / 2, sw, sh), scaled, QRectF(scaled.rect()))
            return
        p.fillPath(path, self._bg)
        p.setPen(self._fg)
        p.setFont(t.font(t.DISPLAY, self._px, self._weight, -0.02))
        p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self._initials)


class HoverFrame(QFrame):
    clicked = Signal()

    def __init__(self, name, clickable=True, parent=None):
        super().__init__(parent)
        self.setObjectName(name)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        if clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._clickable = clickable

    def enterEvent(self, e):
        self.setProperty("hover", True)
        repolish(self)
        super().enterEvent(e)

    def leaveEvent(self, e):
        self.setProperty("hover", False)
        repolish(self)
        super().leaveEvent(e)

    def mouseReleaseEvent(self, e):
        if self._clickable and e.button() == Qt.MouseButton.LeftButton and self.rect().contains(e.position().toPoint()):
            self.clicked.emit()
        super().mouseReleaseEvent(e)


class PrefixLineEdit(QLineEdit):
    def __init__(self, prefix, prefix_font, prefix_color=t.FAINT, parent=None):
        super().__init__(parent)
        self._prefix = QLabel(prefix, self)
        self._prefix.setFont(prefix_font)
        self._prefix.setStyleSheet(f"color: {prefix_color}; background: transparent; border: none;")
        self._prefix.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._prefix.adjustSize()
        self.setObjectName("prefixed")

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._prefix.move(16, (self.height() - self._prefix.height()) // 2)


def expanding(widget):
    widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    return widget
