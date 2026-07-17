"""
usage_summary.py
----------------
Reads data/usage_log.csv and summarizes API consumption + estimated cost.
Used by the dashboard to build the cost charts.
"""

import csv
import os
from collections import defaultdict

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
_USAGE_LOG = os.path.join(_PROJECT_ROOT, "data", "usage_log.csv")


def load_usage():
    """Return all usage rows as a list of dicts (or empty list)."""
    if not os.path.exists(_USAGE_LOG):
        return []
    with open(_USAGE_LOG, "r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def summarize():
    """
    Return a summary dict:
      - totals: total calls, tokens, cost
      - by_model: {model: {calls, tokens, cost}}
      - by_date:  {date: {tokens, cost}}
    """
    rows = load_usage()

    totals = {"calls": 0, "tokens": 0, "cost": 0.0}
    by_model = defaultdict(lambda: {"calls": 0, "tokens": 0, "cost": 0.0})
    by_date = defaultdict(lambda: {"tokens": 0, "cost": 0.0})

    for r in rows:
        try:
            tokens = int(r.get("total_tokens", 0) or 0)
            cost = float(r.get("est_cost_rmb", 0) or 0)
        except ValueError:
            continue
        model = r.get("model", "unknown")
        date = r.get("datetime", "").split(" ")[0]

        totals["calls"] += 1
        totals["tokens"] += tokens
        totals["cost"] += cost

        by_model[model]["calls"] += 1
        by_model[model]["tokens"] += tokens
        by_model[model]["cost"] += cost

        by_date[date]["tokens"] += tokens
        by_date[date]["cost"] += cost

    return {
        "totals": totals,
        "by_model": dict(by_model),
        "by_date": dict(by_date),
    }


if __name__ == "__main__":
    s = summarize()
    print("TOTALS:", s["totals"])
    print("\nBY MODEL:")
    for m, d in s["by_model"].items():
        print(f"  {m}: {d}")
    print("\nBY DATE:")
    for d, v in s["by_date"].items():
        print(f"  {d}: {v}")