"""
exceptions.py — Custom exception hierarchy for Personal Finance Tracker.

Exception
└── FinanceTrackerError          ← base class
    ├── DatabaseError            ← wraps sqlite3.Error with context
    ├── ValidationError          ← field-level input errors
    │   └── InvalidAmountError   ← specific for monetary values
    ├── BudgetExceededError      ← budget limit violations
    └── TransactionNotFoundError ← missing record lookups
"""


class FinanceTrackerError(Exception):
    """Base exception for all Personal Finance Tracker errors."""

    def __init__(self, message="A finance tracker error occurred"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message


class DatabaseError(FinanceTrackerError):
    """Raised when a database operation fails.

    Wraps the original sqlite3.Error with additional context about
    which operation was being performed.
    """

    def __init__(self, message="A database error occurred", operation=None, original_error=None):
        self.operation = operation
        self.original_error = original_error
        detail = message
        if operation:
            detail = f"[{operation}] {message}"
        if original_error:
            detail = f"{detail} (caused by: {original_error})"
        super().__init__(detail)


class ValidationError(FinanceTrackerError):
    """Raised when user input fails validation.

    Stores the field name and the invalid value for structured reporting.
    """

    def __init__(self, message="Validation failed", field=None, value=None):
        self.field = field
        self.value = value
        detail = message
        if field:
            detail = f"[{field}] {message}"
        super().__init__(detail)


class InvalidAmountError(ValidationError):
    """Raised specifically for invalid monetary amounts.

    A subclass of ValidationError that always targets the 'amount' field.
    """

    def __init__(self, message="Invalid amount", value=None):
        super().__init__(message=message, field="amount", value=value)


class BudgetExceededError(FinanceTrackerError):
    """Raised when spending in a category exceeds the set budget.

    Stores the category, the budget limit, and the actual spent amount.
    """

    def __init__(self, message="Budget exceeded", category=None, budget_limit=None, spent=None):
        self.category = category
        self.budget_limit = budget_limit
        self.spent = spent
        detail = message
        if category and budget_limit is not None and spent is not None:
            detail = (
                f"Budget exceeded for '{category}': "
                f"spent ${spent:.2f} of ${budget_limit:.2f} budget"
            )
        super().__init__(detail)


class TransactionNotFoundError(FinanceTrackerError):
    """Raised when a transaction lookup or deletion targets a non-existent ID."""

    def __init__(self, message="Transaction not found", transaction_id=None):
        self.transaction_id = transaction_id
        detail = message
        if transaction_id is not None:
            detail = f"Transaction with ID {transaction_id} not found"
        super().__init__(detail)
