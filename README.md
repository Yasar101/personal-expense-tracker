# Personal Expense Tracker

**TESTED** · [Live demo](https://yasar101.github.io/software-engineering-portfolio/demos/expense-tracker.html) · [Portfolio](https://github.com/Yasar101/software-engineering-portfolio)

A local expense model with category/monthly totals and JSON save/load.

## Purpose and engineering skills

Explore domain modelling, money representation and persistence round trips.

## Structure

tracker.py contains an immutable Expense and a tracker with a JSON adapter. [Source](tracker.py).

## Run

From this directory with Python 3.11+, run this offline example using `python3` (no dependencies or credentials):

```python
from datetime import date
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from tracker import Expense, ExpenseTracker
tracker = ExpenseTracker([Expense(Decimal("4.50"), "food", date(2026, 9, 1))])
with TemporaryDirectory() as directory:
    path = Path(directory) / "expenses.json"
    tracker.save(path)
    assert ExpenseTracker.load(path).total_for_month(2026, 9) == Decimal("4.50")
```

## Test

```sh
python3 -m compileall -q .
python3 - <<'PY'
from datetime import date
from decimal import Decimal
from tracker import Expense, ExpenseTracker
tracker = ExpenseTracker([
    Expense(Decimal("10.50"), "food", date(2026, 9, 1)),
    Expense(Decimal("4.25"), "travel", date(2026, 9, 2)),
])
assert tracker.total_for_month(2026, 9) == Decimal("14.75")
assert [e.category for e in tracker.filter("FOOD", 2026, 9)] == ["food"]
print("report example passed")
PY
```

The full regression suite (failure paths, README examples and demo checks) runs in the [portfolio repository](https://github.com/Yasar101/software-engineering-portfolio).

## Complete and remaining

**Complete:** Positive-amount/category validation, reports and a tested save/load round trip.

**Remaining / limitations:** No UI, encryption, atomic writes, concurrent-writer support or comprehensive corrupt-file recovery. Use synthetic data for evaluation.

## Learning takeaway

Serializing decimals as strings preserves money values across JSON round trips.

## Command-line demonstration
Run a real local persistence flow (expenses.json is local user data):

```bash
python3 -m tracker --file expenses.json add 12.50 food --note "Lunch"
python3 -m tracker --file expenses.json list
python3 -m tracker --file expenses.json list --category food --month 2026-09
python3 -m tracker --file expenses.json summary --month 2026-09
```