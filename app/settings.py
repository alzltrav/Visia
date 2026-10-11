import re
from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QFileDialog, QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from . import icons
from . import theme as t
from .db import DATA_DIR, AuthError
from .dialogs import FormDialog
from .widgets import Avatar, HoverFrame, hline, label

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def time_ago(iso):
    then = datetime.fromisoformat(iso)
    days = (datetime.now() - then).days
    if days < 1:
        return "today"
    if days < 30:
        return f"{days} day{'s' if days != 1 else ''} ago"
    months = days // 30
    if months < 12:
        return f"{months} month{'s' if months != 1 else ''} ago"
    years = days // 365
    return f"{years} year{'s' if years != 1 else ''} ago"


class OptionRow(HoverFrame):
    def __init__(self, svg, title, danger=False):
        super().__init__("option")
        self.setProperty("danger", danger)
        row = QHBoxLayout(self)
        row.setContentsMargins(24, 20, 24, 20)
        row.setSpacing(16)

        box = QLabel()
        box.setFixedSize(40, 40)
        box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box.setPixmap(icons.pixmap(svg, 18))
        box.setStyleSheet(f"background: {t.EXPENSE_BG if danger else t.CHIP}; border-radius: 8px; border: none;")
        row.addWidget(box)

        text = QVBoxLayout()
        text.setSpacing(3)
        text.addWidget(label(title, t.DISPLAY, 15, 600, t.EXPENSE if danger else t.INK))
        self.desc = label("", t.BODY, 12, 400, t.INK3)
        text.addWidget(self.desc)
        row.addLayout(text, 1)

        chev = QLabel()
        chev.setPixmap(icons.pixmap(icons.chevron_right(), 16))
        chev.setStyleSheet("background: transparent; border: none;")
        row.addWidget(chev)

        for child in self.findChildren(QLabel):
            child.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)


