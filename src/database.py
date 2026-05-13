"""
database.py — DatabaseManager for Personal Finance Tracker.

All SQL is isolated in this module. The rest of the application interacts
with the database exclusively through DatabaseManager methods.
"""

import sqlite3

from src.exceptions import DatabaseError, TransactionNotFoundError


class DatabaseManager:
    """Manages all SQLite operations for transactions and budgets."""

    def __init__(self, db_path="finance_tracker.db"):
        """Initialize connection and create tables if they don't exist.

        Args:
            db_path: Path to the SQLite database file. Use ':memory:' for tests.

        Raises:
            DatabaseError: If the connection or table creation fails.
        """
        try:
            self.conn = sqlite3.connect(db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            self._create_tables()
        except sqlite3.Error as e:
            raise DatabaseError(
                "Failed to initialize database",
                operation="init", original_error=e
            )

    def _create_tables(self):
        """Create the transactions and budgets tables if they don't exist."""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    date TEXT NOT NULL,
                    description TEXT
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    month INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    UNIQUE(category, month, year)
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(
                "Failed to create tables",
                operation="create_tables", original_error=e
            )

    # ── Transaction CRUD ─────────────────────────────────────────────────────

    def add_transaction(self, txn_type, category, amount, date, description=""):
        """Insert a new transaction record.

        Args:
            txn_type: 'income' or 'expense'.
            category: Transaction category.
            amount: Monetary amount (positive float).
            date: Date string in YYYY-MM-DD format.
            description: Optional description text.

        Returns:
            int: The ID of the newly created transaction.

        Raises:
            DatabaseError: If the INSERT fails.
        """
        try:
            self.cursor.execute(
                """INSERT INTO transactions (type, category, amount, date, description)
                   VALUES (?, ?, ?, ?, ?)""",
                (txn_type, category, amount, date, description)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            raise DatabaseError(
                "Failed to add transaction",
                operation="add_transaction", original_error=e
            )

    def get_all_transactions(self):
        """Retrieve all transactions ordered by date descending.

        Returns:
            list[dict]: List of transaction dictionaries.
        """
        try:
            self.cursor.execute(
                "SELECT * FROM transactions ORDER BY date DESC, id DESC"
            )
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            raise DatabaseError(
                "Failed to retrieve transactions",
                operation="get_all_transactions", original_error=e
            )

    def get_transaction_by_id(self, txn_id):
        """Retrieve a single transaction by ID.

        Args:
            txn_id: The transaction ID.

        Returns:
            dict: The transaction record.

        Raises:
            TransactionNotFoundError: If no transaction matches the ID.
        """
        try:
            self.cursor.execute(
                "SELECT * FROM transactions WHERE id = ?", (txn_id,)
            )
            row = self.cursor.fetchone()
            if row is None:
                raise TransactionNotFoundError(transaction_id=txn_id)
            return dict(row)
        except TransactionNotFoundError:
            raise
        except sqlite3.Error as e:
            raise DatabaseError(
                f"Failed to retrieve transaction {txn_id}",
                operation="get_transaction_by_id", original_error=e
            )

    def delete_transaction(self, txn_id):
        """Delete a transaction by ID.

        Args:
            txn_id: The transaction ID to delete.

        Returns:
            bool: True if the transaction was deleted.

        Raises:
            TransactionNotFoundError: If no transaction matches the ID.
        """
        try:
            self.cursor.execute(
                "DELETE FROM transactions WHERE id = ?", (txn_id,)
            )
            if self.cursor.rowcount == 0:
                raise TransactionNotFoundError(transaction_id=txn_id)
            self.conn.commit()
            return True
        except TransactionNotFoundError:
            raise
        except sqlite3.Error as e:
            raise DatabaseError(
                f"Failed to delete transaction {txn_id}",
                operation="delete_transaction", original_error=e
            )

    def search_transactions(self, keyword=None, type_filter=None,
                            category_filter=None, date_from=None, date_to=None):
        """Search transactions with optional filters.

        Args:
            keyword: Search in description (LIKE match).
            type_filter: Filter by 'income' or 'expense'.
            category_filter: Filter by category name.
            date_from: Start date (inclusive) in YYYY-MM-DD.
            date_to: End date (inclusive) in YYYY-MM-DD.

        Returns:
            list[dict]: Matching transactions ordered by date descending.
        """
        try:
            query = "SELECT * FROM transactions WHERE 1=1"
            params = []

            if keyword:
                query += " AND description LIKE ?"
                params.append(f"%{keyword}%")
            if type_filter:
                query += " AND type = ?"
                params.append(type_filter)
            if category_filter:
                query += " AND category = ?"
                params.append(category_filter)
            if date_from:
                query += " AND date >= ?"
                params.append(date_from)
            if date_to:
                query += " AND date <= ?"
                params.append(date_to)

            query += " ORDER BY date DESC, id DESC"
            self.cursor.execute(query, params)
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            raise DatabaseError(
                "Failed to search transactions",
                operation="search_transactions", original_error=e
            )

    # ── Summary & Charts ─────────────────────────────────────────────────────

    def get_summary(self, month, year):
        """Get total income and expense for a given month/year.

        Args:
            month: Month number (1-12).
            year: Four-digit year.

        Returns:
            dict: {'total_income': float, 'total_expense': float, 'net': float}
        """
        try:
            date_prefix = f"{year:04d}-{month:02d}"
            result = {"total_income": 0.0, "total_expense": 0.0, "net": 0.0}

            for txn_type in ("income", "expense"):
                self.cursor.execute(
                    """SELECT COALESCE(SUM(amount), 0) as total
                       FROM transactions
                       WHERE type = ? AND date LIKE ?""",
                    (txn_type, f"{date_prefix}%")
                )
                row = self.cursor.fetchone()
                result[f"total_{txn_type}"] = row["total"]

            result["net"] = result["total_income"] - result["total_expense"]
            return result
        except sqlite3.Error as e:
            raise DatabaseError(
                "Failed to get summary",
                operation="get_summary", original_error=e
            )

    def get_category_breakdown(self, month, year, txn_type="expense"):
        """Get spending/income grouped by category for a month.

        Args:
            month: Month number (1-12).
            year: Four-digit year.
            txn_type: 'income' or 'expense'.

        Returns:
            list[dict]: [{'category': str, 'total': float}, ...]
        """
        try:
            date_prefix = f"{year:04d}-{month:02d}"
            self.cursor.execute(
                """SELECT category, SUM(amount) as total
                   FROM transactions
                   WHERE type = ? AND date LIKE ?
                   GROUP BY category
                   ORDER BY total DESC""",
                (txn_type, f"{date_prefix}%")
            )
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            raise DatabaseError(
                "Failed to get category breakdown",
                operation="get_category_breakdown", original_error=e
            )

    def get_monthly_trend(self, year):
        """Get monthly income and expense totals for a given year.

        Args:
            year: Four-digit year.

        Returns:
            list[dict]: [{'month': int, 'income': float, 'expense': float}, ...]
                        One entry per month (1-12).
        """
        try:
            results = []
            for month in range(1, 13):
                date_prefix = f"{year:04d}-{month:02d}"
                income = 0.0
                expense = 0.0

                self.cursor.execute(
                    """SELECT type, COALESCE(SUM(amount), 0) as total
                       FROM transactions
                       WHERE date LIKE ?
                       GROUP BY type""",
                    (f"{date_prefix}%",)
                )
                for row in self.cursor.fetchall():
                    if row["type"] == "income":
                        income = row["total"]
                    elif row["type"] == "expense":
                        expense = row["total"]

                results.append({
                    "month": month,
                    "income": income,
                    "expense": expense
                })
            return results
        except sqlite3.Error as e:
            raise DatabaseError(
                "Failed to get monthly trend",
                operation="get_monthly_trend", original_error=e
            )

    # ── Budget Management ────────────────────────────────────────────────────

    def set_budget(self, category, amount, month, year):
        """Set or update a monthly budget for a category.

        Args:
            category: Expense category name.
            amount: Budget limit amount.
            month: Month number (1-12).
            year: Four-digit year.

        Returns:
            int: The budget record ID.
        """
        try:
            self.cursor.execute(
                """INSERT OR REPLACE INTO budgets (category, amount, month, year)
                   VALUES (?, ?, ?, ?)""",
                (category, amount, month, year)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            raise DatabaseError(
                "Failed to set budget",
                operation="set_budget", original_error=e
            )

    def get_budget(self, category, month, year):
        """Get the budget for a specific category and month.

        Args:
            category: Expense category name.
            month: Month number (1-12).
            year: Four-digit year.

        Returns:
            dict or None: Budget record or None if not set.
        """
        try:
            self.cursor.execute(
                """SELECT * FROM budgets
                   WHERE category = ? AND month = ? AND year = ?""",
                (category, month, year)
            )
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            raise DatabaseError(
                "Failed to get budget",
                operation="get_budget", original_error=e
            )

    def get_all_budgets(self, month, year):
        """Get all budgets for a given month/year.

        Args:
            month: Month number (1-12).
            year: Four-digit year.

        Returns:
            list[dict]: List of budget records.
        """
        try:
            self.cursor.execute(
                """SELECT * FROM budgets
                   WHERE month = ? AND year = ?
                   ORDER BY category""",
                (month, year)
            )
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            raise DatabaseError(
                "Failed to get budgets",
                operation="get_all_budgets", original_error=e
            )

    def close(self):
        """Close the database connection."""
        try:
            if self.conn:
                self.conn.close()
        except sqlite3.Error as e:
            raise DatabaseError(
                "Failed to close database",
                operation="close", original_error=e
            )
