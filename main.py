"""Ledger — Student Budget & Savings Tracker (Python console version)."""
import ast
import json
import math
import os
import uuid
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "budget_data.json")

class Student:
    """Holds the student's identity and allowance."""
    def __init__(self, name, allowance, period="day"):
        self.name = name
        self.allowance = float(allowance)
        self.period = period

    def to_dict(self):
        return {"name": self.name, "allowance": self.allowance, "period": self.period}

    @staticmethod
    def from_dict(data):
        return Student(data["name"], data["allowance"], data.get("period", "day"))

class Expense:
    """A single expense entry."""
    def __init__(self, amount, category, note="", date=None, id_=None):
        self.id = id_ or str(uuid.uuid4())
        self.amount = float(amount)
        self.category = category
        self.note = note
        self.date = date or datetime.now().isoformat(timespec="minutes")

    def to_dict(self):
        return {"id": self.id, "amount": self.amount, "category": self.category,
                "note": self.note, "date": self.date}

    @staticmethod
    def from_dict(data):
        return Expense(data["amount"], data["category"], data.get("note", ""),
                       data.get("date"), data.get("id"))

class Saving:
    """A single savings entry."""
    def __init__(self, amount, note="", date=None, id_=None):
        self.id = id_ or str(uuid.uuid4())
        self.amount = float(amount)
        self.note = note
        self.date = date or datetime.now().isoformat(timespec="minutes")

    def to_dict(self):
        return {"id": self.id, "amount": self.amount, "note": self.note, "date": self.date}

    @staticmethod
    def from_dict(data):
        return Saving(data["amount"], data.get("note", ""), data.get("date"), data.get("id"))

class BudgetTracker:
    """Owns a Student and the expense/savings lists, and calculates totals."""
    def __init__(self, student):
        self.student = student
        self.expenses = []
        self.savings = []

    def add_expense(self, amount, category, note=""):
        entry = Expense(amount, category, note)
        self.expenses.append(entry)
        return entry

    def add_saving(self, amount, note=""):
        entry = Saving(amount, note)
        self.savings.append(entry)
        return entry

    def remove_expense(self, id_):
        self.expenses = [e for e in self.expenses if e.id != id_]

    def remove_saving(self, id_):
        self.savings = [s for s in self.savings if s.id != id_]

    def get_total_spent(self):
        return sum(e.amount for e in self.expenses)

    def get_total_saved(self):
        return sum(s.amount for s in self.savings)

    def get_remaining(self):
        return self.student.allowance - self.get_total_spent() - self.get_total_saved()

    def get_category_totals(self):
        totals = {}
        for expense in self.expenses:
            totals[expense.category] = totals.get(expense.category, 0) + expense.amount
        return totals

    def to_dict(self):
        return {
            "student": self.student.to_dict(),
            "expenses": [e.to_dict() for e in self.expenses],
            "savings": [s.to_dict() for s in self.savings],
        }

    @staticmethod
    def from_dict(data):
        tracker = BudgetTracker(Student.from_dict(data["student"]))
        tracker.expenses = [Expense.from_dict(e) for e in data.get("expenses", [])]
        tracker.savings = [Saving.from_dict(s) for s in data.get("savings", [])]
        return tracker

    def save(self, path=DATA_FILE):
        with open(path, "w", encoding="utf-8") as file:
            json.dump(self.to_dict(), file, indent=2)

    @staticmethod
    def load(path=DATA_FILE):
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as file:
            return BudgetTracker.from_dict(json.load(file))

class Calculator:
    """Basic arithmetic calculator using a safe AST parser."""
    @staticmethod
    def evaluate(expression):
        if not expression or len(expression) > 200:
            raise ValueError("Enter a calculation (maximum 200 characters).")
        ops = {ast.Add: lambda a, b: a + b,
               ast.Sub: lambda a, b: a - b,
               ast.Mult: lambda a, b: a * b,
               ast.Div: lambda a, b: a / b}

        def calculate(node, depth=0):
            if depth > 30:
                raise ValueError("Expression is too complex.")
            if isinstance(node, ast.Expression):
                return calculate(node.body, depth + 1)
            if isinstance(node, ast.Constant) and type(node.value) in (int, float):
                return node.value
            if isinstance(node, ast.BinOp) and type(node.op) in ops:
                return ops[type(node.op)](
                    calculate(node.left, depth + 1), calculate(node.right, depth + 1))
            if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
                value = calculate(node.operand, depth + 1)
                return -value if isinstance(node.op, ast.USub) else value
            raise ValueError("Only numbers and + - * / ( ) are allowed.")

        try:
            result = calculate(ast.parse(expression, mode="eval"))
            if not math.isfinite(result):
                raise ValueError("Calculation must be finite.")
            return result
        except (SyntaxError, ZeroDivisionError, OverflowError) as exc:
            raise ValueError(f"Invalid calculation: {exc}") from exc

def peso(amount):
    return f"₱{amount:,.2f}"

