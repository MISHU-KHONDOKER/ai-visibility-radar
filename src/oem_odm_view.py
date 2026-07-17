"""
oem_odm_view.py
---------------
Intelligence module: focused view of the OEM/ODM competitor lane -
HEIDSTAR's actual battleground. Shows only competitors flagged as
doing OEM/ODM, ranked by their AI visibility.
"""

import csv
import os
from collections import Counter
from foundation_loader import load_competitors_and_sources

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
_RESULTS_PATH = os.path.join(_PROJECT_ROOT, "data", "results.csv")


def build_alias_map_oem_only():
    """
    Build alias -> canonical map, but ONLY for competitors that do OEM/ODM.
    Also return the set of OEM/ODM canonical names.
    """
    data = load_competitors_and_sources()
    alias_map = {}
    oem_canonicals = set()
    for comp in data["competitors"]:
        if comp.get("oem_odm"):
            canonical = comp["name_zh"]
            oem_canonicals.add(canonical)
            alias_map[canonical] = canonical
            for alias in comp.get("aliases", []):
                alias_map[alias] = canonical
    return alias_map, oem_canonicals


def canonicalize_oem(name, alias_map):
    """Map a name to an OEM/ODM canonical company, or None if not one."""
    for alias, canonical in alias_map.items():
        if alias in name:
            return canonical
    return None  # not an OEM/ODM competitor we track


def load_rows():
    if not os.path.exists(_RESULTS_PATH):
        print("No results.csv found. Run a measurement first.")
        return []
    with open(_RESULTS_PATH, "r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def show_oem_view():
    rows = load_rows()
    if not rows:
        return

    alias_map, oem_canonicals = build_alias_map_oem_only()

    # Count mentions of OEM/ODM competitors only.
    counter = Counter()
    for row in rows:
        comps = row.get("competitors_named", "")
        for name in comps.split(";"):
            name = name.strip()
            if name:
                canonical = canonicalize_oem(name, alias_map)
                if canonical:  # only counts if it's an OEM/ODM competitor
                    counter[canonical] += 1

    print("=" * 60)
    print("OEM / ODM COMPETITOR LANE - HEIDSTAR's battleground")
    print("=" * 60)
    print(f"\nCompetitors who do OEM/ODM, ranked by AI visibility:\n")

    if not counter:
        print("  (none found in the data yet)")
    else:
        for name, count in counter.most_common():
            print(f"  {count:3d}  {name}")

    # Also show which OEM/ODM competitors we track but DIDN'T appear.
    appeared = set(counter.keys())
    absent = oem_canonicals - appeared
    if absent:
        print(f"\nTracked OEM/ODM competitors NOT named in this data:")
        for name in sorted(absent):
            print(f"       {name}")

    print("\n" + "=" * 60)
    print("This is the lane HEIDSTAR competes in. These are the rivals")
    print("to watch most closely for OEM/ODM visibility.")


if __name__ == "__main__":
    show_oem_view()