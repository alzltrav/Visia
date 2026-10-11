# Visia — Expense Tracker (Desktop)

A PySide6 (Qt) desktop app built from the "Expense Tracker Web App" Figma Make design.

## Requirements

Python 3.10+ and PySide6 (installed via `requirements.txt`).

## Run

```bash
pip install -r requirements.txt
python main.py
```

First launch creates a demo account so you can see the dashboard filled in:

- Username: `juan`
- Password: `visia123`

Or click **Sign Up** to make your own account.

## Features

- Login / sign up with hashed passwords (PBKDF2)
- Dashboard: balance, this month's income and expenses vs. last month, recent transactions
- Right-click a transaction to delete it
- Add Transaction: expense/income toggle, amount, category, date, optional note
- Settings: change email, change password, upload profile photo, delete account, logout

## Where data is stored

SQLite database at `~/.visia/visia.db` (set the `VISIA_HOME` environment variable to use another folder).
Delete that folder to start fresh.

## Project layout

```
main.py                 entry point
app/theme.py            colors, fonts, global stylesheet
app/db.py               SQLite storage, auth, demo data
app/shell.py            main window, sidebar, navigation
app/login.py            login / sign-up screen
app/dashboard.py        home screen
app/add_transaction.py  add transaction form
app/settings.py         settings screen
app/dialogs.py          change email / password dialogs
app/widgets.py          shared widgets (avatar, logo, hover rows)
app/icons.py            SVG icons and login illustration
assets/fonts            DM Sans, Inter, DM Mono (SIL Open Font License)
```

## Docs

- [User flows](docs/USER-FLOWS.md)
- [Environment setup](docs/ENV.md)
- [Changelog](CHANGELOG.md)
- [Tasks](TASKS.md)

## License

MIT, see [LICENSE](LICENSE). Bundled fonts are under the SIL Open Font License (`assets/fonts/OFL.txt`).
