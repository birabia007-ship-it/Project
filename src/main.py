"""
main.py — Application entry point for Personal Finance Tracker.

Creates the root Tk window with tabbed navigation (Transactions, Dashboard, Budgets),
initializes the database, and manages clean shutdown.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import DatabaseManager
from src.views.transaction_view import TransactionView
from src.views.dashboard_view import DashboardView
from src.views.budget_view import BudgetView


class FinanceTrackerApp:
    """Main application class for Personal Finance Tracker."""

    # ── Theme Colors ─────────────────────────────────────────────────────────
    BG_DARK = "#1a1a2e"
    BG_CARD = "#16213e"
    BG_INPUT = "#0f3460"
    FG_TEXT = "#eeeeee"
    FG_SECONDARY = "#aaaaaa"
    COLOR_ACCENT = "#00cec9"

    def __init__(self):
        """Initialize the application."""
        self.root = tk.Tk()
        self.root.title("Personal Finance Tracker")
        self.root.geometry("1200x700")
        self.root.minsize(900, 550)
        self.root.configure(bg=self.BG_DARK)

        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 600
        y = (self.root.winfo_screenheight() // 2) - 350
        self.root.geometry(f"+{x}+{y}")

        # Initialize database
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "finance_tracker.db"
        )
        self.db = DatabaseManager(db_path)

        # Setup styles and UI
        self._configure_styles()
        self._build_ui()

        # Clean shutdown
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _configure_styles(self):
        """Configure ttk styles for the dark theme."""
        style = ttk.Style()
        style.theme_use("clam")

        # Frame styles
        style.configure("Dark.TFrame", background=self.BG_DARK)
        style.configure("Card.TFrame", background=self.BG_CARD)

        # Label styles
        style.configure("Label.TLabel", background=self.BG_CARD,
                        foreground=self.FG_TEXT, font=("Segoe UI", 10))
        style.configure("CardTitle.TLabel", background=self.BG_CARD,
                        foreground=self.COLOR_ACCENT, font=("Segoe UI", 13, "bold"))
        style.configure("Secondary.TLabel", background=self.BG_CARD,
                        foreground=self.FG_SECONDARY, font=("Segoe UI", 9))

        # Notebook (tabs) style
        style.configure("TNotebook", background=self.BG_DARK, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.BG_INPUT,
                        foreground=self.FG_TEXT, font=("Segoe UI", 11, "bold"),
                        padding=[20, 8])
        style.map("TNotebook.Tab",
                  background=[("selected", self.BG_CARD)],
                  foreground=[("selected", self.COLOR_ACCENT)])

        # Treeview style
        style.configure("Dark.Treeview", background=self.BG_CARD,
                        foreground=self.FG_TEXT, fieldbackground=self.BG_CARD,
                        font=("Segoe UI", 10), rowheight=28)
        style.configure("Dark.Treeview.Heading", background=self.BG_INPUT,
                        foreground=self.COLOR_ACCENT, font=("Segoe UI", 10, "bold"))
        style.map("Dark.Treeview", background=[("selected", self.BG_INPUT)])

        # Entry style
        style.configure("TEntry", fieldbackground=self.BG_INPUT,
                        foreground=self.FG_TEXT, insertcolor=self.FG_TEXT)

        # Combobox style
        style.configure("TCombobox", fieldbackground=self.BG_INPUT,
                        foreground=self.FG_TEXT, selectbackground=self.BG_INPUT,
                        selectforeground=self.FG_TEXT)

        # Radiobutton style
        style.configure("Dark.TRadiobutton", background=self.BG_CARD,
                        foreground=self.FG_TEXT, font=("Segoe UI", 10))

        # Scrollbar style
        style.configure("TScrollbar", background=self.BG_INPUT,
                        troughcolor=self.BG_DARK, arrowcolor=self.FG_TEXT)

    def _build_ui(self):
        """Build the main application layout with tabbed navigation."""
        # Header
        header = tk.Frame(self.root, bg=self.BG_CARD, height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="💰 Personal Finance Tracker", bg=self.BG_CARD,
                 fg=self.COLOR_ACCENT, font=("Segoe UI", 16, "bold")).pack(
            side=tk.LEFT, padx=20, pady=10)

        tk.Label(header, text="Track • Budget • Visualize", bg=self.BG_CARD,
                 fg=self.FG_SECONDARY, font=("Segoe UI", 10)).pack(
            side=tk.RIGHT, padx=20, pady=10)

        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create views
        self.transaction_view = TransactionView(self.notebook, self.db)
        self.dashboard_view = DashboardView(self.notebook, self.db)
        self.budget_view = BudgetView(self.notebook, self.db)

        # Add tabs
        self.notebook.add(self.transaction_view, text="  Transactions  ")
        self.notebook.add(self.dashboard_view, text="  Dashboard  ")
        self.notebook.add(self.budget_view, text="  Budgets  ")

        # Refresh dashboard/budget when switching tabs
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_change)

    def _on_tab_change(self, event):
        """Refresh view data when switching tabs."""
        tab_index = self.notebook.index(self.notebook.select())
        if tab_index == 1:
            self.dashboard_view.refresh()
        elif tab_index == 2:
            self.budget_view.refresh()

    def _on_close(self):
        """Clean shutdown: close database and destroy window."""
        self.db.close()
        self.root.destroy()

    def run(self):
        """Start the application main loop."""
        self.root.mainloop()


if __name__ == "__main__":
    app = FinanceTrackerApp()
    app.run()
