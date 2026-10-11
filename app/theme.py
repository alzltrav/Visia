from pathlib import Path

from PySide6.QtGui import QFont, QFontDatabase

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ICONS = ASSETS / "icons"

INK = "#111110"
INK2 = "#555552"
INK3 = "#999995"
MUTED = "#888884"
FAINT = "#AAAAA6"
LABEL = "#444442"
BORDER = "#E2E2DE"
DIVIDER = "#F2F2EE"
BG = "#F6F6F4"
FIELD = "#F9F9F7"
CHIP = "#F4F4F0"
HOVER = "#FAFAF8"
LOGIN_LEFT = "#ECEAE7"
INCOME = "#1A7A4A"
INCOME_BG = "#EDF7F2"
INCOME_BORDER = "#C2E4D0"
EXPENSE = "#B83232"
EXPENSE_BG = "#FDF0F0"
EXPENSE_BORDER = "#ECCECE"
SIDEBAR = "#111110"
SIDEBAR_MUTED = "#777773"

DISPLAY = "DM Sans"
BODY = "Inter"
MONO = "DM Mono"

CATEGORIES = [
    "Food & Dining", "Transport", "Shopping", "Housing", "Utilities", "Healthcare",
    "Entertainment", "Salary", "Freelance", "Investment", "Other",
]

CATEGORY_ICONS = {
    "Food & Dining": "🍔", "Transport": "🚗", "Shopping": "🛒", "Housing": "🏠",
    "Utilities": "⚡", "Healthcare": "💊", "Entertainment": "🎬", "Salary": "💼",
    "Freelance": "💻", "Investment": "📈", "Other": "📱",
}


_FONT_FILES = {
    DISPLAY: {400: "DMSans-Regular", 500: "DMSans-Medium", 600: "DMSans-SemiBold", 700: "DMSans-Bold"},
    BODY: {400: "Inter-Regular", 500: "Inter-Medium", 600: "Inter-SemiBold"},
    MONO: {400: "DMMono-Regular", 500: "DMMono-Medium"},
}
_REGISTERED = {}


def load_fonts():
    for family, weights in _FONT_FILES.items():
        for weight, stem in weights.items():
            font_id = QFontDatabase.addApplicationFont(str(ASSETS / "fonts" / f"{stem}.ttf"))
            names = QFontDatabase.applicationFontFamilies(font_id) if font_id >= 0 else []
            if names:
                _REGISTERED[(family, weight)] = names[0]


def _resolve(family, weight):
    weights = _FONT_FILES.get(family)
    if not weights:
        return family
    nearest = min(weights, key=lambda w: abs(w - weight))
    return _REGISTERED.get((family, nearest), family)


def font(family=BODY, px=14, weight=400, spacing=None):
    f = QFont(_resolve(family, weight))
    f.setPixelSize(px)
    f.setWeight(QFont.Weight(weight))
    if spacing is not None:
        f.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, spacing * px)
    f.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
    return f


def peso(amount, signed=False):
    text = f"₱{abs(amount):,.2f}"
    if signed:
        return ("-" if amount < 0 else "+") + text
    return ("-" if amount < 0 else "") + text


