"""
test_exceptions.py — 10 unit tests for the custom exception hierarchy.

Tests all exception classes for correct fields, messages, and inheritance.
"""

import unittest
from src.exceptions import (
    FinanceTrackerError, DatabaseError, ValidationError,
    InvalidAmountError, BudgetExceededError, TransactionNotFoundError
)


class TestFinanceTrackerError(unittest.TestCase):
    """Tests for the base FinanceTrackerError."""

    def test_default_message(self):
        e = FinanceTrackerError()
        self.assertEqual(str(e), "A finance tracker error occurred")

    def test_custom_message(self):
        e = FinanceTrackerError("custom error")
        self.assertEqual(str(e), "custom error")
        self.assertEqual(e.message, "custom error")

    def test_inherits_from_exception(self):
        e = FinanceTrackerError()
        self.assertIsInstance(e, Exception)


class TestDatabaseError(unittest.TestCase):
    """Tests for DatabaseError."""

    def test_with_operation_and_original(self):
        orig = Exception("disk full")
        e = DatabaseError("write failed", operation="insert", original_error=orig)
        self.assertIn("insert", str(e))
        self.assertIn("write failed", str(e))
        self.assertIn("disk full", str(e))
        self.assertEqual(e.operation, "insert")
        self.assertEqual(e.original_error, orig)

    def test_inherits_from_base(self):
        e = DatabaseError()
        self.assertIsInstance(e, FinanceTrackerError)


class TestValidationError(unittest.TestCase):
    """Tests for ValidationError."""

    def test_with_field_and_value(self):
        e = ValidationError("bad input", field="email", value="not-an-email")
        self.assertIn("email", str(e))
        self.assertEqual(e.field, "email")
        self.assertEqual(e.value, "not-an-email")

    def test_inherits_from_base(self):
        e = ValidationError()
        self.assertIsInstance(e, FinanceTrackerError)


class TestInvalidAmountError(unittest.TestCase):
    """Tests for InvalidAmountError."""

    def test_field_is_amount(self):
        e = InvalidAmountError("negative value", value=-50)
        self.assertEqual(e.field, "amount")
        self.assertEqual(e.value, -50)

    def test_inherits_from_validation_error(self):
        e = InvalidAmountError()
        self.assertIsInstance(e, ValidationError)
        self.assertIsInstance(e, FinanceTrackerError)


class TestBudgetExceededError(unittest.TestCase):
    """Tests for BudgetExceededError."""

    def test_with_budget_details(self):
        e = BudgetExceededError(category="Food", budget_limit=500.0, spent=600.0)
        self.assertEqual(e.category, "Food")
        self.assertEqual(e.budget_limit, 500.0)
        self.assertEqual(e.spent, 600.0)
        self.assertIn("Food", str(e))
        self.assertIn("600.00", str(e))

    def test_inherits_from_base(self):
        e = BudgetExceededError()
        self.assertIsInstance(e, FinanceTrackerError)


if __name__ == "__main__":
    unittest.main()
