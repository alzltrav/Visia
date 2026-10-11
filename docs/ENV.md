# Environment Setup - Visia

Visia is a local desktop app. It needs no API keys, accounts or `.env` file.

## Optional variables

VISIA_HOME
- Purpose: folder where the SQLite database (`visia.db`) and profile photos are stored.
- Default: `~/.visia`
- Secret: no.
- Example: `VISIA_HOME=./.visia-dev python main.py`

## Local setup
1. Install Python 3.10+.
2. `pip install -r requirements.txt`
3. `python main.py`

## Notes
- Data never leaves your machine. Delete the data folder to reset the app.
- The demo account (`juan` / `visia123`) is created only when the database has no users.
- If you ever add real secrets (API keys, etc.), put them in `.env` (already git-ignored) and commit a placeholder-only `.env.example`.
