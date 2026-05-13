"""
test_database.py — 16 unit tests for DatabaseManager.

Uses in-memory SQLite (':memory:') for test isolation.
Tests: add, get, delete transactions; summary; budgets; monthly trend.
"""

import unittest
from src.database import DatabaseManager
from src.exceptions import DatabaseError, TransactionNotFoundError


class TestDatabaseManager(unittest.TestCase):
    """16 tests for DatabaseManager CRUD, summary, budget, and trend methods."""

    def setUp(self):
        """Create a fresh in-memory database for each test."""
        self.db = DatabaseManager(":memory:")

    def tearDown(self):
        """Close the database after each test."""
        self.db.close()

    # ── Transaction CRUD (6 tests) ───────────────────────────────────────────

    def test_add_transaction_returns_id(self):
        tid = self.db.add_transaction("expense", "Food", 25.50, "2025-05-01", "Lunch")
        self.assertIsInstance(tid, int)
        self.assertGreater(tid, 0)

    def test_get_all_transactions_empty(self):
        result = self.db.get_all_transactions()
        self.assertEqual(result, [])

    def test_get_all_transactions_returns_added(self):
        self.db.add_transaction("income", "Salary", 3000.00, "2025-05-01", "Monthly salary")
        self.db.add_transaction("expense", "Food", 50.00, "2025-05-02", "Groceries")
        result = self.db.get_all_transactions()
        self.assertEqual(len(result), 2)

    def test_get_transaction_by_id(self):
        tid = self.db.add_transaction("expense", "Transport", 15.00, "2025-05-01", "Bus")
        txn = self.db.get_transaction_by_id(tid)
        self.assertEqual(txn["category"], "Transport")
        self.assertEqual(txn["amount"], 15.00)

    def test_get_transaction_by_id_not_found(self):
        with self.assertRaises(TransactionNotFoundError):
            self.db.get_transaction_by_id(9999)

    def test_delete_transaction(self):
        tid = self.db.add_transaction("expense", "Food", 10.00, "2025-05-01", "Snack")
        self.assertTrue(self.db.delete_transaction(tid))
        with self.assertRaises(TransactionNotFoundError):
            self.db.get_transaction_by_id(tid)

    # ── Delete edge case (1 test) ────────────────────────────────────────────

    def test_delete_nonexistent_raises(self):
        with self.assertRaises(TransactionNotFoundError):
            self.db.delete_transaction(9999)

    # ── Search (2 tests) ─────────────────────────────────────────────────────

    def test_search_by_keyword(self):
        self.db.add_transaction("expense", "Food", 30.00, "2025-05-01", "Pizza dinner")
        self.db.add_transaction("expense", "Food", 20.00, "2025-05-02", "Burger lunch")
        results = self.db.search_transactions(keyword="Pizza")
        self.assertEqual(len(results), 1)
        self.assertIn("Pizza", results[0]["description"])

    def test_search_by_type(self):
        self.db.add_transaction("income", "Salary", 3000.00, "2025-05-01", "Pay")
        self.db.add_transaction("expense", "Food", 50.00, "2025-05-02", "Lunch")
        results = self.db.search_transactions(type_filter="income")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["type"], "income")

    # ── Summary (2 tests) ────────────────────────────────────────────────────

    def test_summary_totals(self):
        self.db.add_transaction("income", "Salary", 5000.00, "2025-05-01", "Pay")
        self.db.add_transaction("expense", "Food", 200.00, "2025-05-05", "Groceries")
        self.db.add_transaction("expense", "Transport", 100.00, "2025-05-10", "Gas")
        summary = self.db.get_summary(5, 2025)
        self.assertEqual(summary["total_income"], 5000.00)
        self.assertEqual(summary["total_expense"], 300.00)
        self.assertEqual(summary["net"], 4700.00)

    def test_summary_empty_month(self):
        summary = self.db.get_summary(1, 2025)
        self.assertEqual(summary["total_income"], 0.0)
        self.assertEqual(summary["total_expense"], 0.0)
        self.assertEqual(summary["net"], 0.0)

    # ── Category breakdown (1 test) ──────────────────────────────────────────

    def test_category_breakdown(self):
        self.db.add_transaction("expense", "Food", 100.00, "2025-05-01", "Groceries")
        self.db.add_transaction("expense", "Food", 50.00, "2025-05-02", "Lunch")
        self.db.add_transaction("expense", "Transport", 30.00, "2025-05-03", "Bus")
        breakdown = self.db.get_category_breakdown(5, 2025, "expense")
        self.assertEqual(len(breakdown), 2)
        self.assertEqual(breakdown[0]["category"], "Food")
        self.assertEqual(breakdown[0]["total"], 150.00)

    # ── Monthly trend (1 test) ───────────────────────────────────────────────

    def test_monthly_trend(self):
        self.db.add_transaction("income", "Salary", 5000.00, "2025-01-01", "Jan pay")
        self.db.add_transaction("expense", "Food", 200.00, "2025-01-15", "Food")
        trend = self.db.get_monthly_trend(2025)
        self.assertEqual(len(trend), 12)
        self.assertEqual(trend[0]["month"], 1)
        self.assertEqual(trend[0]["income"], 5000.00)
        self.assertEqual(trend[0]["expense"], 200.00)
        self.assertEqual(trend[1]["income"], 0.0)

    # ── Budget (3 tests) ─────────────────────────────────────────────────────

    def test_set_and_get_budget(self):
        self.db.set_budget("Food", 500.00, 5, 2025)
        budget = self.db.get_budget("Food", 5, 2025)
        self.assertIsNotNone(budget)
        self.assertEqual(budget["category"], "Food")
        self.assertEqual(budget["amount"], 500.00)

    def test_get_budget_not_set(self):
        budget = self.db.get_budget("Food", 1, 2025)
        self.assertIsNone(budget)

    def test_get_all_budgets(self):
        self.db.set_budget("Food", 500.00, 5, 2025)
        self.db.set_budget("Transport", 200.00, 5, 2025)
        budgets = self.db.get_all_budgets(5, 2025)
        self.assertEqual(len(budgets), 2)


if __name__ == "__main__":
    unittest.main()
