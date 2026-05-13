"""
validator.py — Pure input validation functions and category constants.

All functions raise ValidationError (or InvalidAmountError) on invalid input
and return the cleaned/normalized value on success.
"""

from datetime import datetime

from src.exceptions import ValidationError, InvalidAmountError

# ── Category Constants ────────────────────────────────────────────────────────

CATEGORIES_INCOME = ["Salary", "Freelance", "Investment", "Gift", "Other"]

CATEGORIES_EXPENSE = [
    "Food", "Transport", "Housing", "Entertainment",
    "Utilities", "Healthcare", "Education", "Shopping", "Other"
]

TRANSACTION_TYPES = ["income", "expense"]

MAX_AMOUNT = 1_000_000_000  # 1 billion cap
MAX_DESCRIPTION_LENGTH = 200
MIN_YEAR = 2000
MAX_YEAR = 2100


# ── Validation Functions ─────────────────────────────────────────────────────

def validate_amount(value):
    """Validate and return a monetary amount.

    Args:
        value: The raw input value (string or numeric).

    Returns:
        float: Cleaned amount rounded to 2 decimal places.

    Raises:
        InvalidAmountError: If the value is empty, non-numeric, zero,
                            negative, or exceeds MAX_AMOUNT.
    """
    if value is None or (isinstance(value, str) and value.strip() == ""):
        raise InvalidAmountError("Amount cannot be empty", value=value)

    try:
        amount = float(value)
    except (ValueError, TypeError):
        raise InvalidAmountError(
            f"Amount must be a number, got '{value}'", value=value
        )

    if amount <= 0:
        raise InvalidAmountError(
            "Amount must be greater than zero", value=value
        )

    if amount > MAX_AMOUNT:
        raise InvalidAmountError(
            f"Amount cannot exceed {MAX_AMOUNT:,.0f}", value=value
        )

    return round(amount, 2)


def validate_date(value):
    """Validate and return a date string in YYYY-MM-DD format.

    Args:
        value: The raw date string.

    Returns:
        str: The validated date string in YYYY-MM-DD format.

    Raises:
        ValidationError: If the format is wrong, date is invalid,
                         or year is out of bounds.
    """
    if value is None or (isinstance(value, str) and value.strip() == ""):
        raise ValidationError("Date cannot be empty", field="date", value=value)

    value = value.strip()

    try:
        parsed = datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise ValidationError(
            "Date must be in YYYY-MM-DD format", field="date", value=value
        )

    if parsed.year < MIN_YEAR or parsed.year > MAX_YEAR:
        raise ValidationError(
            f"Year must be between {MIN_YEAR} and {MAX_YEAR}",
            field="date", value=value
        )

    return value


def validate_category(value, transaction_type):
    """Validate that a category is valid for the given transaction type.

    Args:
        value: The category string.
        transaction_type: Either 'income' or 'expense'.

    Returns:
        str: The validated category string.

    Raises:
        ValidationError: If the category is empty or not in the allowed list.
    """
    if value is None or (isinstance(value, str) and value.strip() == ""):
        raise ValidationError(
            "Category cannot be empty", field="category", value=value
        )

    value = value.strip()
    valid_categories = (
        CATEGORIES_INCOME if transaction_type == "income" else CATEGORIES_EXPENSE
    )

    if value not in valid_categories:
        raise ValidationError(
            f"Invalid category '{value}' for {transaction_type}. "
            f"Valid options: {', '.join(valid_categories)}",
            field="category", value=value
        )

    return value


def validate_description(value):
    """Validate and return a cleaned description string.

    Args:
        value: The raw description.

    Returns:
        str: Stripped description.

    Raises:
        ValidationError: If None, empty after stripping, or exceeds max length.
    """
    if value is None:
        raise ValidationError(
            "Description cannot be None", field="description", value=value
        )

    if isinstance(value, str):
        value = value.strip()

    if value == "":
        raise ValidationError(
            "Description cannot be empty", field="description", value=value
        )

    if len(value) > MAX_DESCRIPTION_LENGTH:
        raise ValidationError(
            f"Description cannot exceed {MAX_DESCRIPTION_LENGTH} characters",
            field="description", value=value
        )

    return value
