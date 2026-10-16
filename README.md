# Ledger — Student Budget & Savings Tracker

A simple **Python console application** that helps students track their allowance, expenses, savings, and remaining budget, using Object-Oriented Programming (OOP).

## Features

- Enter a student name and allowance (per day, week, or month)
- Add expenses with categories and notes
- Add savings and view total saved
- See remaining balance and expense totals by category
- List and delete transactions
- Calculate arithmetic expressions using `=40+20*2`
- Automatically save data locally in `budget_data.json`

## How to run

Install Python 3.8 or newer and open a terminal inside the project folder:

```bash
python main.py
```

On some systems, use `python3 main.py`. No external dependencies are needed.

## OOP classes

| Class | Purpose |
| --- | --- |
| `Student` | Stores the name and allowance |
| `Expense` | Represents an expense record |
| `Saving` | Represents a savings record |
| `BudgetTracker` | Stores transactions and calculates totals |
| `Calculator` | Evaluates basic arithmetic safely |

## Data and privacy

`budget_data.json` is automatically created locally and excluded from Git through `.gitignore`. Do not publish your personal budget data.

**Note:** The allowance amount is one budget total; expenses and savings accumulate until you reset the tracker. Choosing daily, weekly, or monthly does not automatically filter transactions by date.
