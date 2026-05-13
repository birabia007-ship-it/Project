"""
transaction_view.py — Transaction management view.

Provides a form to add transactions, a searchable/filterable Treeview list,
and delete functionality. Income rows are green-tinted, expense rows are red-tinted.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from src.validator import (
    validate_amount, validate_date, validate_category, validate_description,
    CATEGORIES_INCOME, CATEGORIES_EXPENSE, TRANSACTION_TYPES
)
from src.exceptions import ValidationError, TransactionNotFoundError


class TransactionView(ttk.Frame):
    """Tab view for adding, viewing, searching, and deleting transactions."""

    COLOR_INCOME = "#00b894"
    COLOR_EXPENSE = "#e94560"
    COLOR_ACCENT = "#00cec9"
    COLOR_BUTTON = "#6c5ce7"
    COLOR_DELETE = "#d63031"
    BG_INPUT = "#0f3460"
    FG_TEXT = "#eeeeee"
    FG_SECONDARY = "#aaaaaa"

    def __init__(self, parent, db_manager):
        super().__init__(parent)
        self.db = db_manager
        self.configure(style="Dark.TFrame")
        self._build_ui()
        self._load_transactions()

    def _build_ui(self):
        main_frame = ttk.Frame(self, style="Dark.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        left = ttk.Frame(main_frame, style="Card.TFrame")
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        right = ttk.Frame(main_frame, style="Dark.TFrame")
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_form(left)
        self._build_search_bar(right)
        self._build_table(right)
        self._build_action_bar(right)

    def _build_form(self, parent):
        title = ttk.Label(parent, text="  Add Transaction", style="CardTitle.TLabel")
        title.pack(pady=(15, 10), padx=20, anchor=tk.W)

        form = ttk.Frame(parent, style="Card.TFrame")
        form.pack(padx=20, pady=(0, 10), fill=tk.X)

        ttk.Label(form, text="Type", style="Label.TLabel").pack(anchor=tk.W, pady=(5, 2))
        self.type_var = tk.StringVar(value="expense")
        type_frame = ttk.Frame(form, style="Card.TFrame")
        type_frame.pack(fill=tk.X, pady=(0, 5))
        for t in TRANSACTION_TYPES:
            ttk.Radiobutton(
                type_frame, text=t.capitalize(), value=t,
                variable=self.type_var, style="Dark.TRadiobutton",
                command=self._on_type_change
            ).pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(form, text="Category", style="Label.TLabel").pack(anchor=tk.W, pady=(5, 2))
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(form, textvariable=self.category_var, state="readonly", width=25)
        self.category_combo.pack(fill=tk.X, pady=(0, 5))
        self._update_categories()

        ttk.Label(form, text="Amount ($)", style="Label.TLabel").pack(anchor=tk.W, pady=(5, 2))
        self.amount_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.amount_var, width=25).pack(fill=tk.X, pady=(0, 5))

        ttk.Label(form, text="Date (YYYY-MM-DD)", style="Label.TLabel").pack(anchor=tk.W, pady=(5, 2))
        self.date_var = tk.StringVar(value=date.today().isoformat())
        ttk.Entry(form, textvariable=self.date_var, width=25).pack(fill=tk.X, pady=(0, 5))

        ttk.Label(form, text="Description", style="Label.TLabel").pack(anchor=tk.W, pady=(5, 2))
        self.desc_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.desc_var, width=25).pack(fill=tk.X, pady=(0, 10))

        submit_btn = tk.Button(
            form, text="Add Transaction", bg=self.COLOR_BUTTON, fg="white",
            font=("Segoe UI", 10, "bold"), relief=tk.FLAT, cursor="hand2",
            activebackground="#5b4bd5", padx=15, pady=8, command=self._add_transaction
        )
        submit_btn.pack(fill=tk.X, pady=(5, 15))

    def _build_search_bar(self, parent):
        bar = ttk.Frame(parent, style="Card.TFrame")
        bar.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(bar, text="Search:", style="Label.TLabel").pack(side=tk.LEFT, padx=(10, 5))
        self.search_var = tk.StringVar()
        e = ttk.Entry(bar, textvariable=self.search_var, width=18)
        e.pack(side=tk.LEFT, padx=(0, 10), pady=8)
        e.bind("<KeyRelease>", lambda ev: self._filter_transactions())

        ttk.Label(bar, text="Type:", style="Label.TLabel").pack(side=tk.LEFT, padx=(5, 3))
        self.filter_type_var = tk.StringVar(value="All")
        ft = ttk.Combobox(bar, textvariable=self.filter_type_var, state="readonly", width=10, values=["All", "income", "expense"])
        ft.pack(side=tk.LEFT, padx=(0, 10), pady=8)
        ft.bind("<<ComboboxSelected>>", lambda ev: self._filter_transactions())

        ttk.Label(bar, text="Category:", style="Label.TLabel").pack(side=tk.LEFT, padx=(5, 3))
        self.filter_cat_var = tk.StringVar(value="All")
        all_cats = ["All"] + CATEGORIES_INCOME + [c for c in CATEGORIES_EXPENSE if c not in CATEGORIES_INCOME]
        self.cat_filter_combo = ttk.Combobox(bar, textvariable=self.filter_cat_var, state="readonly", width=14, values=all_cats)
        self.cat_filter_combo.pack(side=tk.LEFT, padx=(0, 10), pady=8)
        self.cat_filter_combo.bind("<<ComboboxSelected>>", lambda ev: self._filter_transactions())

        ttk.Label(bar, text="From:", style="Label.TLabel").pack(side=tk.LEFT, padx=(5, 3))
        self.date_from_var = tk.StringVar()
        ttk.Entry(bar, textvariable=self.date_from_var, width=11).pack(side=tk.LEFT, padx=(0, 5), pady=8)

        ttk.Label(bar, text="To:", style="Label.TLabel").pack(side=tk.LEFT, padx=(5, 3))
        self.date_to_var = tk.StringVar()
        ttk.Entry(bar, textvariable=self.date_to_var, width=11).pack(side=tk.LEFT, padx=(0, 5), pady=8)

        tk.Button(bar, text="Search", bg=self.COLOR_ACCENT, fg="#1a1a2e", font=("Segoe UI", 9, "bold"),
                  relief=tk.FLAT, cursor="hand2", padx=10, pady=3, command=self._filter_transactions).pack(side=tk.LEFT, padx=(10, 5), pady=8)
        tk.Button(bar, text="Reset", bg=self.FG_SECONDARY, fg="#1a1a2e", font=("Segoe UI", 9),
                  relief=tk.FLAT, cursor="hand2", padx=10, pady=3, command=self._reset_filters).pack(side=tk.LEFT, pady=8)

    def _build_table(self, parent):
        columns = ("id", "type", "category", "amount", "date", "description")
        self.tree = ttk.Treeview(parent, columns=columns, show="headings", selectmode="browse", style="Dark.Treeview")
        headings = {"id": ("ID", 50), "type": ("Type", 80), "category": ("Category", 120),
                    "amount": ("Amount ($)", 100), "date": ("Date", 100), "description": ("Description", 250)}
        for col, (text, width) in headings.items():
            self.tree.heading(col, text=text, anchor=tk.W)
            self.tree.column(col, width=width, minwidth=40)

        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.tag_configure("income", foreground=self.COLOR_INCOME)
        self.tree.tag_configure("expense", foreground=self.COLOR_EXPENSE)

    def _build_action_bar(self, parent):
        bar = ttk.Frame(parent, style="Card.TFrame")
        bar.pack(fill=tk.X, pady=(5, 0))
        self.count_label = ttk.Label(bar, text="0 records", style="Secondary.TLabel")
        self.count_label.pack(side=tk.LEFT, padx=10, pady=8)

        tk.Button(bar, text="Delete Selected", bg=self.COLOR_DELETE, fg="white",
                  font=("Segoe UI", 9, "bold"), relief=tk.FLAT, cursor="hand2",
                  padx=12, pady=5, command=self._delete_selected).pack(side=tk.RIGHT, padx=10, pady=8)
        tk.Button(bar, text="Refresh", bg=self.BG_INPUT, fg=self.FG_TEXT,
                  font=("Segoe UI", 9), relief=tk.FLAT, cursor="hand2",
                  padx=12, pady=5, command=self._load_transactions).pack(side=tk.RIGHT, padx=(0, 5), pady=8)

    # ── Event Handlers ───────────────────────────────────────────────────────

    def _on_type_change(self):
        self._update_categories()

    def _update_categories(self):
        txn_type = self.type_var.get()
        cats = CATEGORIES_INCOME if txn_type == "income" else CATEGORIES_EXPENSE
        self.category_combo["values"] = cats
        if cats:
            self.category_var.set(cats[0])

    def _add_transaction(self):
        try:
            txn_type = self.type_var.get()
            amount = validate_amount(self.amount_var.get())
            txn_date = validate_date(self.date_var.get())
            category = validate_category(self.category_var.get(), txn_type)
            desc_raw = self.desc_var.get().strip()
            description = validate_description(desc_raw) if desc_raw else ""

            self.db.add_transaction(txn_type, category, amount, txn_date, description)
            self.amount_var.set("")
            self.desc_var.set("")
            self.date_var.set(date.today().isoformat())
            self._load_transactions()
            messagebox.showinfo("Success", f"{txn_type.capitalize()} of ${amount:.2f} added!")
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _load_transactions(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            transactions = self.db.get_all_transactions()
            for txn in transactions:
                self.tree.insert("", tk.END, values=(
                    txn["id"], txn["type"].capitalize(), txn["category"],
                    f"{txn['amount']:.2f}", txn["date"], txn["description"]
                ), tags=(txn["type"],))
            self.count_label.config(text=f"{len(transactions)} records")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _filter_transactions(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            keyword = self.search_var.get().strip() or None
            tf = self.filter_type_var.get()
            type_filter = tf if tf != "All" else None
            cf = self.filter_cat_var.get()
            cat_filter = cf if cf != "All" else None
            date_from = self.date_from_var.get().strip() or None
            date_to = self.date_to_var.get().strip() or None

            transactions = self.db.search_transactions(
                keyword=keyword, type_filter=type_filter,
                category_filter=cat_filter, date_from=date_from, date_to=date_to
            )
            for txn in transactions:
                self.tree.insert("", tk.END, values=(
                    txn["id"], txn["type"].capitalize(), txn["category"],
                    f"{txn['amount']:.2f}", txn["date"], txn["description"]
                ), tags=(txn["type"],))
            self.count_label.config(text=f"{len(transactions)} records")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _reset_filters(self):
        self.search_var.set("")
        self.filter_type_var.set("All")
        self.filter_cat_var.set("All")
        self.date_from_var.set("")
        self.date_to_var.set("")
        self._load_transactions()

    def _delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a transaction to delete.")
            return
        item = self.tree.item(selected[0])
        txn_id = item["values"][0]
        if not messagebox.askyesno("Confirm Delete", f"Delete transaction #{txn_id}?"):
            return
        try:
            self.db.delete_transaction(txn_id)
            self._load_transactions()
            messagebox.showinfo("Deleted", f"Transaction #{txn_id} deleted.")
        except TransactionNotFoundError as e:
            messagebox.showerror("Not Found", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))
