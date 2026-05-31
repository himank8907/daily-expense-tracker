import os
import json
import datetime
import matplotlib.pyplot as plt

# ---------------- CONFIG / FILES ----------------
EXPENSES_FILE = "expenses.txt"
PASSWORD_FILE = "password.txt"
BUDGET_FILE = "monthly_budget.txt"

# ---------------- EMOJIS ----------------
emojis = {
    "Food": "🍔",
    "Transport": "🚌",
    "Entertainment": "🎮",
    "Shopping": "🛍",
    "Rent": "🏠",
    "Personal Expenses": "💸",
    "Medical Expenses": "💊",
    "Household Expense": "🧺",
    "Other": "📌"
}

# ---------------- HELPERS ----------------
def read_json_file(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default

def write_json_file(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def read_budget():
    if not os.path.exists(BUDGET_FILE):
        return None
    try:
        with open(BUDGET_FILE, "r") as f:
            return float(f.read().strip())
    except:
        return None

def save_budget(value):
    with open(BUDGET_FILE, "w") as f:
        f.write(str(value))

# ---------------- PASSWORD ----------------
def password_exists():
    return os.path.exists(PASSWORD_FILE)

def create_new_password():
    print("\n🔐 Create a new password.")
    while True:
        new_pass = input("Create NEW password: ").strip()
        confirm = input("Confirm NEW password: ").strip()

        if new_pass != confirm:
            print("❌ Passwords do not match! Try again.")
            continue

        with open(PASSWORD_FILE, "w") as f:
            f.write(new_pass)

        print("✅ Password created successfully!\n")
        return new_pass

def load_password():
    with open(PASSWORD_FILE, "r") as f:
        return f.read().strip()

def change_password_interactive():
    print("\n🔐 Change Password")
    old = input("Enter OLD password: ").strip()

    if not password_exists() or old != load_password():
        print("❌ Incorrect old password!")
        return False

    return create_new_password()

def login():
    """Login only if a password already exists."""
    if not password_exists():
        return  # First run → no login required yet

    current_password = load_password()

    while True:
        attempts = 0

        while attempts < 3:
            user = input("Enter password: ").strip()

            if user == current_password:
                print("\n✔ Login Successful!\n")
                return

            attempts += 1
            print(f"❌ Wrong password ({3 - attempts} attempts left)")

        print("\nToo many failed attempts.")
        if input("Reset password? (yes/no): ").lower() == "yes":
            current_password = create_new_password()

# ---------------- FIX EXPENSE ENTRIES ----------------
def repair_and_fix_expense_entry(e):
    try:
        d = datetime.datetime.strptime(e.get("date", ""), "%Y-%m-%d").date()
    except:
        d = datetime.date.today()
    e["date"] = d.isoformat()

    e["category"] = e.get("category") or "Other"
    e["emoji"] = emojis.get(e["category"], "")
    e["name"] = e.get("name") or "Unnamed"

    try:
        e["amount"] = float(e.get("amount", 0))
    except:
        e["amount"] = 0.0

    return e

def load_expenses():
    data = read_json_file(EXPENSES_FILE, [])
    if not isinstance(data, list):
        return []

    fixed = [repair_and_fix_expense_entry(e) for e in data]
    write_json_file(EXPENSES_FILE, fixed)
    return fixed

def save_expenses(expenses):
    write_json_file(EXPENSES_FILE, expenses)

# ---------------- BUDGET ----------------
def compute_remaining_month(expenses, monthly_budget):
    month_prefix = datetime.date.today().isoformat()[:7]
    spent = sum(e["amount"] for e in expenses if e["date"].startswith(month_prefix))
    return round(monthly_budget - spent, 2)

def ask_monthly_budget(expenses):
    while True:
        try:
            b = float(input("Enter monthly budget (₹): ").strip())
            break
        except:
            print("❌ Invalid input!")

    save_budget(b)
    remaining = compute_remaining_month(expenses, b)
    return b, remaining

def reset_monthly_budget(expenses):
    print("\n🔄 RESET MONTHLY BUDGET")
    return ask_monthly_budget(expenses)
# ---------------- GRAPH ----------------
def graph_categories(expenses):
    month = datetime.date.today().isoformat()[:7]
    cats = {}

    for e in expenses:
        if e["date"].startswith(month):
            cats[e["category"]] = cats.get(e["category"], 0) + e["amount"]

    if not cats:
        print("\n⚠ No expenses this month to show in graph!")
        return

    labels = list(cats.keys())
    values = list(cats.values())

    plt.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    plt.title("Spending by Category")
    plt.show()

# ---------------- MENU ----------------
def print_menu(first_time):
    print("\n========== MENU ==========")

    if first_time:
        print("1. Set Password")
        print("2. Exit")
        return

    print("1. Add Expense")
    print("2. View All Expenses")
    print("3. Monthly Total")
    print("4. Remaining Budget")
    print("5. Change Password")
    print("6. Show Category Graph")
    print("7. Reset Monthly Budget")
    print("8. Exit")

# ---------------- MAIN ----------------
def add_expense(expenses, remaining, budget):
    print("\n--- Add Expense ---")
    cats = list(emojis.keys())

    for i, c in enumerate(cats, 1):
        print(f"{i}. {c} {emojis[c]}")
    print(f"{len(cats) + 1}. Add new category")

    while True:
        try:
            choice = int(input("Choose category: "))
            if choice == len(cats) + 1:
                cat = input("Enter new category: ").strip()
                emojis[cat] = ""
            else:
                cat = cats[choice - 1]
            break
        except:
            print("❌ Invalid choice!")

    name = input("Item name: ").strip() or "Unnamed"

    while True:
        try:
            amount = float(input("Amount (₹): ").strip())
            if amount <= 0:
                print("❌ Amount must be greater than zero.")
                continue
            break
        except:
            print("❌ Invalid number!")

    entry = {
        "name": name,
        "amount": amount,
        "category": cat,
        "emoji": emojis.get(cat, ""),
        "date": datetime.date.today().isoformat()
    }

    expenses.append(entry)
    save_expenses(expenses)

    remaining = compute_remaining_month(expenses, budget)

    print(f"✔ Expense added! Remaining Budget: ₹{remaining}")
    return remaining

def monthly_total(expenses):
    month = datetime.date.today().isoformat()[:7]
    total = sum(e["amount"] for e in expenses if e["date"].startswith(month))
    print(f"\n📅 Monthly Total: ₹{total:.2f}")
    return total

def main():
    first_time = not password_exists()

    if not first_time:
        login()

    if first_time:
        while True:
            print_menu(first_time=True)
            choice = input("Option: ").strip()

            if choice == "1":
                create_new_password()
                first_time = False
                break

            elif choice == "2":
                print("Goodbye!")
                return

            else:
                print("Invalid option!")
    # Load data normally
    expenses = load_expenses()

    budget = read_budget()
    if budget is None:
        budget, remaining = ask_monthly_budget(expenses)
    else:
        remaining = compute_remaining_month(expenses, budget)

    print(f"\nMonthly Budget Loaded: ₹{budget} | Remaining: ₹{remaining}\n")

    # Main menu loop
    while True:
        print_menu(first_time=False)
        choice = input("Option: ").strip()

        if choice == "1":
            remaining = add_expense(expenses, remaining, budget)

        elif choice == "2":
            for i, e in enumerate(expenses, 1):
                print(f"{i}. {e['date']} {e['emoji']} {e['category']} - {e['name']} ₹{e['amount']}")

        elif choice == "3":
            monthly_total(expenses)

        elif choice == "4":
            print(f"\nRemaining Monthly Budget: ₹{remaining}")

        elif choice == "5":
            change_password_interactive()

        elif choice == "6":
            graph_categories(expenses)

        elif choice == "7":
            budget, remaining = reset_monthly_budget(expenses)

        elif choice == "8":
            print("Goodbye!")
            break

        else:
            print("Invalid option!")

if __name__ == "__main__":
    main()
    
