import hashlib
import os
import secrets
import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

DATA_DIR = Path(os.environ.get("VISIA_HOME", Path.home() / ".visia"))
DB_PATH = DATA_DIR / "visia.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL DEFAULT '',
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    photo_path TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    password_changed_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    kind TEXT NOT NULL CHECK (kind IN ('income', 'expense')),
    amount REAL NOT NULL CHECK (amount > 0),
    category TEXT NOT NULL,
    date TEXT NOT NULL,
    note TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tx_user_date ON transactions(user_id, date);
"""


@dataclass
class User:
    id: int
    username: str
    full_name: str
    email: str
    photo_path: str
    created_at: str
    password_changed_at: str

    @property
    def first_name(self):
        return self.full_name.split()[0] if self.full_name.strip() else self.username

    @property
    def initials(self):
        parts = [p for p in self.full_name.split() if p]
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        return (parts[0][:2] if parts else self.username[:2]).upper()


@dataclass
class Transaction:
    id: int
    kind: str
    amount: float
    category: str
    date: str
    note: str

    @property
    def signed(self):
        return self.amount if self.kind == "income" else -self.amount


class AuthError(Exception):
    pass


def _hash(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 200_000).hex()


def _now():
    return datetime.now().isoformat(timespec="seconds")


class Database:
    def __init__(self, path=DB_PATH):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def _user(self, row):
        return User(row["id"], row["username"], row["full_name"], row["email"], row["photo_path"],
                    row["created_at"], row["password_changed_at"]) if row else None

    def get_user(self, user_id):
        return self._user(self.conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone())

    def user_count(self):
        return self.conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    def create_user(self, username, password, full_name, email="", created_at=None):
        username = username.strip()
        if len(username) < 3:
            raise AuthError("Username must be at least 3 characters.")
        if not username.replace("_", "").replace(".", "").isalnum():
            raise AuthError("Username can only use letters, numbers, dots and underscores.")
        if len(password) < 6:
            raise AuthError("Password must be at least 6 characters.")
        if not full_name.strip():
            raise AuthError("Please enter your full name.")
        if self.conn.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone():
            raise AuthError("That username is already taken.")
        salt = secrets.token_hex(16)
        now = created_at or _now()
        cur = self.conn.execute(
            "INSERT INTO users (username, full_name, email, password_hash, salt, created_at, password_changed_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (username, full_name.strip(), email.strip(), _hash(password, salt), salt, now, now),
        )
        self.conn.commit()
        return self.get_user(cur.lastrowid)

    def authenticate(self, username, password):
        if not username.strip() or not password:
            raise AuthError("Enter your username and password.")
        row = self.conn.execute("SELECT * FROM users WHERE username = ?", (username.strip(),)).fetchone()
        if not row or not secrets.compare_digest(_hash(password, row["salt"]), row["password_hash"]):
            raise AuthError("Incorrect username or password.")
        return self._user(row)

    def update_email(self, user_id, email):
        self.conn.execute("UPDATE users SET email = ? WHERE id = ?", (email.strip(), user_id))
        self.conn.commit()

    def update_photo(self, user_id, path):
        self.conn.execute("UPDATE users SET photo_path = ? WHERE id = ?", (path, user_id))
        self.conn.commit()

    def change_password(self, user_id, current, new):
        row = self.conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not secrets.compare_digest(_hash(current, row["salt"]), row["password_hash"]):
            raise AuthError("Current password is incorrect.")
        if len(new) < 6:
            raise AuthError("New password must be at least 6 characters.")
        salt = secrets.token_hex(16)
        self.conn.execute("UPDATE users SET password_hash = ?, salt = ?, password_changed_at = ? WHERE id = ?",
                          (_hash(new, salt), salt, _now(), user_id))
        self.conn.commit()

    def delete_user(self, user_id):
        row = self.conn.execute("SELECT photo_path FROM users WHERE id = ?", (user_id,)).fetchone()
        self.conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        self.conn.commit()
        if row and row["photo_path"]:
            Path(row["photo_path"]).unlink(missing_ok=True)

    def add_transaction(self, user_id, kind, amount, category, day, note=""):
        self.conn.execute(
            "INSERT INTO transactions (user_id, kind, amount, category, date, note, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, kind, round(float(amount), 2), category, day, note.strip(), _now()),
        )
        self.conn.commit()

    def delete_transaction(self, user_id, tx_id):
        self.conn.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?", (tx_id, user_id))
        self.conn.commit()

    def recent_transactions(self, user_id, limit=50):
        rows = self.conn.execute(
            "SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT ?", (user_id, limit)
        ).fetchall()
        return [Transaction(r["id"], r["kind"], r["amount"], r["category"], r["date"], r["note"]) for r in rows]

    def balance(self, user_id):
        row = self.conn.execute(
            "SELECT COALESCE(SUM(CASE WHEN kind = 'income' THEN amount ELSE -amount END), 0) FROM transactions WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        return row[0]

    def month_totals(self, user_id, year, month):
        prefix = f"{year:04d}-{month:02d}-%"
        rows = self.conn.execute(
            "SELECT kind, SUM(amount) FROM transactions WHERE user_id = ? AND date LIKE ? GROUP BY kind",
            (user_id, prefix),
        ).fetchall()
        totals = {"income": 0.0, "expense": 0.0}
        totals.update({r[0]: r[1] for r in rows})
        return totals


def seed_demo(db):
    if db.user_count():
        return
    user = db.create_user("juan", "visia123", "Juan Dela Cruz", "juandelacruz@email.com",
                          created_at="2025-01-15T09:00:00")
    today = date.today()
    first = today.replace(day=1)
    last_month = first - timedelta(days=1)

    def day(offset):
        return max(first, today - timedelta(days=offset)).isoformat()

    def prev(d):
        return last_month.replace(day=min(d, last_month.day)).isoformat()

    entries = [
        ("income", 6200.00, "Salary", prev(1), "Opening Savings"),
        ("income", 5200.00, "Salary", prev(27), "Monthly Salary"),
        ("income", 700.00, "Freelance", prev(18), "Logo Commission"),
        ("expense", 1500.00, "Housing", prev(5), "Rent Share"),
        ("expense", 310.00, "Food & Dining", prev(14), "Groceries"),
        ("income", 5200.00, "Salary", day(7), "Monthly Salary"),
        ("income", 1200.00, "Freelance", day(4), "Freelance Project"),
        ("expense", 500.00, "Other", day(6), "GCash Transfer"),
        ("expense", 38.00, "Healthcare", day(5), "Mercury Drug"),
        ("expense", 142.00, "Utilities", day(3), "Meralco Bill"),
        ("expense", 15.99, "Food & Dining", day(2), "Jollibee"),
        ("expense", 18.50, "Transport", day(1), "Grab Ride"),
        ("expense", 84.32, "Shopping", day(0), "SM Supermarket"),
    ]
    for kind, amount, category, d, note in entries:
        db.add_transaction(user.id, kind, amount, category, d, note)
