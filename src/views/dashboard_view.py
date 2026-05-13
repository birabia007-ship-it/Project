"""
dashboard_view.py — Dashboard with pie chart, bar chart, and summary cards.

All charts are drawn using tkinter.Canvas — no external dependencies.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import math


class DashboardView(ttk.Frame):
    """Tab view for financial dashboard with charts and summary."""

    COLORS_PIE = [
        "#e94560", "#00b894", "#6c5ce7", "#fdcb6e", "#00cec9",
        "#e17055", "#a29bfe", "#55efc4", "#fab1a0", "#74b9ff",
    ]
    COLOR_INCOME = "#00b894"
    COLOR_EXPENSE = "#e94560"
    COLOR_NET_POS = "#00b894"
    COLOR_NET_NEG = "#e94560"
    BG_DARK = "#1a1a2e"
    BG_CARD = "#16213e"
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
        # Month/Year selector
        sel_frame = ttk.Frame(self, style="Card.TFrame")
        sel_frame.pack(fill=tk.X, padx=15, pady=(10, 5))

        ttk.Label(sel_frame, text="Dashboard", style="CardTitle.TLabel").pack(side=tk.LEFT, padx=10, pady=8)

        # Navigation buttons
        nav = ttk.Frame(sel_frame, style="Card.TFrame")
        nav.pack(side=tk.RIGHT, padx=10, pady=8)

        tk.Button(nav, text="<", bg="#0f3460", fg="#eee", font=("Segoe UI", 10, "bold"),
                  relief=tk.FLAT, width=3, command=self._prev_month).pack(side=tk.LEFT, padx=2)
        self.month_label = ttk.Label(nav, text="", style="Label.TLabel", width=20, anchor=tk.CENTER)
        self.month_label.pack(side=tk.LEFT, padx=5)
        tk.Button(nav, text=">", bg="#0f3460", fg="#eee", font=("Segoe UI", 10, "bold"),
                  relief=tk.FLAT, width=3, command=self._next_month).pack(side=tk.LEFT, padx=2)

        tk.Button(nav, text="Refresh", bg="#00cec9", fg="#1a1a2e", font=("Segoe UI", 9, "bold"),
                  relief=tk.FLAT, padx=10, pady=2, command=self.refresh).pack(side=tk.LEFT, padx=(15, 0))

        # Summary cards row
        self.cards_frame = ttk.Frame(self, style="Dark.TFrame")
        self.cards_frame.pack(fill=tk.X, padx=15, pady=5)

        # Charts area
        charts_frame = ttk.Frame(self, style="Dark.TFrame")
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 10))

        # Pie chart (left)
        pie_container = ttk.Frame(charts_frame, style="Card.TFrame")
        pie_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        ttk.Label(pie_container, text="Expense Breakdown", style="CardTitle.TLabel").pack(pady=(10, 5))
        self.pie_canvas = tk.Canvas(pie_container, bg=self.BG_CARD, highlightthickness=0, height=320)
        self.pie_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Bar chart (right)
        bar_container = ttk.Frame(charts_frame, style="Card.TFrame")
        bar_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        ttk.Label(bar_container, text="Monthly Trend", style="CardTitle.TLabel").pack(pady=(10, 5))
        self.bar_canvas = tk.Canvas(bar_container, bg=self.BG_CARD, highlightthickness=0, height=320)
        self.bar_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def _create_summary_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg=self.BG_CARD, padx=20, pady=12)
        card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        tk.Label(card, text=title, bg=self.BG_CARD, fg=self.FG_SECONDARY,
                 font=("Segoe UI", 9)).pack(anchor=tk.W)
        tk.Label(card, text=value, bg=self.BG_CARD, fg=color,
                 font=("Segoe UI", 18, "bold")).pack(anchor=tk.W, pady=(2, 0))

    def refresh(self):
        """Refresh all dashboard data."""
        month = self.selected_month.get()
        year = self.selected_year.get()
        self.month_label.config(text=f"{self.MONTH_NAMES[month]} {year}")

        try:
            summary = self.db.get_summary(month, year)
            breakdown = self.db.get_category_breakdown(month, year, "expense")
            trend = self.db.get_monthly_trend(year)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        # Update summary cards
        for w in self.cards_frame.winfo_children():
            w.destroy()
        net_color = self.COLOR_NET_POS if summary["net"] >= 0 else self.COLOR_NET_NEG
        self._create_summary_card(self.cards_frame, "Total Income", f"${summary['total_income']:,.2f}", self.COLOR_INCOME)
        self._create_summary_card(self.cards_frame, "Total Expenses", f"${summary['total_expense']:,.2f}", self.COLOR_EXPENSE)
        self._create_summary_card(self.cards_frame, "Net Balance", f"${summary['net']:,.2f}", net_color)

        self._draw_pie_chart(breakdown)
        self._draw_bar_chart(trend, month)

    def _draw_pie_chart(self, breakdown):
        self.pie_canvas.delete("all")
        w = self.pie_canvas.winfo_width() or 400
        h = self.pie_canvas.winfo_height() or 300

        if not breakdown:
            self.pie_canvas.create_text(w // 2, h // 2, text="No expenses this month",
                                        fill=self.FG_SECONDARY, font=("Segoe UI", 12))
            return

        total = sum(item["total"] for item in breakdown)
        cx, cy = w // 2 - 60, h // 2
        radius = min(cx, cy, 120)
        start = 0

        for i, item in enumerate(breakdown):
            extent = (item["total"] / total) * 360 if total > 0 else 0
            color = self.COLORS_PIE[i % len(self.COLORS_PIE)]
            self.pie_canvas.create_arc(
                cx - radius, cy - radius, cx + radius, cy + radius,
                start=start, extent=extent, fill=color, outline=self.BG_CARD, width=2
            )
            start += extent

        # Legend
        lx = cx + radius + 30
        ly = cy - (len(breakdown) * 22) // 2
        for i, item in enumerate(breakdown):
            color = self.COLORS_PIE[i % len(self.COLORS_PIE)]
            pct = (item["total"] / total * 100) if total > 0 else 0
            self.pie_canvas.create_rectangle(lx, ly, lx + 14, ly + 14, fill=color, outline="")
            self.pie_canvas.create_text(
                lx + 20, ly + 7, anchor=tk.W,
                text=f"{item['category']}  ${item['total']:,.0f} ({pct:.0f}%)",
                fill=self.FG_TEXT, font=("Segoe UI", 9)
            )
            ly += 22

    def _draw_bar_chart(self, trend, current_month):
        self.bar_canvas.delete("all")
        w = self.bar_canvas.winfo_width() or 500
        h = self.bar_canvas.winfo_height() or 300

        margin_left, margin_bottom, margin_top = 55, 35, 15
        chart_w = w - margin_left - 20
        chart_h = h - margin_bottom - margin_top

        max_val = max((max(m["income"], m["expense"]) for m in trend), default=0)
        if max_val == 0:
            self.bar_canvas.create_text(w // 2, h // 2, text="No data for this year",
                                        fill=self.FG_SECONDARY, font=("Segoe UI", 12))
            return

        bar_group_w = chart_w / 12
        bar_w = bar_group_w * 0.35

        # Y-axis gridlines
        for i in range(5):
            y = margin_top + chart_h - (chart_h * i / 4)
            val = max_val * i / 4
            self.bar_canvas.create_line(margin_left, y, w - 20, y, fill="#2d3436", dash=(2, 4))
            self.bar_canvas.create_text(margin_left - 5, y, anchor=tk.E,
                                        text=f"${val:,.0f}", fill=self.FG_SECONDARY, font=("Segoe UI", 7))

        # Bars
        month_abbr = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
        for i, m in enumerate(trend):
            x = margin_left + i * bar_group_w
            # Income bar
            ih = (m["income"] / max_val) * chart_h if max_val else 0
            self.bar_canvas.create_rectangle(
                x + 2, margin_top + chart_h - ih, x + 2 + bar_w, margin_top + chart_h,
                fill=self.COLOR_INCOME, outline=""
            )
            # Expense bar
            eh = (m["expense"] / max_val) * chart_h if max_val else 0
            self.bar_canvas.create_rectangle(
                x + 2 + bar_w + 2, margin_top + chart_h - eh, x + 2 + bar_w * 2 + 2, margin_top + chart_h,
                fill=self.COLOR_EXPENSE, outline=""
            )
            # Month label
            label_color = "#00cec9" if m["month"] == current_month else self.FG_SECONDARY
            self.bar_canvas.create_text(
                x + bar_group_w / 2, margin_top + chart_h + 15,
                text=month_abbr[i], fill=label_color, font=("Segoe UI", 8, "bold")
            )

        # Legend
        lx, ly = margin_left + 10, margin_top + 5
        self.bar_canvas.create_rectangle(lx, ly, lx + 10, ly + 10, fill=self.COLOR_INCOME, outline="")
        self.bar_canvas.create_text(lx + 15, ly + 5, anchor=tk.W, text="Income", fill=self.FG_TEXT, font=("Segoe UI", 8))
        self.bar_canvas.create_rectangle(lx + 75, ly, lx + 85, ly + 10, fill=self.COLOR_EXPENSE, outline="")
        self.bar_canvas.create_text(lx + 90, ly + 5, anchor=tk.W, text="Expense", fill=self.FG_TEXT, font=("Segoe UI", 8))

    def _prev_month(self):
        m = self.selected_month.get() - 1
        y = self.selected_year.get()
        if m < 1:
            m = 12
            y -= 1
        self.selected_month.set(m)
        self.selected_year.set(y)
        self.refresh()

    def _next_month(self):
        m = self.selected_month.get() + 1
        y = self.selected_year.get()
        if m > 12:
            m = 1
            y += 1
        self.selected_month.set(m)
        self.selected_year.set(y)
        self.refresh()
