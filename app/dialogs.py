from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout

from . import theme as t
from .widgets import label, placeholder_color


class FormDialog(QDialog):
    def __init__(self, parent, title, subtitle, fields, confirm="Save", danger=False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(420)
        self._validator = None
        self.inputs = {}

        col = QVBoxLayout(self)
        col.setContentsMargins(32, 30, 32, 28)
        col.setSpacing(0)
        col.addWidget(label(title, t.DISPLAY, 20, 700, t.INK, -0.02))
        if subtitle:
            col.addSpacing(6)
            col.addWidget(label(subtitle, t.BODY, 13, 400, t.MUTED, wrap=True))
        col.addSpacing(22)

        for key, caption, placeholder, value, secret in fields:
            col.addWidget(label(caption, t.BODY, 11, 600, "#777773", 0.07, upper=True))
            col.addSpacing(8)
            edit = QLineEdit(value)
            edit.setPlaceholderText(placeholder)
            edit.setFont(t.font(t.BODY, 14))
            placeholder_color(edit)
            if secret:
                edit.setEchoMode(QLineEdit.EchoMode.Password)
            edit.returnPressed.connect(self._accept)
            edit.textChanged.connect(lambda: self.error.hide())
            self.inputs[key] = edit
            col.addWidget(edit)
            col.addSpacing(16)

        self.error = label("", t.BODY, 13, 500, t.EXPENSE, wrap=True)
        self.error.hide()
        col.addWidget(self.error)
        col.addSpacing(8)

        row = QHBoxLayout()
        row.setSpacing(10)
        row.addStretch()
        cancel = QPushButton("Cancel")
        cancel.setObjectName("ghost")
        cancel.setFont(t.font(t.BODY, 13))
        cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel.clicked.connect(self.reject)
        ok = QPushButton(confirm)
        ok.setObjectName("danger" if danger else "primary")
        ok.setFont(t.font(t.BODY, 13, 600))
        ok.setCursor(Qt.CursorShape.PointingHandCursor)
        if not danger:
            ok.setProperty("size", "sm")
        ok.clicked.connect(self._accept)
        row.addWidget(cancel)
        row.addWidget(ok)
        col.addLayout(row)

        if self.inputs:
            next(iter(self.inputs.values())).setFocus()

    def on_submit(self, fn):
        self._validator = fn
        return self

    def values(self):
        return {k: w.text() for k, w in self.inputs.items()}

    def _accept(self):
        if self._validator:
            message = self._validator(self.values())
            if message:
                self.error.setText(message)
                self.error.show()
                return
        self.accept()


def info(parent, title, message):
    dlg = QDialog(parent)
    dlg.setWindowTitle(title)
    dlg.setModal(True)
    dlg.setMinimumWidth(400)
    col = QVBoxLayout(dlg)
    col.setContentsMargins(32, 30, 32, 28)
    col.setSpacing(0)
    col.addWidget(label(title, t.DISPLAY, 20, 700, t.INK, -0.02))
    col.addSpacing(10)
    col.addWidget(label(message, t.BODY, 14, 400, t.INK2, wrap=True))
    col.addSpacing(24)
    row = QHBoxLayout()
    row.addStretch()
    ok = QPushButton("Got it")
    ok.setObjectName("primary")
    ok.setFont(t.font(t.BODY, 13, 600))
    ok.setProperty("size", "sm")
    ok.setCursor(Qt.CursorShape.PointingHandCursor)
    ok.clicked.connect(dlg.accept)
    row.addWidget(ok)
    col.addLayout(row)
    dlg.exec()
