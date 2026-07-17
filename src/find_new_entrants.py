"""
find_new_entrants.py
--------------------
Intelligence module: flags competitors the AI named that are NOT in our
foundation - i.e. companies we aren't tracking yet (early warning).
"""

import csv
import os
from collections import Counter
from foundation_loader import load_competitors_and_sources

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
_RESULTS_PATH = os.path.join(_PROJECT_ROOT, "data", "results.csv")


def build_known_aliases():
    """Collect ALL known names+aliases from the foundation into one set."""
    data = load_competitors_and_sources()
    known = set()
    for comp in data["competitors"]:
        known.add(comp["name_zh"])
        for alias in comp.get("aliases", []):
            known.add(alias)
    return known


def is_known(name, known_aliases):
    """True if this name matches any known company/alias."""
    for alias in known_aliases:
        if alias in name:
            return True
    return False


def load_rows():
    if not os.path.exists(_RESULTS_PATH):
        print("No results.csv found. Run a measurement first.")
        return []
    with open(_RESULTS_PATH, "r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def find_new_entrants():
    rows = load_rows()
    if not rows:
        return

    known_aliases = build_known_aliases()

    # Count every named competitor that is NOT known.
    new_entrants = Counter()
    for row in rows:
        competitors = row.get("competitors_named", "")
        if competitors.strip():
            for name in competitors.split(";"):
                name = name.strip()
                if name and not is_known(name, known_aliases):
                    new_entrants[name] += 1

    print("=" * 60)
    print("NEW ENTRANTS - competitors NOT in our foundation")
    print("=" * 60)

    if not new_entrants:
        print("\nNo new entrants found - all named competitors are tracked.")
        return

    print(f"\nFound {len(new_entrants)} companies we are NOT tracking yet.")
    print("(Sorted by how often the AI named them - top ones worth adding.)\n")

    for name, count in new_entrants.most_common(25):
        print(f"  {count:3d}  {name}")

    print("\nTip: review the top ones - if any are real competitors,")
    print("add them to competitors_and_sources.json so they get tracked.")


if __name__ == "__main__":
    find_new_entrants()