import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
from pathlib import Path
from datetime import datetime, date, timedelta
from collections import defaultdict

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


# ============================================================
# ADVANCED EXPENSE TRACKER
# Python + Tkinter + JSON + Matplotlib
# Single-file project
# ============================================================

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"

FILES = {
    "expenses": DATA / "expenses.json",
    "income": DATA / "income.json",
    "budgets": DATA / "budgets.json",
    "settings": DATA / "settings.json",
}

CATEGORIES = [
    "Food",
    "Shopping",
    "Transport",
    "Education",
    "Health",
    "Entertainment",
    "Bills",
    "Travel",
    "Other"
]

SOURCES = [
    "Salary",
    "Pocket Money",
    "Freelance",
    "Business",
    "Gift",
    "Other"
]


# ============================================================
# JSON FUNCTIONS
# ============================================================

def save(path, data):
    DATA.mkdir(exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def load(path, default):
    DATA.mkdir(exist_ok=True)
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        save(path, default)
        return default


for key, default in [
    ("expenses", []),
    ("income", []),
    ("budgets", {}),
    ("settings", {"theme": "light"})
]:
    if not FILES[key].exists():
        save(FILES[key], default)


# ============================================================
# MAIN APPLICATION
# ============================================================

class App:

    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker System")
        self.root.geometry("1250x800")
        self.root.minsize(1050, 680)

        self.expenses = load(FILES["expenses"], [])
        self.income = load(FILES["income"], [])
        self.budgets = load(FILES["budgets"], {})
        self.settings = load(FILES["settings"], {"theme": "light"})
        self.theme = self.settings.get("theme", "light")

        self.selected_id = None
        self.selected_type = None

        self.create_variables()
        self.build_interface()

    # ========================================================
    # VARIABLES
    # ========================================================

    def create_variables(self):
        today = date.today().isoformat()

        self.kind = tk.StringVar(value="Expense")
        self.d = tk.StringVar(value=today)
        self.category = tk.StringVar(value=CATEGORIES[0])
        self.desc = tk.StringVar()
        self.amount = tk.StringVar()

        self.search = tk.StringVar()
        self.fcat = tk.StringVar(value="All")
        self.fmonth = tk.StringVar(value="All")
        self.fmin = tk.StringVar()
        self.fmax = tk.StringVar()

        self.bcat = tk.StringVar(value=CATEGORIES[0])
        self.bamount = tk.StringVar()

        self.rmonth = tk.StringVar(value=f"{date.today().month:02d}")
        self.ryear = tk.StringVar(value=str(date.today().year))

        self.income_var = tk.StringVar()
        self.expense_var = tk.StringVar()
        self.balance_var = tk.StringVar()
        self.month_var = tk.StringVar()

        self.today_var = tk.StringVar()
        self.week_var = tk.StringVar()
        self.high_var = tk.StringVar()
        self.top_var = tk.StringVar()

    # ========================================================
    # COLORS
    # ========================================================

    def palette(self):
        if self.theme == "light":
            return {
                "bg": "#eef2f6", "panel": "#ffffff", "text": "#1f2937",
                "muted": "#64748b", "header": "#203b4d", "accent": "#1677ff",
                "green": "#16a34a", "red": "#dc2626", "orange": "#f59e0b",
                "purple": "#7c3aed"
            }
        return {
            "bg": "#151a21", "panel": "#202731", "text": "#f1f5f9",
            "muted": "#a7b0bd", "header": "#0d151e", "accent": "#4f9cff",
            "green": "#35c76f", "red": "#ff5c5c", "orange": "#f6b73c",
            "purple": "#a678ff"
        }

    # ========================================================
    # TKINTER STYLE
    # ========================================================

    def setup_style(self):
        c = self.palette()
        self.root.configure(bg=c["bg"])
        style = ttk.Style()

        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("TFrame", background=c["bg"])
        style.configure("Panel.TFrame", background=c["panel"])
        style.configure("TLabel", background=c["bg"], foreground=c["text"], font=("Segoe UI", 10))
        style.configure("Panel.TLabel", background=c["panel"], foreground=c["text"], font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=c["header"], foreground="white", font=("Segoe UI", 24, "bold"))
        style.configure("Sub.TLabel", background=c["header"], foreground="#dbeafe", font=("Segoe UI", 10))
        style.configure("Section.TLabel", background=c["panel"], foreground=c["text"], font=("Segoe UI", 12, "bold"))
        style.configure("CardTitle.TLabel", background=c["panel"], foreground=c["muted"], font=("Segoe UI", 9, "bold"))
        style.configure("CardValue.TLabel", background=c["panel"], foreground=c["text"], font=("Segoe UI", 16, "bold"))
        style.configure("TEntry", fieldbackground=c["panel"], foreground=c["text"])
        style.configure("TCombobox", fieldbackground=c["panel"], foreground=c["text"])
        style.configure("Treeview", background=c["panel"], fieldbackground=c["panel"], foreground=c["text"], rowheight=28)
        style.configure("Treeview.Heading", background=c["header"], foreground="white", font=("Segoe UI", 9, "bold"))
        style.map("Treeview", background=[("selected", c["accent"])], foreground=[("selected", "white")])
        style.configure("TNotebook", background=c["bg"])
        style.configure("TNotebook.Tab", padding=(16, 8), font=("Segoe UI", 10, "bold"))

        buttons = {
            "Green": c["green"], "Red": c["red"], "Accent": c["accent"],
            "Purple": c["purple"], "Orange": c["orange"]
        }
        for name, color in buttons.items():
            style.configure(
                name + ".TButton",
                background=color, foreground="white",
                font=("Segoe UI", 9, "bold"), padding=(10, 6)
            )

            # ========================================================
    # BUILD MAIN INTERFACE
    # ========================================================

    def build_interface(self):
        self.setup_style()

        for widget in self.root.winfo_children():
            widget.destroy()

        c = self.palette()

        header = tk.Frame(self.root, bg=c["header"], height=90)
        header.pack(fill="x")
        header.pack_propagate(False)

        title_box = tk.Frame(header, bg=c["header"])
        title_box.pack(side="left", padx=25, pady=13)

        ttk.Label(title_box, text="Expense Tracker System", style="Title.TLabel").pack(anchor="w")
        ttk.Label(title_box, text="Personal Finance Management Dashboard", style="Sub.TLabel").pack(anchor="w")

        main = ttk.Frame(self.root)
        main.pack(fill="both", expand=True, padx=14, pady=12)

        self.build_cards(main)

        notebook = ttk.Notebook(main)
        notebook.pack(fill="both", expand=True)

        tabs = [
            ("Dashboard", self.dashboard_tab),
            ("Transactions", self.transactions_tab),
            ("Budgets", self.budgets_tab),
            ("Reports & Analytics", self.reports_tab)
        ]

        for name, function in tabs:
            frame = ttk.Frame(notebook)
            notebook.add(frame, text=f"  {name}  ")
            function(frame)

        self.status = tk.Label(
            self.root, text="Ready", anchor="w",
            bg=c["header"], fg="white", padx=10, pady=5
        )
        self.status.pack(fill="x")

        self.refresh()

    # ========================================================
    # DASHBOARD CARDS
    # ========================================================

    def build_cards(self, parent):
        c = self.palette()
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=(0, 10))

        cards = [
            ("Total Income", self.income_var, c["green"]),
            ("Total Expenses", self.expense_var, c["red"]),
            ("Current Balance", self.balance_var, c["accent"]),
            ("This Month", self.month_var, c["orange"])
        ]

        for i, (title, variable, accent) in enumerate(cards):
            frame.columnconfigure(i, weight=1)

            card = tk.Frame(frame, bg=c["panel"], highlightthickness=1, highlightbackground="#d7dee7")
            card.grid(row=0, column=i, sticky="nsew", padx=5)

            tk.Frame(card, bg=accent, height=4).pack(fill="x")

            ttk.Label(card, text=title, style="CardTitle.TLabel").pack(anchor="w", padx=13, pady=(10, 2))
            ttk.Label(card, textvariable=variable, style="CardValue.TLabel").pack(anchor="w", padx=13, pady=(0, 12))

    # ========================================================
    # DASHBOARD TAB
    # ========================================================

    def dashboard_tab(self, parent):
        top = ttk.Frame(parent)
        top.pack(fill="x", pady=8)

        stats = [
            ("Today's Spending", self.today_var),
            ("This Week", self.week_var),
            ("Highest Expense", self.high_var),
            ("Top Category", self.top_var)
        ]

        for i, (title, variable) in enumerate(stats):
            top.columnconfigure(i, weight=1)
            panel = ttk.Frame(top, style="Panel.TFrame")
            panel.grid(row=0, column=i, sticky="nsew", padx=5)

            ttk.Label(panel, text=title, style="CardTitle.TLabel").pack(anchor="w", padx=12, pady=(10, 2))
            ttk.Label(panel, textvariable=variable, style="CardValue.TLabel").pack(anchor="w", padx=12, pady=(0, 10))

        bottom = ttk.Frame(parent)
        bottom.pack(fill="both", expand=True)

        left = ttk.Frame(bottom, style="Panel.TFrame")
        left.pack(side="left", fill="both", expand=True, padx=(5, 3), pady=5)

        right = ttk.Frame(bottom, style="Panel.TFrame")
        right.pack(side="left", fill="both", expand=True, padx=(3, 5), pady=5)

        ttk.Label(left, text="Recent Expenses", style="Section.TLabel").pack(anchor="w", padx=10, pady=8)

        self.recent_tree = self.make_tree(
            left,
            [
                ("date", "Date", 105),
                ("category", "Category", 130),
                ("description", "Description", 250),
                ("amount", "Amount", 120)
            ]
        )
        self.recent_tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        ttk.Label(right, text="Category Spending", style="Section.TLabel").pack(anchor="w", padx=10, pady=8)

        self.category_tree = self.make_tree(
            right,
            [
                ("category", "Category", 150),
                ("spent", "Spent", 130),
                ("budget", "Budget", 130),
                ("remaining", "Remaining", 130)
            ]
        )
        self.category_tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # ========================================================
    # TREEVIEW HELPER
    # ========================================================

    def make_tree(self, parent, columns):
        tree = ttk.Treeview(
            parent,
            columns=[x[0] for x in columns],
            show="headings",
            selectmode="browse"
        )

        for key, title, width in columns:
            tree.heading(key, text=title)
            tree.column(key, width=width, minwidth=50)

        return tree

    # ========================================================
    # TRANSACTIONS TAB
    # ========================================================

    def transactions_tab(self, parent):
        c = self.palette()

        form = tk.Frame(
            parent, bg=c["panel"],
            highlightthickness=1, highlightbackground="#d7dee7"
        )
        form.pack(fill="x", padx=6, pady=6)

        ttk.Label(form, text="Add / Manage Transaction", style="Section.TLabel").grid(
            row=0, column=0, columnspan=8, sticky="w", padx=12, pady=10
        )

        ttk.Label(form, text="Type:", style="Panel.TLabel").grid(row=1, column=0, padx=6)

        type_combo = ttk.Combobox(
            form, textvariable=self.kind,
            values=["Expense", "Income"], state="readonly", width=11
        )
        type_combo.grid(row=1, column=1, padx=4)
        type_combo.bind("<<ComboboxSelected>>", self.kind_changed)

        ttk.Label(form, text="Date:", style="Panel.TLabel").grid(row=1, column=2, padx=5)
        ttk.Entry(form, textvariable=self.d, width=13).grid(row=1, column=3, padx=4)

        self.category_label = ttk.Label(form, text="Category:", style="Panel.TLabel")
        self.category_label.grid(row=1, column=4, padx=5)

        self.category_combo = ttk.Combobox(
            form, textvariable=self.category,
            values=CATEGORIES, state="readonly", width=15
        )
        self.category_combo.grid(row=1, column=5, padx=4)

        ttk.Label(form, text="Amount:", style="Panel.TLabel").grid(row=1, column=6, padx=5)
        ttk.Entry(form, textvariable=self.amount, width=14).grid(row=1, column=7, padx=(4, 12))

        ttk.Label(form, text="Description:", style="Panel.TLabel").grid(row=2, column=2, padx=5, pady=7)
        ttk.Entry(form, textvariable=self.desc, width=45).grid(
            row=2, column=3, columnspan=4, padx=4, pady=7, sticky="ew"
        )

        buttons = ttk.Frame(form, style="Panel.TFrame")
        buttons.grid(row=2, column=7, padx=8, pady=5)

        ttk.Button(buttons, text="Add", style="Green.TButton", command=self.add).pack(side="left", padx=2)
        ttk.Button(buttons, text="Update", style="Accent.TButton", command=self.update).pack(side="left", padx=2)
        ttk.Button(buttons, text="Delete", style="Red.TButton", command=self.delete).pack(side="left", padx=2)
        ttk.Button(buttons, text="Clear", style="Purple.TButton", command=self.clear_form).pack(side="left", padx=2)

        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill="both", expand=True, padx=6, pady=6)

        self.trans_tree = self.make_tree(
            tree_frame,
            [
                ("id", "ID", 100),
                ("date", "Date", 100),
                ("type", "Type", 90),
                ("category", "Category", 130),
                ("description", "Description", 260),
                ("amount", "Amount", 120)
            ]
        )
        self.trans_tree.pack(fill="both", expand=True)
        self.trans_tree.bind("<<TreeviewSelect>>", self.on_select_transaction)

        self.refresh_transactions_tree()

    def refresh_transactions_tree(self):
        if not hasattr(self, "trans_tree"):
            return

        for row in self.trans_tree.get_children():
            self.trans_tree.delete(row)

        combined = []
        for e in self.expenses:
            combined.append((e, "Expense"))
        for i in self.income:
            combined.append((i, "Income"))

        combined.sort(key=lambda x: x[0].get("date", ""), reverse=True)

        for record, kind in combined:
            self.trans_tree.insert(
                "", "end",
                iid=f"{kind}:{record['id']}",
                values=(
                    record.get("id", ""),
                    record.get("date", ""),
                    kind,
                    record.get("category", ""),
                    record.get("description", ""),
                    f"Rs. {float(record.get('amount', 0)):,.2f}"
                )
            )

    def on_select_transaction(self, event=None):
        selection = self.trans_tree.selection()
        if not selection:
            return

        iid = selection[0]
        kind, rec_id = iid.split(":")
        rec_id = int(rec_id)

        data = self.income if kind == "Income" else self.expenses
        record = next((r for r in data if r["id"] == rec_id), None)

        if record:
            self.selected_id = rec_id
            self.selected_type = kind
            self.kind.set(kind)
            self.kind_changed()
            self.d.set(record.get("date", ""))
            self.category.set(record.get("category", ""))
            self.desc.set(record.get("description", ""))
            self.amount.set(str(record.get("amount", "")))

    def kind_changed(self, event=None):
        if self.kind.get() == "Income":
            self.category_label.config(text="Source:")
            self.category_combo.config(values=SOURCES)
            if self.category.get() not in SOURCES:
                self.category.set(SOURCES[0])
        else:
            self.category_label.config(text="Category:")
            self.category_combo.config(values=CATEGORIES)
            if self.category.get() not in CATEGORIES:
                self.category.set(CATEGORIES[0])

    # ========================================================
    # ADD / UPDATE / DELETE / CLEAR
    # ========================================================

    def add(self):
        try:
            amount = float(self.amount.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive amount.")
            return

        if not self.desc.get().strip():
            messagebox.showerror("Error", "Description cannot be empty.")
            return

        try:
            datetime.strptime(self.d.get(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Date must be in YYYY-MM-DD format.")
            return

        record = {
            "id": int(datetime.now().timestamp() * 1000),
            "date": self.d.get(),
            "category": self.category.get(),
            "description": self.desc.get().strip(),
            "amount": amount
        }

        if self.kind.get() == "Income":
            self.income.append(record)
            save(FILES["income"], self.income)
        else:
            self.expenses.append(record)
            save(FILES["expenses"], self.expenses)

        messagebox.showinfo("Success", "Transaction added.")
        self.clear_form()
        self.refresh()
        self.refresh_transactions_tree()

    def update(self):
        if self.selected_id is None:
            messagebox.showerror("Error", "Select a transaction first.")
            return

        try:
            amount = float(self.amount.get())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive amount.")
            return

        data = self.income if self.selected_type == "Income" else self.expenses

        for record in data:
            if record["id"] == self.selected_id:
                record["date"] = self.d.get()
                record["category"] = self.category.get()
                record["description"] = self.desc.get().strip()
                record["amount"] = amount
                break

        save(
            FILES["income"] if self.selected_type == "Income" else FILES["expenses"],
            data
        )

        messagebox.showinfo("Success", "Transaction updated.")
        self.clear_form()
        self.refresh()
        self.refresh_transactions_tree()

    def delete(self):
        if self.selected_id is None:
            messagebox.showerror("Error", "Select a transaction first.")
            return

        if not messagebox.askyesno("Confirm", "Delete this transaction?"):
            return

        if self.selected_type == "Income":
            self.income = [r for r in self.income if r["id"] != self.selected_id]
            save(FILES["income"], self.income)
        else:
            self.expenses = [r for r in self.expenses if r["id"] != self.selected_id]
            save(FILES["expenses"], self.expenses)

        self.clear_form()
        self.refresh()
        self.refresh_transactions_tree()

    def clear_form(self):
        self.selected_id = None
        self.selected_type = None
        self.kind.set("Expense")
        self.d.set(date.today().isoformat())
        self.category.set(CATEGORIES[0])
        self.desc.set("")
        self.amount.set("")
        self.kind_changed()

        # ========================================================
    # BUDGETS TAB
    # ========================================================

    def budgets_tab(self, parent):
        c = self.palette()

        form = tk.Frame(
            parent, bg=c["panel"],
            highlightthickness=1, highlightbackground="#d7dee7"
        )
        form.pack(fill="x", padx=6, pady=6)

        ttk.Label(form, text="Set Budget", style="Section.TLabel").grid(
            row=0, column=0, columnspan=4, sticky="w", padx=12, pady=10
        )

        ttk.Label(form, text="Category:", style="Panel.TLabel").grid(row=1, column=0, padx=6)
        ttk.Combobox(
            form, textvariable=self.bcat, values=CATEGORIES,
            state="readonly", width=15
        ).grid(row=1, column=1, padx=4)

        ttk.Label(form, text="Amount:", style="Panel.TLabel").grid(row=1, column=2, padx=6)
        ttk.Entry(form, textvariable=self.bamount, width=14).grid(row=1, column=3, padx=4)

        ttk.Button(
            form, text="Save Budget", style="Accent.TButton",
            command=self.save_budget
        ).grid(row=1, column=4, padx=10)

        self.budget_tree = self.make_tree(
            parent,
            [("category", "Category", 200), ("amount", "Budget Amount", 200)]
        )
        self.budget_tree.pack(fill="both", expand=True, padx=6, pady=6)

        self.refresh_budget_tree()

    def refresh_budget_tree(self):
        if not hasattr(self, "budget_tree"):
            return

        for row in self.budget_tree.get_children():
            self.budget_tree.delete(row)

        for category, amount in self.budgets.items():
            self.budget_tree.insert("", "end", values=(category, f"Rs. {amount:,.2f}"))

    def save_budget(self):
        category = self.bcat.get()
        amount_text = self.bamount.get().strip()

        if not amount_text:
            messagebox.showerror("Error", "Please enter a budget amount.")
            return

        try:
            amount = float(amount_text)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number.")
            return

        if amount < 0:
            messagebox.showerror("Error", "Amount cannot be negative.")
            return

        self.budgets[category] = amount
        save(FILES["budgets"], self.budgets)

        messagebox.showinfo("Saved", f"Budget for {category} set to Rs. {amount:,.2f}")

        self.bamount.set("")
        self.refresh_budget_tree()
        self.refresh()

    # ========================================================
    # REPORTS TAB
    # ========================================================

    def reports_tab(self, parent):
        c = self.palette()

        form = tk.Frame(
            parent, bg=c["panel"],
            highlightthickness=1, highlightbackground="#d7dee7"
        )
        form.pack(fill="x", padx=6, pady=6)

        ttk.Label(form, text="Monthly Report", style="Section.TLabel").grid(
            row=0, column=0, columnspan=4, sticky="w", padx=12, pady=10
        )

        ttk.Label(form, text="Month:", style="Panel.TLabel").grid(row=1, column=0, padx=6)
        ttk.Combobox(
            form, textvariable=self.rmonth,
            values=[f"{i:02d}" for i in range(1, 13)],
            state="readonly", width=6
        ).grid(row=1, column=1, padx=4)

        ttk.Label(form, text="Year:", style="Panel.TLabel").grid(row=1, column=2, padx=6)
        ttk.Entry(form, textvariable=self.ryear, width=8).grid(row=1, column=3, padx=4)

        ttk.Button(
            form, text="Generate Report", style="Accent.TButton",
            command=self.generate_report
        ).grid(row=1, column=4, padx=10)

        self.report_label = ttk.Label(
            parent, text="Select a month and year, then click Generate Report.",
            style="Panel.TLabel", justify="left"
        )
        self.report_label.pack(anchor="w", padx=12, pady=12)

    def generate_report(self):
        month = self.rmonth.get()
        year = self.ryear.get()

        total_income = 0.0
        total_expense = 0.0
        count = 0
        highest = 0.0
        category_totals = {}

        for e in self.expenses:
            if e.get("date", "").startswith(f"{year}-{month}"):
                amt = float(e.get("amount", 0))
                total_expense += amt
                count += 1
                if amt > highest:
                    highest = amt
                cat = e.get("category", "Other")
                category_totals[cat] = category_totals.get(cat, 0) + amt

        for i in self.income:
            if i.get("date", "").startswith(f"{year}-{month}"):
                total_income += float(i.get("amount", 0))

        balance = total_income - total_expense
        top_category = max(category_totals, key=category_totals.get) if category_totals else "N/A"

        text = (
            f"Report for {month}/{year}\n\n"
            f"Total Income: Rs. {total_income:,.2f}\n"
            f"Total Expenses: Rs. {total_expense:,.2f}\n"
            f"Balance: Rs. {balance:,.2f}\n"
            f"Number of Expenses: {count}\n"
            f"Highest Expense: Rs. {highest:,.2f}\n"
            f"Top Spending Category: {top_category}"
        )

        self.report_label.config(text=text)

    # ========================================================
    # DASHBOARD REFRESH
    # ========================================================

    def refresh(self):
        total_income = sum(float(i.get("amount", 0)) for i in self.income)
        total_expense = sum(float(e.get("amount", 0)) for e in self.expenses)
        balance = total_income - total_expense

        today = date.today()
        today_str = today.isoformat()
        month_str = f"{today.year}-{today.month:02d}"

        month_total = sum(
            float(e.get("amount", 0)) for e in self.expenses
            if e.get("date", "").startswith(month_str)
        )

        today_total = sum(
            float(e.get("amount", 0)) for e in self.expenses
            if e.get("date", "") == today_str
        )

        week_ago = (today - timedelta(days=7)).isoformat()
        week_total = sum(
            float(e.get("amount", 0)) for e in self.expenses
            if e.get("date", "") >= week_ago
        )

        highest = max((float(e.get("amount", 0)) for e in self.expenses), default=0)

        cat_totals = {}
        for e in self.expenses:
            cat = e.get("category", "Other")
            cat_totals[cat] = cat_totals.get(cat, 0) + float(e.get("amount", 0))

        top_cat = max(cat_totals, key=cat_totals.get) if cat_totals else "N/A"

        self.income_var.set(f"Rs. {total_income:,.2f}")
        self.expense_var.set(f"Rs. {total_expense:,.2f}")
        self.balance_var.set(f"Rs. {balance:,.2f}")
        self.month_var.set(f"Rs. {month_total:,.2f}")

        self.today_var.set(f"Rs. {today_total:,.2f}")
        self.week_var.set(f"Rs. {week_total:,.2f}")
        self.high_var.set(f"Rs. {highest:,.2f}")
        self.top_var.set(top_cat)

        if hasattr(self, "recent_tree"):
            for row in self.recent_tree.get_children():
                self.recent_tree.delete(row)

            recent = sorted(self.expenses, key=lambda e: e.get("date", ""), reverse=True)[:15]

            for e in recent:
                self.recent_tree.insert(
                    "", "end",
                    values=(
                        e.get("date", ""),
                        e.get("category", ""),
                        e.get("description", ""),
                        f"Rs. {float(e.get('amount', 0)):,.2f}"
                    )
                )

        if hasattr(self, "category_tree"):
            for row in self.category_tree.get_children():
                self.category_tree.delete(row)

            for cat in CATEGORIES:
                spent = cat_totals.get(cat, 0)
                budget = float(self.budgets.get(cat, 0))
                remaining = budget - spent

                self.category_tree.insert(
                    "", "end",
                    values=(
                        cat,
                        f"Rs. {spent:,.2f}",
                        f"Rs. {budget:,.2f}",
                        f"Rs. {remaining:,.2f}"
                    )
                )


# ============================================================
# START APPLICATION
# ============================================================

root = tk.Tk()
app = App(root)
root.mainloop()