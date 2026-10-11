from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QMainWindow, QStackedWidget, QVBoxLayout, QWidget

from . import icons
from . import theme as t
from .add_transaction import AddTransactionScreen
from .dashboard import DashboardScreen
from .login import LoginScreen
from .settings import SettingsScreen
from .widgets import Avatar, HoverFrame, LogoMark, hline, label, logo_pixmap, repolish, set_color

NAV = [
    ("home", "Home", lambda c, a: icons.home(c, filled=a)),
    ("transactions", "Transactions", lambda c, a: icons.transactions(c)),
    ("settings", "Settings", lambda c, a: icons.settings(c)),
]


class NavItem(HoverFrame):
    def __init__(self, key, text, svg_fn):
        super().__init__("nav")
        self.key, self.svg_fn = key, svg_fn
        row = QHBoxLayout(self)
        row.setContentsMargins(14, 11, 14, 11)
        row.setSpacing(12)
        self.icon = QLabel()
        self.icon.setFixedSize(20, 20)
        self.text = label(text, t.DISPLAY, 14, 400, t.SIDEBAR_MUTED)
        self.dot = QLabel()
        self.dot.setFixedSize(5, 5)
        self.dot.setStyleSheet("background: rgba(255,255,255,0.7); border-radius: 2px;")
        row.addWidget(self.icon)
        row.addWidget(self.text)
        row.addStretch()
        row.addWidget(self.dot)
        for w in (self.icon, self.text, self.dot):
            w.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.set_active(False)

    def set_active(self, active):
        color = "#FFFFFF" if active else t.SIDEBAR_MUTED
        self.icon.setPixmap(icons.pixmap(self.svg_fn(color, active), 20))
        self.text.setFont(t.font(t.DISPLAY, 14, 600 if active else 400))
        set_color(self.text, color)
        self.dot.setVisible(active)
        self.setProperty("active", active)
        repolish(self)


class Sidebar(QFrame):
    navigate = Signal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("sidebar")
        self.setFixedWidth(224)
        col = QVBoxLayout(self)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(0)

        brand = QHBoxLayout()
        brand.setContentsMargins(24, 30, 24, 26)
        brand.setSpacing(10)
        brand.addWidget(LogoMark(32, bg="#FFFFFF", fg=t.INK))
        brand.addWidget(label("Visia", t.DISPLAY, 18, 700, "#FFFFFF", -0.02))
        brand.addStretch()
        col.addLayout(brand)
        col.addWidget(hline("sideSep"))

        nav = QVBoxLayout()
        nav.setContentsMargins(12, 16, 12, 16)
        nav.setSpacing(2)
        self.items = {}
        for key, text, fn in NAV:
            item = NavItem(key, text, fn)
            item.clicked.connect(lambda k=key: self.navigate.emit(k))
            nav.addWidget(item)
            self.items[key] = item
        nav.addStretch()
        col.addLayout(nav, 1)

        col.addWidget(hline("sideSep"))
        user = QHBoxLayout()
        user.setContentsMargins(24, 18, 24, 18)
        user.setSpacing(10)
        self.avatar = Avatar(32)
        user.addWidget(self.avatar)
        info = QVBoxLayout()
        info.setSpacing(1)
        self.name = label("", t.DISPLAY, 13, 500, "#E8E8E4")
        info.addWidget(self.name)
        info.addWidget(label("Personal", t.BODY, 11, 400, t.INK2))
        user.addLayout(info, 1)
        col.addLayout(user)

    def set_active(self, key):
        for k, item in self.items.items():
            item.set_active(k == key)

    def set_user(self, user):
        self.avatar.set_user(user)
        self.name.setText(user.full_name)


class AppShell(QWidget):
    logged_out = Signal()

    def __init__(self, db):
        super().__init__()
        self.db = db
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        self.sidebar = Sidebar()
        row.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        self.dashboard = DashboardScreen(db)
        self.add = AddTransactionScreen(db)
        self.settings = SettingsScreen(db)
        self.pages = {"home": self.dashboard, "transactions": self.add, "settings": self.settings}
        for page in self.pages.values():
            self.stack.addWidget(page)
        row.addWidget(self.stack, 1)

        self.sidebar.navigate.connect(self.go)
        self.dashboard.add_requested.connect(lambda: self.go("transactions"))
        self.add.saved.connect(self.dashboard.refresh)
        self.settings.user_changed.connect(self._user_changed)
        self.settings.logout_requested.connect(self.logged_out)
        self.settings.account_deleted.connect(self.logged_out)

    def set_user(self, user):
        self.sidebar.set_user(user)
        for page in self.pages.values():
            page.set_user(user)
        self.go("home")

    def _user_changed(self, user):
        self.sidebar.set_user(user)
        self.dashboard.set_user(user)
        self.add.user = user

    def go(self, key):
        self.sidebar.set_active(key)
        if key == "home":
            self.dashboard.refresh()
        self.stack.setCurrentWidget(self.pages[key])


class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.setWindowTitle("Visia")
        self.setWindowIcon(logo_pixmap(128))
        self.resize(1360, 900)
        self.setMinimumSize(1100, 720)

        self.stack = QStackedWidget()
        self.login = LoginScreen(db)
        self.shell = AppShell(db)
        self.stack.addWidget(self.login)
        self.stack.addWidget(self.shell)
        self.setCentralWidget(self.stack)

        self.login.logged_in.connect(self._enter)
        self.shell.logged_out.connect(self._leave)

    def _enter(self, user):
        self.shell.set_user(user)
        self.stack.setCurrentWidget(self.shell)

    def _leave(self):
        self.login.reset()
        self.stack.setCurrentWidget(self.login)
