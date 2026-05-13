"""
budget_view.py — Budget management view.

Set monthly budgets per expense category, view spending progress with
color-coded progress bars, and get alerts when approaching/exceeding limits.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from src.validator import validate_amount, CATEGORIES_EXPENSE
from src.exceptions import ValidationError


class BudgetView(ttk.Frame):
    """Tab view for setting and monitoring monthly budgets."""

    COLOR_SAFE = "#00b894"
    COLOR_WARN = "#fdcb6e"
    COLOR_DANGER = "#e94560"
    COLOR_BUTTON = "#6c5ce7"
    BG_CARD = "#16213e"
    BG_DARK = "#1a1a2e"
    BG_INPUT = "#0f3460"
    FG_TEXT = "#eeeeee"
    FG_SECONDARY = "#aaaaaa"

    MONTH_NAMES = [
        "", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db = db_manager
        self.configure(style="Dark.TFrame")
        today = date.today()
        self.selected_month = tk.IntVar(value=today.month)
        self.selected_year = tk.IntVar(value=today.year)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        main = ttk.Frame(self, style="Dark.TFrame")
        main.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Left panel: Set budget form
        left = ttk.Frame(main, style="Card.TFrame")
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self._build_form(left)

        # Right panel: Budget overview
        right = ttk.Frame(main, style="Dark.TFrame")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._build_overview(right)

    def _build_form(self, parent):
        ttk.Label(parent, text="  Set Budget", style="CardTitle.TLabel").pack(pady=(15, 10), padx=20, anchor=tk.W)

        form = ttk.Frame(parent, style="Card.TFrame")
        form.pack(padx=20, pady=(0, 10), fill=tk.X)

        # Month/Year
        ttk.Label(form, text="Month", style="Label.TLabel").pack(anchor=tk.W, pady=(5, 2))
        month_frame = ttk.Frame(form, style="Card.TFrame")
        month_frame.pack(fill=tk.X, pady=(0, 5))

        self.month_combo = ttk.Combobox(month_frame, textvariable=self.selected_month,
                                         state="readonly", width=5, values=list(range(1, 13)))
        self.month_combo.pack(side=tk.LEFT, padx=(0, 5))

        ttk.Label(month_frame, text="Year:", style="Label.TLabel").pack(side=tk.LEFT, padx=(5, 3))
        self.year_entry = ttk.Entry(month_frame, textvariable=self.selected_year, width=8)
        self.year_entry.pack(side=tk.LEFT)

        # Category
        ttk.Label(form, text="Category", style="Label.TLabel").pack(anchor=tk.W, pady=(5, 2))
        self.cat_var = tk.StringVar(value=CATEGORIES_EXPENSE[0])
        ttk.Combobox(form, textvariable=self.cat_var, state="readonly", width=25,
                     values=CATEGORIES_EXPENSE).pack(fill=tk.X, pady=(0, 5))

        # Budget amount
        ttk.Label(form, text="Budget Amount ($)", style="Label.TLabel").pack(anchor=tk.W, pady=(5, 2))
        self.budget_amount_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.budget_amount_var, width=25).pack(fill=tk.X, pady=(0, 10))

        # Submit
        tk.Button(form, text="Set Budget", bg=self.COLOR_BUTTON, fg="white",
                  font=("Segoe UI", 10, "bold"), relief=tk.FLAT, cursor="hand2",
                  activebackground="#5b4bd5", padx=15, pady=8,
                  command=self._set_budget).pack(fill=tk.X, pady=(5, 15))

        # Quick-set all
        ttk.Label(parent, text="Quick Set All Categories", style="CardTitle.TLabel").pack(
            pady=(10, 5), padx=20, anchor=tk.W)
        quick_frame = ttk.Frame(parent, style="Card.TFrame")
        quick_frame.pack(padx=20, fill=tk.X)

        ttk.Label(quick_frame, text="Amount ($):", style="Label.TLabel").pack(side=tk.LEFT, pady=8, padx=(0, 5))
        self.quick_amount_var = tk.StringVar()
        ttk.Entry(quick_frame, textvariable=self.quick_amount_var, width=12).pack(side=tk.LEFT, padx=(0, 10), pady=8)
        tk.Button(quick_frame, text="Set All", bg="#0f3460", fg="#eee",
                  font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, pady=3,
                  command=self._set_all_budgets).pack(side=tk.LEFT, pady=8)

    def _build_overview(self, parent):
        # Header with navigation
        header = ttk.Frame(parent, style="Card.TFrame")
        header.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(header, text="Budget Overview", style="CardTitle.TLabel").pack(side=tk.LEFT, padx=10, pady=8)

        nav = ttk.Frame(header, style="Card.TFrame")
        nav.pack(side=tk.RIGHT, padx=10, pady=8)
        tk.Button(nav, text="<", bg="#0f3460", fg="#eee", font=("Segoe UI", 10, "bold"),
                  relief=tk.FLAT, width=3, command=self._prev_month).pack(side=tk.LEFT, padx=2)
        self.nav_label = ttk.Label(nav, text="", style="Label.TLabel", width=20, anchor=tk.CENTER)
        self.nav_label.pack(side=tk.LEFT, padx=5)
        tk.Button(nav, text=">", bg="#0f3460", fg="#eee", font=("Segoe UI", 10, "bold"),
                  relief=tk.FLAT, width=3, command=self._next_month).pack(side=tk.LEFT, padx=2)
        tk.Button(nav, text="Refresh", bg="#00cec9", fg="#1a1a2e", font=("Segoe UI", 9, "bold"),
                  relief=tk.FLAT, padx=10, pady=2, command=self.refresh).pack(side=tk.LEFT, padx=(15, 0))

        # Budget cards container with scrollbar
        container = ttk.Frame(parent, style="Dark.TFrame")
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container, bg=self.BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        self.budget_frame = ttk.Frame(canvas, style="Dark.TFrame")

        self.budget_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.budget_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _create_budget_card(self, parent, category, budget_amount, spent):
        """Create a single budget category card with progress bar."""
        card = tk.Frame(parent, bg=self.BG_CARD, padx=15, pady=10)
        card.pack(fill=tk.X, pady=3)

        remaining = budget_amount - spent
        pct = (spent / budget_amount * 100) if budget_amount > 0 else 0

        if pct >= 100:
            color = self.COLOR_DANGER
            status = "EXCEEDED"
        elif pct >= 80:
            color = self.COLOR_WARN
            status = "WARNING"
        else:
            color = self.COLOR_SAFE
            status = "OK"

        # Top row: category name and status
        top = tk.Frame(card, bg=self.BG_CARD)
        top.pack(fill=tk.X)
        tk.Label(top, text=category, bg=self.BG_CARD, fg=self.FG_TEXT,
                 font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)
        tk.Label(top, text=status, bg=self.BG_CARD, fg=color,
                 font=("Segoe UI", 9, "bold")).pack(side=tk.RIGHT)

        # Progress bar (canvas-based)
        bar_h = 16
        bar_canvas = tk.Canvas(card, bg=self.BG_CARD, height=bar_h, highlightthickness=0)
        bar_canvas.pack(fill=tk.X, pady=(5, 3))
        bar_canvas.update_idletasks()
        bw = bar_canvas.winfo_width() or 400

        # Background
        bar_canvas.create_rectangle(0, 0, bw, bar_h, fill="#2d3436", outline="")
        # Fill
        fill_w = min(pct / 100, 1.0) * bw
        bar_canvas.create_rectangle(0, 0, fill_w, bar_h, fill=color, outline="")
        # Percentage text
        bar_canvas.create_text(bw // 2, bar_h // 2, text=f"{pct:.0f}%",
                               fill="white", font=("Segoe UI", 8, "bold"))

        # Bottom row: amounts
        bottom = tk.Frame(card, bg=self.BG_CARD)
        bottom.pack(fill=tk.X)
        tk.Label(bottom, text=f"Spent: ${spent:,.2f}", bg=self.BG_CARD,
                 fg=self.FG_SECONDARY, font=("Segoe UI", 9)).pack(side=tk.LEFT)
        tk.Label(bottom, text=f"Budget: ${budget_amount:,.2f}", bg=self.BG_CARD,
                 fg=self.FG_SECONDARY, font=("Segoe UI", 9)).pack(side=tk.RIGHT)
        rem_color = self.COLOR_SAFE if remaining >= 0 else self.COLOR_DANGER
        tk.Label(bottom, text=f"Remaining: ${remaining:,.2f}", bg=self.BG_CARD,
                 fg=rem_color, font=("Segoe UI", 9)).pack(side=tk.RIGHT, padx=(0, 20))

    def refresh(self):
        """Refresh the budget overview."""
        month = self.selected_month.get()
        year = self.selected_year.get()
        self.nav_label.config(text=f"{self.MONTH_NAMES[month]} {year}")

        # Clear existing cards
        for w in self.budget_frame.winfo_children():
            w.destroy()

        try:
            budgets = self.db.get_all_budgets(month, year)
            breakdown = self.db.get_category_breakdown(month, year, "expense")
            spent_map = {item["category"]: item["total"] for item in breakdown}

            if not budgets:
                ttk.Label(self.budget_frame, text="No budgets set for this month.\nUse the form to set budgets.",
                          style="Secondary.TLabel").pack(pady=50)
                return

            alerts = []
            for b in budgets:
                cat = b["category"]
                spent = spent_map.get(cat, 0.0)
                self._create_budget_card(self.budget_frame, cat, b["amount"], spent)
                pct = (spent / b["amount"] * 100) if b["amount"] > 0 else 0
                if pct >= 100:
                    alerts.append(f"  {cat}: EXCEEDED (${spent:,.2f} / ${b['amount']:,.2f})")
                elif pct >= 80:
                    alerts.append(f"  {cat}: WARNING at {pct:.0f}%")

            if alerts:
                messagebox.showwarning("Budget Alerts", "The following categories need attention:\n\n" + "\n".join(alerts))

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _set_budget(self):
        try:
            amount = validate_amount(self.budget_amount_var.get())
            category = self.cat_var.get()
            month = self.selected_month.get()
            year = self.selected_year.get()

            self.db.set_budget(category, amount, month, year)
            self.budget_amount_var.set("")
            self.refresh()
            messagebox.showinfo("Success", f"Budget set: {category} = ${amount:,.2f} for {self.MONTH_NAMES[month]} {year}")
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _set_all_budgets(self):
        try:
            amount = validate_amount(self.quick_amount_var.get())
            month = self.selected_month.get()
            year = self.selected_year.get()

            for cat in CATEGORIES_EXPENSE:
                self.db.set_budget(cat, amount, month, year)

            self.quick_amount_var.set("")
            self.refresh()
            messagebox.showinfo("Success", f"All budgets set to ${amount:,.2f} for {self.MONTH_NAMES[month]} {year}")
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _prev_month(self):
        m = self.selected_month.get() - 1
        y = self.selected_year.get()
        if m < 1:
            m, y = 12, y - 1
        self.selected_month.set(m)
        self.selected_year.set(y)
        self.refresh()

    def _next_month(self):
        m = self.selected_month.get() + 1
        y = self.selected_year.get()
        if m > 12:
            m, y = 1, y + 1
        self.selected_month.set(m)
        self.selected_year.set(y)
        self.refresh()