def ask_amount(prompt):
    """Ask for a positive monetary amount; = starts a math expression."""
    while True:
        raw = input(prompt).strip()
        try:
            value = Calculator.evaluate(raw[1:]) if raw.startswith("=") else float(raw)
            if not math.isfinite(value) or round(value, 2) <= 0:
                print("  Amount must be at least ₱0.01.")
                continue
            if raw.startswith("="):
                print(f"  -> {peso(value)}")
            return round(value, 2)
        except (ValueError, OverflowError) as exc:
            print(f"  Invalid amount: {exc}. Try 40 or =40+20.")

def print_header(text):
    print("\n" + "=" * 44)
    print(text)
    print("=" * 44)

def setup_student():
    print_header("Set up your allowance")
    name = input("Your name: ").strip() or "Student"
    while True:
        try:
            allowance = float(input("Allowance amount (₱): ").strip())
            if not math.isfinite(allowance) or allowance < 0:
                raise ValueError
            break
        except ValueError:
            print("  Please enter a valid non-negative number.")
    period = input("Per day/week/month [day]: ").strip().lower() or "day"
    if period not in ("day", "week", "month"):
        period = "day"
    tracker = BudgetTracker(Student(name, allowance, period))
    tracker.save()
    print(f"\nWelcome, {name}! Allowance set to {peso(allowance)} per {period}.")
    return tracker

def show_summary(tracker):
    print_header(f"Summary for {tracker.student.name}")
    print(f"Allowance ({tracker.student.period}): {peso(tracker.student.allowance)}")
    print(f"Total spent: {peso(tracker.get_total_spent())}")
    print(f"Total saved: {peso(tracker.get_total_saved())}")
    remaining = tracker.get_remaining()
    print(f"Remaining balance: {peso(remaining)}" +
          ("  (over budget!)" if remaining < 0 else ""))
    totals = tracker.get_category_totals()
    if totals:
        print("\nSpending by category:")
        for category, amount in sorted(totals.items(), key=lambda pair: -pair[1]):
            print(f"  - {category}: {peso(amount)}")

def add_expense_flow(tracker):
    print_header("Add an expense")
    amount = ask_amount("Amount (₱, or '=' for calculator, e.g. =40+20): ")
    category = input("Category (Pagkain/Pamasahe/Load/School supplies/Libangan/Iba pa): ").strip() or "Iba pa"
    note = input("Note (optional): ").strip()
    tracker.add_expense(amount, category, note)
    tracker.save()
    print(f"Added expense: {peso(amount)} - {category}")

def add_saving_flow(tracker):
    print_header("Add to savings")
    amount = ask_amount("Amount (₱, or '=' for calculator): ")
    note = input("Note (optional): ").strip()
    tracker.add_saving(amount, note)
    tracker.save()
    print(f"Added savings: {peso(amount)}")

def list_transactions(tracker):
    print_header("Transactions")
    items = (
        [("EXPENSE", e.id, e.date, e.category, e.note, -e.amount) for e in tracker.expenses]
        + [("SAVING", s.id, s.date, "Savings", s.note, s.amount) for s in tracker.savings]
    )
    items.sort(key=lambda item: item[2], reverse=True)
    if not items:
        print("No transactions yet.")
        return []
    for index, (kind, id_, date, category, note, signed) in enumerate(items, 1):
        sign = "+" if signed >= 0 else "-"
        print(f"{index:>2}. [{kind:<7}] {date} {category:<15} {sign}{peso(abs(signed))} {note}")
    return items

def delete_flow(tracker):
    items = list_transactions(tracker)
    if not items:
        return
    choice = input("\nEnter the number to delete (or blank to cancel): ").strip()
    if not choice.isdigit():
        return
    index = int(choice) - 1
    if 0 <= index < len(items):
        kind, id_, *_ = items[index]
        if kind == "EXPENSE":
            tracker.remove_expense(id_)
        else:
            tracker.remove_saving(id_)
        tracker.save()
        print("Deleted.")
    else:
        print("Invalid number.")

def calculator_flow():
    print_header("Calculator")
    expression = input("Enter expression (e.g. 40+20*2): ").strip()
    try:
        print(f"= {Calculator.evaluate(expression)}")
    except ValueError as exc:
        print(f"Invalid expression: {exc}")

def main_menu(tracker):
    while True:
        print_header(f"Ledger — {tracker.student.name}")
        print("1. View summary")
        print("2. Add expense")
        print("3. Add savings")
        print("4. View transactions")
        print("5. Delete a transaction")
        print("6. Calculator")
        print("7. Reset (start over)")
        print("0. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "1":
            show_summary(tracker)
        elif choice == "2":
            add_expense_flow(tracker)
        elif choice == "3":
            add_saving_flow(tracker)
        elif choice == "4":
            list_transactions(tracker)
        elif choice == "5":
            delete_flow(tracker)
        elif choice == "6":
            calculator_flow()
        elif choice == "7":
            confirm = input("This will erase all saved data. Type 'yes' to confirm: ").strip().lower()
            if confirm == "yes":
                if os.path.exists(DATA_FILE):
                    os.remove(DATA_FILE)
                tracker = setup_student()
        elif choice == "0":
            print("Ingat! Data mo ay naka-save na.")
            break
        else:
            print("Invalid option, please try again.")

def main():
    tracker = BudgetTracker.load()
    if tracker is None:
        tracker = setup_student()
    else:
        print(f"Welcome back, {tracker.student.name}!")
    main_menu(tracker)

if __name__ == "__main__":
    main()
