# User Flows - Visia

## Purpose
Help individuals track income and expenses on their own computer.

## Flow 1: Sign in / sign up
Entry: Login screen.
1. Enter username and password, then sign in. (First launch has a demo account.)
2. Or choose Sign Up and enter full name, username and password.
Validation: username 3+ chars (letters, numbers, dots, underscores); password 6+ chars.
Failure: "Incorrect username or password." Input is kept.

## Flow 2: Add a transaction
Entry: Sidebar > Add Transaction.
1. Toggle Expense or Income.
2. Enter amount, category, date and an optional note.
3. Save; the dashboard shows the new transaction and updated balance.

## Flow 3: Review the dashboard
Entry: After login.
Shows balance, this month's income and expenses vs. last month, and recent transactions.
Right-click a transaction to delete it.

## Flow 4: Manage account
Entry: Sidebar > Settings.
Change email, change password (needs current password), upload profile photo, delete account, log out.

## Open decisions
- "Forgot password" is a placeholder message; there is no recovery flow yet.
