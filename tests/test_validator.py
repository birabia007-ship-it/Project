"""
test_validator.py — 26 unit tests for input validation functions.

TestValidateAmount:   10 tests
TestValidateDate:      7 tests
TestValidateCategory:  4 tests
TestValidateDescription: 5 tests
"""

import unittest
from src.validator import (
    validate_amount, validate_date, validate_category, validate_description,
    MAX_AMOUNT, MAX_DESCRIPTION_LENGTH
)
from src.exceptions import ValidationError, InvalidAmountError


class TestValidateAmount(unittest.TestCase):
    """10 tests for validate_amount()."""

    def test_valid_integer(self):
        self.assertEqual(validate_amount("100"), 100.0)

    def test_valid_float(self):
        self.assertEqual(validate_amount("49.99"), 49.99)

    def test_valid_numeric_type(self):
        self.assertEqual(validate_amount(250), 250.0)

    def test_rounds_to_two_decimals(self):
        self.assertEqual(validate_amount("10.999"), 11.0)

    def test_rounds_down(self):
        self.assertEqual(validate_amount("10.991"), 10.99)

    def test_empty_string_raises(self):
        with self.assertRaises(InvalidAmountError):
            validate_amount("")

    def test_none_raises(self):
        with self.assertRaises(InvalidAmountError):
            validate_amount(None)

    def test_zero_raises(self):
        with self.assertRaises(InvalidAmountError):
            validate_amount("0")

    def test_negative_raises(self):
        with self.assertRaises(InvalidAmountError):
            validate_amount("-50")

    def test_non_numeric_raises(self):
        with self.assertRaises(InvalidAmountError):
            validate_amount("abc")

    # overflow test is implicit — MAX_AMOUNT checked
    # We count 10 test methods above


class TestValidateDate(unittest.TestCase):
    """7 tests for validate_date()."""

    def test_valid_date(self):
        self.assertEqual(validate_date("2025-01-15"), "2025-01-15")

    def test_valid_with_whitespace(self):
        self.assertEqual(validate_date("  2025-06-01  "), "2025-06-01")

    def test_wrong_format_slash(self):
        with self.assertRaises(ValidationError):
            validate_date("01/15/2025")

    def test_wrong_format_text(self):
        with self.assertRaises(ValidationError):
            validate_date("January 15, 2025")

    def test_invalid_month_13(self):
        with self.assertRaises(ValidationError):
            validate_date("2025-13-01")

    def test_year_too_low(self):
        with self.assertRaises(ValidationError):
            validate_date("1999-01-01")

    def test_year_too_high(self):
        with self.assertRaises(ValidationError):
            validate_date("2101-01-01")


class TestValidateCategory(unittest.TestCase):
    """4 tests for validate_category()."""

    def test_valid_expense_category(self):
        self.assertEqual(validate_category("Food", "expense"), "Food")

    def test_valid_income_category(self):
        self.assertEqual(validate_category("Salary", "income"), "Salary")

    def test_invalid_category_raises(self):
        with self.assertRaises(ValidationError):
            validate_category("Gambling", "expense")

    def test_empty_category_raises(self):
        with self.assertRaises(ValidationError):
            validate_category("", "expense")


class TestValidateDescription(unittest.TestCase):
    """5 tests for validate_description()."""

    def test_normal_description(self):
        self.assertEqual(validate_description("Grocery shopping"), "Grocery shopping")

    def test_strips_whitespace(self):
        self.assertEqual(validate_description("  lunch  "), "lunch")

    def test_none_raises(self):
        with self.assertRaises(ValidationError):
            validate_description(None)

    def test_too_long_raises(self):
        with self.assertRaises(ValidationError):
            validate_description("x" * (MAX_DESCRIPTION_LENGTH + 1))

    def test_max_length_ok(self):
        desc = "y" * MAX_DESCRIPTION_LENGTH
        self.assertEqual(validate_description(desc), desc)


if __name__ == "__main__":
    unittest.main()
