from PySide6.QtCore import Qt, Signal
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLineEdit, QPushButton, QSizePolicy, QVBoxLayout, QWidget

from . import icons
from . import theme as t
from .db import AuthError
from .dialogs import info
from .widgets import LogoMark, label, placeholder_color, set_color


def centered(inner, max_width):
    inner.setMaximumWidth(max_width)
    inner.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
    wrap = QHBoxLayout()
    wrap.setContentsMargins(0, 0, 0, 0)
    wrap.addStretch(1)
    wrap.addWidget(inner, 100)
    wrap.addStretch(1)
    return wrap


class LoginScreen(QWidget):
    logged_in = Signal(object)

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.sign_up = False
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._left(), 1)
        root.addWidget(self._right(), 1)
        self._apply_mode()

    def _left(self):
        panel = QFrame()
        panel.setObjectName("loginLeft")
        outer = QVBoxLayout(panel)
        outer.setContentsMargins(72, 64, 72, 64)
        outer.addStretch(1)

        inner = QWidget()
        col = QVBoxLayout(inner)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(0)

        brand = QHBoxLayout()
        brand.setSpacing(12)
        brand.addWidget(LogoMark(40))
        brand.addWidget(label("Visia", t.DISPLAY, 24, 700, t.INK, -0.03))
        brand.addStretch()
        col.addLayout(brand)
        col.addSpacing(60)

        heading = label("", t.DISPLAY, 40, 700, t.INK, -0.035)
        heading.setTextFormat(Qt.TextFormat.RichText)
        heading.setText('<p style="line-height:44px; margin:0;">Track every<br>peso with<br>clarity.</p>')
        col.addWidget(heading)
        col.addSpacing(16)

        sub = label("", t.BODY, 15, 400, t.MUTED)
        sub.setText('<p style="line-height:25px; margin:0;">Simple, clear expense tracking<br>built for everyday Filipino life.</p>')
        col.addWidget(sub)
        col.addSpacing(52)

        art = QSvgWidget()
        art.load(icons.ILLUSTRATION.encode())
        art.setFixedSize(300, 230)
        art.setStyleSheet("background: transparent;")
        col.addWidget(art)

        outer.addLayout(centered(inner, 400))
        outer.addStretch(1)
        return panel

    def _right(self):
        panel = QFrame()
        panel.setObjectName("loginRight")
        outer = QVBoxLayout(panel)
        outer.setContentsMargins(72, 64, 72, 64)
        outer.addStretch(1)

        inner = QWidget()
        col = QVBoxLayout(inner)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(0)

        self.title = label("", t.DISPLAY, 30, 700, t.INK, -0.025)
        self.subtitle = label("", t.BODY, 14, 400, t.MUTED)
        col.addWidget(self.title)
        col.addSpacing(8)
        col.addWidget(self.subtitle)
        col.addSpacing(36)

        self.name_block, self.name_input = self._field("Full name", "Enter your full name")
        self.user_block, self.user_input = self._field("Username", "Enter your username")
        self.pass_block, self.pass_input = self._field("Password", "Enter your password", password=True)
        for block in (self.name_block, self.user_block, self.pass_block):
            col.addWidget(block)
            col.addSpacing(18)

        self.error = label("", t.BODY, 13, 500, t.EXPENSE, wrap=True)
        self.error.setContentsMargins(0, 0, 0, 10)
        self.error.hide()
        col.addWidget(self.error)

        col.addSpacing(4)
        self.submit = QPushButton()
        self.submit.setObjectName("primary")
        self.submit.setFont(t.font(t.DISPLAY, 15, 600, -0.01))
        self.submit.setCursor(Qt.CursorShape.PointingHandCursor)
        self.submit.clicked.connect(self._submit)
        col.addWidget(self.submit)
        col.addSpacing(28)

        self.forgot = QPushButton("Forgot Password?")
        self.forgot.setObjectName("link")
        self.forgot.setFont(t.font(t.BODY, 13))
        self.forgot.setCursor(Qt.CursorShape.PointingHandCursor)
        self.forgot.clicked.connect(self._forgot)
        col.addWidget(self.forgot, 0, Qt.AlignmentFlag.AlignHCenter)
        col.addSpacing(14)

        switch_row = QHBoxLayout()
        switch_row.setSpacing(4)
        self.switch_prompt = label("", t.BODY, 13, 400, "#666662")
        self.switch_btn = QPushButton()
        self.switch_btn.setObjectName("linkStrong")
        self.switch_btn.setFont(t.font(t.BODY, 13, 600))
        self.switch_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.switch_btn.clicked.connect(self._toggle_mode)
        switch_row.addStretch()
        switch_row.addWidget(self.switch_prompt)
        switch_row.addWidget(self.switch_btn)
        switch_row.addStretch()
        col.addLayout(switch_row)

        for w in (self.name_input, self.user_input, self.pass_input):
            w.returnPressed.connect(self._submit)

        outer.addLayout(centered(inner, 380))
        outer.addStretch(1)
        return panel

    def _field(self, caption, placeholder, password=False):
        block = QWidget()
        lay = QVBoxLayout(block)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)
        lay.addWidget(label(caption, t.BODY, 13, 500, t.LABEL))
        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setFont(t.font(t.BODY, 14))
        placeholder_color(edit)
        if password:
            edit.setEchoMode(QLineEdit.EchoMode.Password)
        edit.textChanged.connect(self._clear_error)
        lay.addWidget(edit)
        return block, edit

    def _apply_mode(self):
        s = self.sign_up
        self.title.setText("Create account" if s else "Welcome back")
        self.subtitle.setText("Start tracking your finances today." if s else "Sign in to your account to continue.")
        self.submit.setText("Create Account" if s else "Login")
        self.switch_prompt.setText("Already have an account?" if s else "Don't Have an Account?")
        self.switch_btn.setText("Login" if s else "Sign Up")
        self.name_block.setVisible(s)
        self.forgot.setVisible(not s)
        self._clear_error()

    def _toggle_mode(self):
        self.sign_up = not self.sign_up
        self._apply_mode()
        (self.name_input if self.sign_up else self.user_input).setFocus()

    def _clear_error(self):
        self.error.hide()

    def _show_error(self, message):
        self.error.setText(message)
        set_color(self.error, t.EXPENSE)
        self.error.show()

    def _submit(self):
        try:
            if self.sign_up:
                user = self.db.create_user(self.user_input.text(), self.pass_input.text(), self.name_input.text())
            else:
                user = self.db.authenticate(self.user_input.text(), self.pass_input.text())
        except AuthError as e:
            self._show_error(str(e))
            return
        self.reset()
        self.logged_in.emit(user)

    def _forgot(self):
        info(self, "Forgot password",
             "Visia keeps your data on this computer only, so there's no email reset yet.\n\n"
             "If you can't remember your password, create a new account.")

    def reset(self):
        for w in (self.name_input, self.user_input, self.pass_input):
            w.clear()
        if self.sign_up:
            self.sign_up = False
        self._apply_mode()
        self.user_input.setFocus()
