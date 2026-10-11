from datetime import date, datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QFrame, QGridLayout, QHBoxLayout, QLabel, QMenu, QPushButton, QScrollArea,
                               QVBoxLayout, QWidget)

from . import theme as t
from .widgets import HoverFrame, amount_html, hline, label

COLS = (150, None, 160, 110)


def greeting():
    h = datetime.now().hour
    return "Good morning" if h < 12 else "Good afternoon" if h < 18 else "Good evening"


def month_delta(current, previous):
    if previous <= 0:
        return "No data from last month" if current <= 0 else "New this month"
    change = (current - previous) / previous * 100
    arrow = "↑" if change >= 0 else "↓"
    return f"{arrow} {abs(change):.0f}% from last month"


class SummaryCard(QFrame):
    def __init__(self, kind):
        super().__init__()
        income = kind == "income"
        self.setObjectName("incomeCard" if income else "expenseCard")
        color = t.INCOME if income else t.EXPENSE
        col = QVBoxLayout(self)
        col.setContentsMargins(30, 26, 30, 26)
        col.setSpacing(0)

        head = QHBoxLayout()
        head.setSpacing(8)
        dot = QLabel()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background: {color}; border-radius: 4px; border: none;")
        head.addWidget(dot)
        head.addWidget(label("Income" if income else "Expenses", t.BODY, 11, 600, color, 0.08, upper=True))
        head.addStretch()
        col.addLayout(head)
        col.addSpacing(14)

        self.amount = label("", t.DISPLAY, 36, 700, t.INK, -0.03)
        self.amount.setTextFormat(Qt.TextFormat.RichText)
        self.amount.setStyleSheet("background: transparent; border: none;")
        col.addWidget(self.amount)
        col.addSpacing(8)
        self.delta = label("", t.BODY, 12, 400, color)
        self.delta.setStyleSheet(f"color: {color}; background: transparent; border: none;")
        col.addWidget(self.delta)

    def set_values(self, current, previous):
        self.amount.setText(amount_html(current, 20, 20))
        self.delta.setText(month_delta(current, previous))


class TxRow(HoverFrame):
    delete_requested = Signal(int)

    def __init__(self, tx, last):
        super().__init__("row", clickable=False)
        self.tx = tx
        self.setProperty("last", last)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        row = QHBoxLayout(self)
        row.setContentsMargins(28, 15, 28, 15)
        row.setSpacing(0)

        d = date.fromisoformat(tx.date)
        date_lbl = label(d.strftime("%b %d, %Y"), t.MONO, 11, 400, t.INK3)
        date_lbl.setFixedWidth(COLS[0])
        row.addWidget(date_lbl)

        desc = QHBoxLayout()
        desc.setSpacing(10)
        desc.addWidget(label(t.CATEGORY_ICONS.get(tx.category, "📱"), t.BODY, 17))
        name = label(tx.note or tx.category, t.BODY, 14, 500, t.INK)
        name.setToolTip(tx.note or tx.category)
        desc.addWidget(name, 1)
        row.addLayout(desc, 1)

        chip_box = QWidget()
        chip_box.setFixedWidth(COLS[2])
        chip_lay = QHBoxLayout(chip_box)
        chip_lay.setContentsMargins(0, 0, 8, 0)
        chip = label(tx.category, t.BODY, 11, 400, "#666662")
        chip.setStyleSheet(f"color: #666662; background: {t.CHIP}; border-radius: 10px; padding: 3px 10px;")
        chip_lay.addWidget(chip)
        chip_lay.addStretch()
        row.addWidget(chip_box)

        amt = label(t.peso(tx.signed, signed=True), t.MONO, 13, 500, t.INCOME if tx.kind == "income" else t.EXPENSE)
        amt.setFixedWidth(COLS[3])
        amt.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(amt)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._menu)
        self.setToolTip("Right-click to delete")

    def _menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet(f"QMenu {{ background: white; border: 1.5px solid {t.BORDER}; border-radius: 8px; padding: 4px; }}"
                           f"QMenu::item {{ padding: 8px 16px; border-radius: 6px; color: {t.EXPENSE}; }}"
                           f"QMenu::item:selected {{ background: {t.EXPENSE_BG}; }}")
        action = menu.addAction("Delete transaction")
        if menu.exec(self.mapToGlobal(pos)) == action:
            self.delete_requested.emit(self.tx.id)


