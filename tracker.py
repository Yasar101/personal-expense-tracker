"""Personal expense domain model with JSON persistence."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path


@dataclass(frozen=True)
class Expense:
    amount: Decimal
    category: str
    spent_on: date
    note: str = ""

    def __post_init__(self) -> None:
        if self.amount <= 0:
            raise ValueError("amount must be positive")
        if not self.category.strip():
            raise ValueError("category is required")


class ExpenseTracker:
    def __init__(self, expenses: list[Expense] | None = None) -> None:
        self.expenses = list(expenses or [])

    def add(self, expense: Expense) -> None:
        self.expenses.append(expense)

    def totals_by_category(self) -> dict[str, Decimal]:
        totals: dict[str, Decimal] = {}
        for item in self.expenses:
            totals[item.category] = totals.get(item.category, Decimal("0")) + item.amount
        return totals

    def total_for_month(self, year: int, month: int) -> Decimal:
        return sum(
            (item.amount for item in self.expenses if item.spent_on.year == year and item.spent_on.month == month),
            start=Decimal("0"),
        )

    def filter(self, category: str | None = None, year: int | None = None, month: int | None = None) -> list[Expense]:
        """Return expenses matching optional category and calendar filters."""
        normalised_category = category.strip().casefold() if category else None
        return [item for item in self.expenses if (
            (normalised_category is None or item.category.casefold() == normalised_category)
            and (year is None or item.spent_on.year == year)
            and (month is None or item.spent_on.month == month)
        )]

    def save(self, path: Path) -> None:
        payload = [
            {**asdict(item), "amount": str(item.amount), "spent_on": item.spent_on.isoformat()}
            for item in self.expenses
        ]
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "ExpenseTracker":
        if not path.exists():
            return cls()
        payload = json.loads(path.read_text(encoding="utf-8"))
        return cls([Expense(Decimal(row["amount"]), row["category"], date.fromisoformat(row["spent_on"]), row.get("note", "")) for row in payload])


def main() -> None:
    """Manage a portable local expense file without external dependencies."""
    import argparse

    parser = argparse.ArgumentParser(description="Track personal expenses in a local JSON file.")
    parser.add_argument("--file", type=Path, default=Path("expenses.json"), help="JSON file to read and update")
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add", help="add an expense")
    add.add_argument("amount", help="positive decimal amount, for example 12.50")
    add.add_argument("category", help="for example food or travel")
    add.add_argument("--date", dest="spent_on", default=date.today().isoformat(), help="ISO date (default: today)")
    add.add_argument("--note", default="", help="optional description")
    listing = commands.add_parser("list", help="list recorded expenses")
    listing.add_argument("--category", help="case-insensitive category filter")
    listing.add_argument("--month", help="YYYY-MM filter")
    summary = commands.add_parser("summary", help="show totals for a month")
    summary.add_argument("--month", help="YYYY-MM (default: current month)")
    args = parser.parse_args()

    try:
        tracker = ExpenseTracker.load(args.file)
        if args.command == "add":
            tracker.add(Expense(Decimal(args.amount), args.category, date.fromisoformat(args.spent_on), args.note))
            tracker.save(args.file)
            print(f"Saved expense to {args.file}: {args.category} £{Decimal(args.amount):.2f}")
        elif args.command == "list":
            year = month = None
            if args.month:
                year, month = map(int, args.month.split("-"))
            expenses = tracker.filter(args.category, year, month)
            if not expenses:
                print("No expenses recorded yet.")
            for item in expenses:
                note = f" — {item.note}" if item.note else ""
                print(f"{item.spent_on.isoformat()}  {item.category:<12} £{item.amount:.2f}{note}")
        else:
            year, month = map(int, (args.month or date.today().strftime("%Y-%m")).split("-"))
            print(f"Total for {year:04d}-{month:02d}: £{tracker.total_for_month(year, month):.2f}")
            for category, amount in sorted(tracker.totals_by_category().items()):
                print(f"{category:<12} £{amount:.2f}")
    except (ValueError, InvalidOperation, json.JSONDecodeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
