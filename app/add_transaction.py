from PySide6.QtCore import QDate, Qt, QTimer, Signal
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import (QComboBox, QDateEdit, QFrame, QHBoxLayout, QLineEdit, QPushButton, QScrollArea,
                               QVBoxLayout, QWidget)

from . import theme as t
from .widgets import PrefixLineEdit, label, placeholder_color, repolish, set_color, shadow


def field_label(text, optional=False):
    lbl = label("", t.BODY, 11, 600, "#777773", 0.07)
    lbl.setTextFormat(Qt.TextFormat.RichText)
    extra = (f'<span style="font-weight:400; color:{t.FAINT}; letter-spacing:0px; text-transform:none;">'
             f' (optional)</span>') if optional else ""
    lbl.setText(text.upper() + extra)
    return lbl


class AddTransactionScreen(QScrollArea):
    saved = Signal()

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.user = None
        self.kind = "expense"
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        page = QWidget()
        page.setObjectName("page")
        self.setWidget(page)
        outer = QVBoxLayout(page)
        outer.setContentsMargins(48, 40, 48, 40)
        outer.addStretch(1)

        inner = QWidget()
        inner.setMaximumWidth(520)
        col = QVBoxLayout(inner)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(0)
        col.addWidget(label("Add Transaction", t.DISPLAY, 28, 700, t.INK, -0.025))
        col.addSpacing(6)
        col.addWidget(label("Record a new income or expense entry.", t.BODY, 14, 400, t.MUTED))
        col.addSpacing(32)

        card = QFrame()
        card.setObjectName("card")
        shadow(card)
        form = QVBoxLayout(card)
        form.setContentsMargins(40, 36, 40, 36)
        form.setSpacing(0)

        toggle = QFrame()
        toggle.setObjectName("toggle")
        tl = QHBoxLayout(toggle)
        tl.setContentsMargins(4, 4, 4, 4)
        tl.setSpacing(0)
        self.seg = {}
        for kind, text in (("expense", "↓  Expense"), ("income", "↑  Income")):
            b = QPushButton(text)
            b.setObjectName("seg")
            b.setFont(t.font(t.DISPLAY, 14, 600, -0.01))
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda _=False, k=kind: self.set_kind(k))
            tl.addWidget(b, 1)
            self.seg[kind] = b
        form.addWidget(toggle)
        form.addSpacing(32)

        form.addWidget(field_label("Amount"))
        form.addSpacing(10)
        self.amount = PrefixLineEdit("₱", t.font(t.MONO, 22))
        self.amount.setPlaceholderText("0.00")
        self.amount.setFont(t.font(t.MONO, 22, 500))
        validator = QDoubleValidator(0.0, 1e9, 2, self.amount)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.amount.setValidator(validator)
        placeholder_color(self.amount)
        self.amount.textChanged.connect(self._clear_error)
        form.addWidget(self.amount)
        form.addSpacing(22)

        form.addWidget(field_label("Category"))
        form.addSpacing(10)
        self.category = QComboBox()
        self.category.setFont(t.font(t.BODY, 14))
        self.category.addItems(t.CATEGORIES)
        self.category.setPlaceholderText("Select a category")
        self.category.setCurrentIndex(-1)
        self.category.setCursor(Qt.CursorShape.PointingHandCursor)
        self.category.view().setFont(t.font(t.BODY, 14))
        placeholder_color(self.category)
        self.category.currentIndexChanged.connect(self._clear_error)
        self.category.currentIndexChanged.connect(self._mark_category)
        form.addWidget(self.category)
        form.addSpacing(22)

        form.addWidget(field_label("Date"))
        form.addSpacing(10)
        self.date = QDateEdit()
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat("MM/dd/yyyy")
        self.date.setFont(t.font(t.MONO, 14))
        self.date.setCursor(Qt.CursorShape.PointingHandCursor)
        self.date.setMaximumDate(QDate.currentDate().addYears(1))
        self.date.calendarWidget().setFont(t.font(t.BODY, 13))
        self.date.calendarWidget().setVerticalHeaderFormat(self.date.calendarWidget().VerticalHeaderFormat.NoVerticalHeader)
        form.addWidget(self.date)
        form.addSpacing(22)

        form.addWidget(field_label("Note", optional=True))
        form.addSpacing(10)
        self.note = QLineEdit()
        self.note.setPlaceholderText("Add a short description...")
        self.note.setFont(t.font(t.BODY, 14))
        self.note.setMaxLength(80)
        placeholder_color(self.note)
        self.note.returnPressed.connect(self._save)
        form.addWidget(self.note)

        form.addSpacing(16)
        self.error = label("", t.BODY, 13, 500, t.EXPENSE)
        self.error.hide()
        form.addWidget(self.error)
        form.addSpacing(14)

        self.save_btn = QPushButton("Save Entry")
        self.save_btn.setObjectName("primary")
        self.save_btn.setFont(t.font(t.DISPLAY, 15, 600, -0.01))
        self.save_btn.setProperty("size", "lg")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.clicked.connect(self._save)
        form.addWidget(self.save_btn)

        col.addWidget(card)

        center = QHBoxLayout()
        center.addStretch(1)
        center.addWidget(inner, 100)
        center.addStretch(1)
        outer.addLayout(center)
        outer.addStretch(1)

        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._unsave)
        self.reset()

    def set_user(self, user):
        self.user = user
        self.reset()

    def set_kind(self, kind):
        self.kind = kind
        for k, b in self.seg.items():
            b.setProperty("active", k if k == kind else "")
            repolish(b)

    def reset(self):
        self.set_kind("expense")
        self.amount.clear()
        self.category.setCurrentIndex(-1)
        self._mark_category(-1)
        self.note.clear()
        self.date.setDate(QDate.currentDate())
        self._clear_error()

    def _mark_category(self, index):
        self.category.setProperty("empty", index < 0)
        repolish(self.category)

    def _clear_error(self, *_):
        self.error.hide()
        self.amount.setProperty("error", False)
        repolish(self.amount)

    def _fail(self, message, widget=None):
        self.error.setText(message)
        set_color(self.error, t.EXPENSE)
        self.error.show()
        if widget is self.amount:
            self.amount.setProperty("error", True)
            repolish(self.amount)
        if widget:
            widget.setFocus()

    def _save(self):
        try:
            value = float(self.amount.text().replace(",", ""))
        except ValueError:
            value = 0
        if value <= 0:
            self._fail("Enter an amount greater than zero.", self.amount)
            return
        if self.category.currentIndex() < 0:
            self._fail("Choose a category.", self.category)
            return
        self.db.add_transaction(self.user.id, self.kind, value, self.category.currentText(),
                                self.date.date().toString("yyyy-MM-dd"), self.note.text())
        kind = self.kind
        self.amount.clear()
        self.category.setCurrentIndex(-1)
        self.note.clear()
        self.set_kind(kind)
        self.save_btn.setText("✓  Entry Saved")
        self.save_btn.setProperty("saved", True)
        repolish(self.save_btn)
        self._timer.start(2200)
        self.saved.emit()

    def _unsave(self):
        self.save_btn.setText("Save Entry")
        self.save_btn.setProperty("saved", False)
        repolish(self.save_btn)