class DashboardScreen(QScrollArea):
    add_requested = Signal()
    changed = Signal()

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

        top = QHBoxLayout()
        left = QVBoxLayout()
        left.setSpacing(0)
        self.hello = label("", t.BODY, 13, 400, t.MUTED, 0.01)
        left.addWidget(self.hello)
        left.addSpacing(10)
        left.addWidget(label("Current Balance", t.BODY, 11, 600, t.INK3, 0.08, upper=True))
        left.addSpacing(6)
        self.balance = label("", t.DISPLAY, 52, 700, t.INK, -0.04)
        self.balance.setTextFormat(Qt.TextFormat.RichText)
        left.addWidget(self.balance)
        top.addLayout(left)
        top.addStretch()

        add = QPushButton("+  Add New")
        add.setObjectName("primary")
        add.setFont(t.font(t.DISPLAY, 14, 600, -0.01))
        add.setProperty("size", "md")
        add.setCursor(Qt.CursorShape.PointingHandCursor)
        add.clicked.connect(self.add_requested)
        top.addWidget(add, 0, Qt.AlignmentFlag.AlignTop)
        col.addLayout(top)
        col.addSpacing(36)

        cards = QGridLayout()
        cards.setHorizontalSpacing(16)
        self.income_card = SummaryCard("income")
        self.expense_card = SummaryCard("expense")
        cards.addWidget(self.income_card, 0, 0)
        cards.addWidget(self.expense_card, 0, 1)
        col.addLayout(cards)
        col.addSpacing(32)

        table = QFrame()
        table.setObjectName("table")
        tcol = QVBoxLayout(table)
        tcol.setContentsMargins(0, 0, 0, 0)
        tcol.setSpacing(0)

        head = QHBoxLayout()
        head.setContentsMargins(28, 20, 28, 20)
        head.addWidget(label("Recent Transactions", t.DISPLAY, 16, 600, t.INK))
        head.addStretch()
        self.month_lbl = label("", t.BODY, 12, 400, t.INK3)
        head.addWidget(self.month_lbl)
        tcol.addLayout(head)
        tcol.addWidget(hline())

        header = QHBoxLayout()
        header.setContentsMargins(28, 11, 28, 11)
        header.setSpacing(0)
        for text, width in zip(("Date", "Description", "Category", "Amount"), COLS):
            h = label(text, t.BODY, 10, 600, t.FAINT, 0.07, upper=True)
            if width:
                h.setFixedWidth(width)
                header.addWidget(h)
            else:
                header.addWidget(h, 1)
            if text == "Amount":
                h.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        tcol.addLayout(header)
        tcol.addWidget(hline())

        self.rows = QVBoxLayout()
        self.rows.setSpacing(0)
        tcol.addLayout(self.rows)
        tcol.addSpacing(2)

        col.addWidget(table)
        col.addStretch()

    def set_user(self, user):
        self.user = user
        self.refresh()

    def refresh(self):
        if not self.user:
            return
        today = date.today()
        prev_year, prev_month = (today.year, today.month - 1) if today.month > 1 else (today.year - 1, 12)
        cur = self.db.month_totals(self.user.id, today.year, today.month)
        prev = self.db.month_totals(self.user.id, prev_year, prev_month)

        self.hello.setText(f"{greeting()}, {self.user.first_name}")
        self.balance.setText(amount_html(self.db.balance(self.user.id), 30, 28))
        self.income_card.set_values(cur["income"], prev["income"])
        self.expense_card.set_values(cur["expense"], prev["expense"])
        self.month_lbl.setText(today.strftime("%b %Y"))

        while self.rows.count():
            w = self.rows.takeAt(0).widget()
            if w:
                w.hide()
                w.setParent(None)
                w.deleteLater()

        txs = self.db.recent_transactions(self.user.id)
        if not txs:
            empty = label('No transactions yet. Click "Add New" to record your first one.', t.BODY, 13, 400, t.INK3)
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setContentsMargins(28, 40, 28, 40)
            self.rows.addWidget(empty)
            return
        for i, tx in enumerate(txs):
            row = TxRow(tx, last=i == len(txs) - 1)
            row.delete_requested.connect(self._delete)
            self.rows.addWidget(row)

    def _delete(self, tx_id):
        self.db.delete_transaction(self.user.id, tx_id)
        self.refresh()
        self.changed.emit()
