"""
category_breakdown.py
---------------------
Intelligence module: shows HEIDSTAR's visibility BY CATEGORY
(general, oem_odm, application, buyer_context, comparison) and by engine.
Reveals which lanes HEIDSTAR wins vs loses.
"""

import csv
import os
from collections import defaultdict
from foundation_loader import load_buyer_questions

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
_RESULTS_PATH = os.path.join(_PROJECT_ROOT, "data", "results.csv")


def build_question_categories():
    """Map each question's text -> its category, from the foundation."""
    questions = load_buyer_questions()
    return {q["text"]: q["category"] for q in questions}


def load_rows():
    if not os.path.exists(_RESULTS_PATH):
        print("No results.csv found. Run a measurement first.")
        return []
    with open(_RESULTS_PATH, "r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def parse_frequency(freq):
    """Turn '2/3' into (appeared=2, total=3). Returns (0,0) if unparseable."""
    if "/" in freq:
        parts = freq.split("/")
        if parts[0].isdigit() and parts[1].isdigit():
            return int(parts[0]), int(parts[1])
    return 0, 0


def breakdown():
    rows = load_rows()
    if not rows:
        return

    q_categories = build_question_categories()

    # Accumulate appeared/total per (category, engine).
    # stats[category][engine] = [appeared_sum, total_sum]
    stats = defaultdict(lambda: defaultdict(lambda: [0, 0]))

    for row in rows:
        question = row.get("question", "")
        category = q_categories.get(question, "uncategorized")
        engine = row.get("engine", "")
        appeared, total = parse_frequency(row.get("heidstar_appeared", ""))
        stats[category][engine][0] += appeared
        stats[category][engine][1] += total

    print("=" * 64)
    print("HEIDSTAR VISIBILITY BY CATEGORY")
    print("=" * 64)
    print("(How often HEIDSTAR appeared, per question-category, per engine)\n")

    # Print each category, showing each engine's hit-rate.
    for category in sorted(stats.keys()):
        print(f"--- {category.upper()} ---")
        for engine in sorted(stats[category].keys()):
            appeared, total = stats[category][engine]
            if total > 0:
                pct = (appeared / total) * 100
                bar = "#" * int(pct / 10)  # simple visual bar
                print(f"  {engine:20s}  {appeared:2d}/{total:2d}  "
                      f"({pct:5.1f}%)  {bar}")
            else:
                print(f"  {engine:20s}  no data")
        print()

    print("=" * 64)
    print("Read: categories where HEIDSTAR scores >0% are the winnable lanes.")
    print("Compare general/oem_odm (likely 0%) vs application (your bright spot).")


if __name__ == "__main__":
    breakdown()