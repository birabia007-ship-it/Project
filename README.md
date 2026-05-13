# Personal Finance Tracker

A standalone Python desktop application for tracking personal income and expenses, setting monthly budgets per category, and visualizing financial health through interactive charts.

## Features

- **Transaction Management**: Add, view, search, filter, and delete income/expense records
- **Budget Tracking**: Set monthly spending budgets per category with visual progress indicators
- **Interactive Dashboard**: Pie charts for expense breakdown and bar charts for monthly trends
- **Data Persistence**: SQLite database with automatic creation on first run
- **Input Validation**: Comprehensive validation with structured error messages
- **Custom Exceptions**: Full exception hierarchy for robust error handling

## Project Structure

```
Project/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── database.py             # DatabaseManager (SQLite)
│   ├── validator.py            # Input validation + constants
│   ├── exceptions.py           # Custom exception hierarchy
│   └── views/
│       ├── __init__.py
│       ├── transaction_view.py # Add/view/search/delete transactions
│       ├── dashboard_view.py   # Pie + bar charts, summary stats
│       └── budget_view.py      # Budget setting + monitoring
├── tests/
│   ├── __init__.py
│   ├── test_database.py        # 16 tests
│   ├── test_validator.py       # 26 tests
│   └── test_exceptions.py      # 10 tests
└── README.md
```

## Requirements

- Python 3.10+
- No external dependencies — uses only Python's standard library:
  - `tkinter` — GUI framework
  - `sqlite3` — Database
  - `datetime` — Date handling
  - `unittest` — Testing

## Setup & Run

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd Project
   ```

2. Run the application:
   ```bash
   python src/main.py
   ```

3. The SQLite database (`finance_tracker.db`) is automatically created on first run.

## Running Tests

```bash
python -m unittest discover tests/ -v
```

**Total: 52 tests** — all should pass ✅

### Test Breakdown

| Module | Tests | Coverage |
|--------|-------|----------|
| `test_database.py` | 16 | CRUD, search, summary, budgets, trends |
| `test_validator.py` | 26 | Amount, date, category, description validation |
| `test_exceptions.py` | 10 | Exception fields, messages, inheritance |

## Exception Hierarchy

```
Exception
└── FinanceTrackerError          ← base class
    ├── DatabaseError            ← wraps sqlite3.Error with context
    ├── ValidationError          ← field-level input errors
    │   └── InvalidAmountError   ← specific for monetary values
    ├── BudgetExceededError      ← budget limit violations
    └── TransactionNotFoundError ← missing record lookups
```

## Architecture

- **All SQL isolated** in `DatabaseManager` — no SQL in UI code
- **Pure validation functions** in `validator.py` — no side effects
- **Custom exceptions** for structured error reporting
- **Modular views** — each tab is a self-contained class
- **Parameterized queries** — protection against SQL injection

## Deployment

### Run directly
```bash
python src/main.py
```

### Package as executable
```bash
pip install pyinstaller
pyinstaller --onefile src/main.py
```

## UI Theme

Dark navy theme with teal accents:
- Income transactions in green (#00b894)
- Expense transactions in red (#e94560)
- Interactive canvas-drawn charts (no external chart libraries)
- Color-coded budget progress bars (green → yellow → red)