STYLESHEET = f"""
QWidget {{ color: {INK}; }}
QMainWindow, QStackedWidget {{ background: {BG}; }}
QToolTip {{ background: {INK}; color: white; border: none; padding: 6px 8px; }}

QScrollArea, QScrollArea > QWidget > QWidget {{ background: transparent; border: none; }}
QScrollBar:vertical {{ background: transparent; width: 8px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: #D0D0CC; border-radius: 2px; min-height: 30px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ height: 0; background: none; }}

QLineEdit, QComboBox, QDateEdit {{
    border: 1.5px solid {BORDER}; border-radius: 8px; background: {FIELD};
    color: {INK}; padding: 12px 16px; selection-background-color: {INK};
}}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QComboBox:on {{ border-color: {INK}; }}
QLineEdit[error="true"] {{ border-color: {EXPENSE}; }}

QComboBox {{ padding-right: 40px; }}
QComboBox[empty="true"] {{ color: {FAINT}; }}
QComboBox::drop-down, QDateEdit::drop-down {{
    subcontrol-origin: padding; subcontrol-position: center right;
    width: 40px; border: none; background: transparent;
}}
QComboBox::down-arrow {{ image: url({(ICONS / 'chevron-down.svg').as_posix()}); width: 16px; height: 16px; }}
QDateEdit::down-arrow {{ image: url({(ICONS / 'calendar.svg').as_posix()}); width: 16px; height: 16px; }}
QComboBox QAbstractItemView {{
    background: white; border: 1.5px solid {BORDER}; border-radius: 8px;
    padding: 4px; outline: none; color: {INK}; selection-background-color: {CHIP}; selection-color: {INK};
}}
QComboBox QAbstractItemView::item {{ min-height: 32px; padding: 0 10px; border-radius: 6px; }}

QCalendarWidget QWidget {{ alternate-background-color: white; }}
QCalendarWidget QAbstractItemView {{
    background: white; selection-background-color: {INK}; selection-color: white;
}}
QCalendarWidget QWidget#qt_calendar_navigationbar {{ background: white; }}
QCalendarWidget QToolButton {{ color: {INK}; background: transparent; padding: 4px 8px; border-radius: 6px; }}
QCalendarWidget QToolButton:hover {{ background: {CHIP}; }}

QPushButton {{ border: none; }}
QPushButton#primary {{
    background: {INK}; color: white; border-radius: 8px; padding: 14px;
}}
QPushButton#primary:hover {{ background: #3C3C3B; }}
QPushButton#primary:pressed {{ background: #000000; }}
QPushButton#primary[size="md"] {{ padding: 12px 22px; }}
QPushButton#primary[size="lg"] {{ padding: 15px; }}
QPushButton#primary[size="sm"] {{ padding: 10px 22px; border-radius: 6px; }}
QPushButton#primary[saved="true"] {{ background: {INCOME}; }}

QPushButton#secondary {{
    background: {CHIP}; color: {INK2}; border: 1.5px solid {BORDER}; border-radius: 6px; padding: 9px 22px;
}}
QPushButton#secondary:hover {{ background: #EAEAE6; }}

QPushButton#ghost {{
    background: white; color: {INK2}; border: 1.5px solid {BORDER}; border-radius: 6px; padding: 10px 22px;
}}
QPushButton#ghost:hover {{ background: {HOVER}; }}

QPushButton#danger {{
    background: {EXPENSE}; color: white; border-radius: 6px; padding: 10px 22px;
}}
QPushButton#danger:hover {{ background: #9E2A2A; }}

QPushButton#link {{ background: transparent; color: {MUTED}; padding: 0; text-decoration: underline; }}
QPushButton#link:hover {{ color: {INK}; }}
QPushButton#linkStrong {{ background: transparent; color: {INK}; padding: 0; text-decoration: underline; }}
QPushButton#linkStrong:hover {{ color: #3C3C3B; }}
QWidget#page {{ background: {BG}; }}
QFrame#loginLeft {{ background: {LOGIN_LEFT}; }}
QFrame#loginRight {{ background: #FFFFFF; }}
QLineEdit#prefixed {{ padding-left: 38px; }}

QPushButton#logout {{
    background: {INK}; color: white; border-radius: 10px; padding: 16px 24px; text-align: left;
}}
QPushButton#logout:hover {{ background: #3C3C3B; }}

QFrame#toggle {{ background: {CHIP}; border-radius: 8px; }}
QPushButton#seg {{ background: transparent; color: {INK3}; border-radius: 6px; padding: 11px; }}
QPushButton#seg:hover {{ color: {INK2}; }}
QPushButton#seg[active="expense"] {{ background: {EXPENSE}; color: white; }}
QPushButton#seg[active="income"] {{ background: {INCOME}; color: white; }}

QFrame#card {{ background: white; border: 1.5px solid {BORDER}; border-radius: 14px; }}
QFrame#table {{ background: white; border: 1.5px solid {BORDER}; border-radius: 12px; }}
QFrame#incomeCard {{ background: {INCOME_BG}; border: 1.5px solid {INCOME_BORDER}; border-radius: 12px; }}
QFrame#expenseCard {{ background: {EXPENSE_BG}; border: 1.5px solid {EXPENSE_BORDER}; border-radius: 12px; }}
QFrame#confirm {{ background: {EXPENSE_BG}; border: 1.5px solid {EXPENSE_BORDER}; border-radius: 10px; }}

QFrame#option {{ background: white; border: 1.5px solid {BORDER}; border-radius: 10px; }}
QFrame#option[danger="true"] {{ border-color: {EXPENSE_BORDER}; }}
QFrame#option[hover="true"] {{ background: {HOVER}; }}
QFrame#option[danger="true"][hover="true"] {{ background: {EXPENSE_BG}; }}

QFrame#row {{ background: transparent; border: none; border-bottom: 1px solid {BG}; }}
QFrame#row[last="true"] {{ border-bottom: none; }}
QFrame#row[hover="true"] {{ background: {HOVER}; }}
QFrame#divider {{ background: {DIVIDER}; border: none; }}

QFrame#sidebar {{ background: {SIDEBAR}; }}
QFrame#sideSep {{ background: rgba(255,255,255,0.07); border: none; }}
QFrame#nav {{ background: transparent; border-radius: 8px; }}
QFrame#nav[hover="true"] {{ background: rgba(255,255,255,0.05); }}
QFrame#nav[active="true"] {{ background: rgba(255,255,255,0.11); }}

QDialog {{ background: white; }}
QMessageBox {{ background: white; }}
"""
