# Visia: Track Every Peso with Clarity

A desktop expense tracker for people who want to know where their money goes without keeping a notebook or maintaining a spreadsheet. Record income and expenses in pesos, and see your balance, this month's totals and a comparison with last month on one dashboard.

Built with Python, PySide6 (Qt) and SQLite. Everything stays on your computer and the app works offline.

> Project for **6IMSOFTENG**, School of Computing, Holy Angel University, First Semester A.Y. 2026-2027.

<!-- Add screenshots here once they are in docs/screenshots/, for example:
![Dashboard](docs/screenshots/dashboard.png)
-->

## Features

- Sign up and log in, with passwords stored as salted PBKDF2 hashes
- Dashboard: current balance, this month's income and expenses compared with last month, and recent transactions
- Add Transaction: expense/income toggle, amount in pesos, category, date and an optional note
- Delete a transaction by right-clicking it
- Settings: change email, change password, upload a profile photo, delete account, log out

## Get it

```bash
git clone https://github.com/alzltrav/visia.git
cd visia
```

## Requirements

Python 3.13 or newer and PySide6 (installed through `requirements.txt`). Demonstrated on Windows; the same code is expected to run on macOS and Linux but has not been tested there.

## Run

```bash
pip install -r requirements.txt
python main.py
```

First launch creates a demo account so you can see the dashboard filled in:

- Username: `juan`
- Password: `visia123`

Or click **Sign Up** to make your own account.

## Where data is stored

A SQLite database at `~/.visia/visia.db`. Set the `VISIA_HOME` environment variable to use another folder. Copy `visia.db` to back up your records, or delete the folder to start fresh.

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

## Known limitations

- No password recovery: without an email service, a forgotten password means creating a new account
- Transactions can be added and deleted but not edited
- Data lives on one computer, with no sync between devices

See [TASKS.md](TASKS.md) for planned work.

## Team

- Keon Zane Almodovar
- Travis Alzola
- Kiel Xedric Barles
- Jan Marti Dizon
- Samuel David Mercado

## Docs

- [User flows](docs/USER-FLOWS.md)
- [Environment setup](docs/ENV.md)
- [Changelog](CHANGELOG.md)
- [Tasks](TASKS.md)

## License

MIT, see [LICENSE](LICENSE). Bundled fonts are under the SIL Open Font License (`assets/fonts/OFL.txt`).
