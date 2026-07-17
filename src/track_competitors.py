"""
track_competitors.py
--------------------
Intelligence module: tracks competitor mentions over time.
Merges duplicate spellings using BOTH foundation aliases AND
automatic name-normalization (so unseen spelling variants merge too).
"""

import csv
import os
from collections import defaultdict, Counter
from foundation_loader import load_competitors_and_sources
from normalize_names import normalize

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
_RESULTS_PATH = os.path.join(_PROJECT_ROOT, "data", "results.csv")


def build_alias_map():
    """Build a lookup: alias -> canonical name (from the foundation)."""
    data = load_competitors_and_sources()
    alias_map = {}
    for comp in data["competitors"]:
        canonical = comp["name_zh"]
        for alias in comp.get("aliases", []):
            alias_map[alias] = canonical
    return alias_map


def canonicalize(name, alias_map):
    """
    Translate a messy extracted name to its canonical company name.
    Step 1: if a known alias appears in the name, use that canonical name.
    Step 2: otherwise, fall back to the normalized key (merges variants).
    """
    for alias, canonical in alias_map.items():
        if alias in name:
            return canonical
    # No known alias: use the normalized form so spelling variants merge.
    norm = normalize(name)
    return norm if norm else name


def load_rows():
    if not os.path.exists(_RESULTS_PATH):
        print("No results.csv found. Run a measurement first.")
        return []
    with open(_RESULTS_PATH, "r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def track():
    rows = load_rows()
    if not rows:
        return

    alias_map = build_alias_map()

    # We track two things per date:
    #  - counts keyed by canonical key
    #  - a nice DISPLAY name for each key (the most common original spelling)
    by_date = defaultdict(Counter)               # date -> {key: count}
    display_for_key = defaultdict(Counter)        # key -> {original_name: count}

    for row in rows:
        day = row.get("date", "").split(" ")[0]
        competitors = row.get("competitors_named", "")
        if competitors.strip():
            for name in competitors.split(";"):
                name = name.strip()
                if not name:
                    continue
                key = canonicalize(name, alias_map)
                by_date[day][key] += 1
                display_for_key[key][name] += 1

    def label(key):
        """Pick the nicest display name for a canonical key."""
        if display_for_key[key]:
            # most common original spelling for this key
            return display_for_key[key].most_common(1)[0][0]
        return key

    print("=" * 60)
    print("COMPETITOR TRACKING OVER TIME (duplicates merged)")
    print("=" * 60)

    for day in sorted(by_date.keys(), reverse=True):
        counter = by_date[day]
        total = sum(counter.values())
        print(f"\n--- {day}  ({total} total mentions, "
              f"{len(counter)} distinct competitors) ---")
        for key, count in counter.most_common(12):
            print(f"  {count:3d}  {label(key)}")

    days = sorted(by_date.keys())
    if len(days) >= 2:
        print("\n" + "=" * 60)
        print("TREND (first vs latest date) - only notable changes")
        print("=" * 60)
        first, last = days[0], days[-1]
        # Only show competitors named at least 3 times total (skip noise).
        trends = []
        for key in set(by_date[first]) | set(by_date[last]):
            before = by_date[first].get(key, 0)
            after = by_date[last].get(key, 0)
            if before != after and (before + after) >= 3:
                trends.append((label(key), before, after))
        # Sort by size of change, biggest first.
        trends.sort(key=lambda t: abs(t[2] - t[1]), reverse=True)
        if trends:
            for name, before, after in trends:
                arrow = "UP" if after > before else "DOWN"
                print(f"  {name}: {before} -> {after}  ({arrow})")
        else:
            print("  (no notable changes yet)")
    else:
        print("\n(Only one date so far - run on different days to see trends.)")


if __name__ == "__main__":
    track()