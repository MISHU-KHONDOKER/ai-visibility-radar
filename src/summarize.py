"""
summarize.py
------------
Reads data/results.csv and prints a readable summary:
  - how many YES vs NO per engine
  - which competitors appear most often (ranked)
  - which sources are cited most often (ranked)

This teaches reading data BACK from a file and analysing it.
"""

import csv
import os
from collections import Counter

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
_RESULTS_PATH = os.path.join(_PROJECT_ROOT, "data", "results.csv")


def load_rows():
    """Read every row from results.csv into a list of dictionaries."""
    if not os.path.exists(_RESULTS_PATH):
        print("No results.csv found yet. Run a measurement first.")
        return []

    with open(_RESULTS_PATH, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader)


def summarize():
    rows = load_rows()
    if not rows:
        return

    print("=" * 60)
    print(f"SUMMARY OF {len(rows)} MEASUREMENTS")
    print("=" * 60)

    # --- 1. HEIDSTAR appearances, per engine ---
    print("\n--- HEIDSTAR appearance by engine ---")
    # Count YES/NO for each engine label.
    by_engine = {}
    for row in rows:
        engine = row["engine"]
        appeared = row["heidstar_appeared"]
        if engine not in by_engine:
            by_engine[engine] = {"YES": 0, "NO": 0}
        by_engine[engine][appeared] = by_engine[engine].get(appeared, 0) + 1

    for engine, counts in by_engine.items():
        yes = counts.get("YES", 0)
        no = counts.get("NO", 0)
        total = yes + no
        print(f"  {engine}: HEIDSTAR appeared {yes}/{total} times")

    # --- 2. Most-named competitors ---
    print("\n--- Top competitors (most frequently named) ---")
    competitor_counter = Counter()
    for row in rows:
        names = row.get("competitors_named", "")
        if names.strip():
            for name in names.split(";"):
                name = name.strip()
                if name:
                    competitor_counter[name] += 1

    for name, count in competitor_counter.most_common(15):
        print(f"  {count:3d}  {name}")

    # --- 3. Most-cited sources ---
    print("\n--- Top sources (most frequently cited) ---")
    source_counter = Counter()
    for row in rows:
        srcs = row.get("sources_cited", "")
        if srcs.strip():
            for s in srcs.split(";"):
                s = s.strip()
                if s:
                    source_counter[s] += 1

    if source_counter:
        for s, count in source_counter.most_common(15):
            print(f"  {count:3d}  {s}")
    else:
        print("  (no sources recorded)")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    summarize()