class SettingsScreen(QScrollArea):
    logout_requested = Signal()
    user_changed = Signal(object)
    account_deleted = Signal()

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.user = None
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        page = QWidget()
        page.setObjectName("page")
        self.setWidget(page)
        col = QVBoxLayout(page)
        col.setContentsMargins(48, 40, 48, 40)
        col.setSpacing(0)
        col.addWidget(label("Settings", t.DISPLAY, 28, 700, t.INK, -0.025))
        col.addSpacing(6)
        col.addWidget(label("Manage your account and preferences.", t.BODY, 14, 400, t.MUTED))
        col.addSpacing(40)

        grid = QHBoxLayout()
        grid.setSpacing(28)
        grid.addWidget(self._profile_card(), 0, Qt.AlignmentFlag.AlignTop)
        grid.addLayout(self._options(), 1)
        col.addLayout(grid)
        col.addStretch()

    def _profile_card(self):
        card = QFrame()
        card.setObjectName("card")
        card.setFixedWidth(250)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(24, 36, 24, 28)
        lay.setSpacing(0)

        self.avatar = Avatar(88, bg=t.INK, fg="#FFFFFF", px=30, weight=700)
        lay.addWidget(self.avatar, 0, Qt.AlignmentFlag.AlignHCenter)
        lay.addSpacing(16)
        self.name = label("", t.DISPLAY, 17, 700, t.INK)
        self.name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name.setWordWrap(True)
        lay.addWidget(self.name)
        lay.addSpacing(4)
        self.handle = label("", t.BODY, 13, 400, t.INK3)
        self.handle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.handle)
        lay.addSpacing(22)

        upload = QPushButton("Upload Photo")
        upload.setObjectName("secondary")
        upload.setFont(t.font(t.BODY, 12, 500))
        upload.setCursor(Qt.CursorShape.PointingHandCursor)
        upload.clicked.connect(self._upload_photo)
        lay.addWidget(upload)
        lay.addSpacing(24)
        lay.addWidget(hline())
        lay.addSpacing(22)
        lay.addWidget(label("Member Since", t.BODY, 10, 600, t.FAINT, 0.07, upper=True))
        lay.addSpacing(8)
        self.since = label("", t.MONO, 13, 400, "#666662")
        lay.addWidget(self.since)
        return card

    def _options(self):
        lay = QVBoxLayout()
        lay.setSpacing(10)

        self.email_row = OptionRow(icons.email(), "Change Email")
        self.email_row.clicked.connect(self._change_email)
        self.password_row = OptionRow(icons.lock(), "Change Password")
        self.password_row.clicked.connect(self._change_password)
        self.delete_row = OptionRow(icons.trash(), "Delete Account", danger=True)
        self.delete_row.desc.setText("Permanently remove your account")
        self.delete_row.clicked.connect(lambda: self.confirm.setVisible(not self.confirm.isVisible()))
        for r in (self.email_row, self.password_row, self.delete_row):
            lay.addWidget(r)

        self.confirm = QFrame()
        self.confirm.setObjectName("confirm")
        cl = QVBoxLayout(self.confirm)
        cl.setContentsMargins(24, 20, 24, 20)
        cl.setSpacing(16)
        msg = label("Are you sure? This action cannot be undone. All your data will be permanently deleted.",
                    t.BODY, 14, 500, t.EXPENSE, wrap=True)
        cl.addWidget(msg)
        btns = QHBoxLayout()
        btns.setSpacing(10)
        cancel = QPushButton("Cancel")
        cancel.setObjectName("ghost")
        cancel.setFont(t.font(t.BODY, 13))
        cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel.clicked.connect(lambda: self.confirm.hide())
        really = QPushButton("Yes, Delete Account")
        really.setObjectName("danger")
        really.setFont(t.font(t.BODY, 13, 600))
        really.setCursor(Qt.CursorShape.PointingHandCursor)
        really.clicked.connect(self._delete_account)
        btns.addWidget(cancel)
        btns.addWidget(really)
        btns.addStretch()
        cl.addLayout(btns)
        self.confirm.hide()
        lay.addWidget(self.confirm)

        lay.addSpacing(6)
        out = QPushButton("  Logout")
        out.setObjectName("logout")
        out.setFont(t.font(t.DISPLAY, 15, 600, -0.01))
        out.setIcon(icons.icon(icons.logout(), 18))
        out.setCursor(Qt.CursorShape.PointingHandCursor)
        out.clicked.connect(self.logout_requested)
        lay.addWidget(out)
        lay.addStretch()
        return lay

    def set_user(self, user):
        self.user = user
        self.confirm.hide()
        self.avatar.set_user(user)
        self.name.setText(user.full_name)
        self.handle.setText(f"@{user.username}")
        self.since.setText(datetime.fromisoformat(user.created_at).strftime("%b %Y"))
        self.email_row.desc.setText(user.email or "No email added yet")
        self.password_row.desc.setText(f"Last changed {time_ago(user.password_changed_at)}")

    def _reload(self):
        self.user = self.db.get_user(self.user.id)
        self.set_user(self.user)
        self.user_changed.emit(self.user)

    def _change_email(self):
        dlg = FormDialog(self, "Change Email", "We'll use this to identify your account.",
                         [("email", "Email address", "you@example.com", self.user.email, False)])
        dlg.on_submit(lambda v: None if EMAIL_RE.match(v["email"].strip()) else "Enter a valid email address.")
        if dlg.exec():
            self.db.update_email(self.user.id, dlg.values()["email"])
            self._reload()

    def _change_password(self):
        dlg = FormDialog(self, "Change Password", "Use at least 6 characters.", [
            ("current", "Current password", "Enter current password", "", True),
            ("new", "New password", "Enter new password", "", True),
            ("confirm", "Confirm new password", "Re-enter new password", "", True),
        ])

        def validate(v):
            if v["new"] != v["confirm"]:
                return "New passwords don't match."
            try:
                self.db.change_password(self.user.id, v["current"], v["new"])
            except AuthError as e:
                return str(e)
            return None

        dlg.on_submit(validate)
        if dlg.exec():
            self._reload()

    def _upload_photo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Choose a profile photo", "",
                                              "Images (*.png *.jpg *.jpeg *.bmp *.webp)")
        if not path:
            return
        img = QImage(path)
        if img.isNull():
            return
        side = min(img.width(), img.height())
        img = img.copy((img.width() - side) // 2, (img.height() - side) // 2, side, side)
        img = img.scaled(256, 256, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
        folder = DATA_DIR / "avatars"
        folder.mkdir(parents=True, exist_ok=True)
        dest = folder / f"user-{self.user.id}.png"
        img.save(str(dest), "PNG")
        self.db.update_photo(self.user.id, str(dest))
        self._reload()

    def _delete_account(self):
        self.db.delete_user(self.user.id)
        self.confirm.hide()
        self.account_deleted.emit()
