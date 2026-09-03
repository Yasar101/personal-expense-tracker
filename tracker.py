"""Personal expense domain model with JSON persistence."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from decimal import Decimal
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
