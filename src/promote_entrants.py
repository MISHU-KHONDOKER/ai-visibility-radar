"""
promote_entrants.py
-------------------
Interactive helper: walks through new entrants and adds the ones you
approve into competitors_and_sources.json - no manual JSON editing.
Now with LLM pre-filtering to remove non-company noise before review.
Makes a backup before changing anything (safety).
"""

import csv
import os
import json
import shutil
from collections import Counter
from foundation_loader import load_competitors_and_sources
from filter_companies_llm import filter_real_companies

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
_RESULTS_PATH = os.path.join(_PROJECT_ROOT, "data", "results.csv")
_FOUNDATION_PATH = os.path.join(_PROJECT_ROOT, "foundation", "competitors_and_sources.json")


def build_known_aliases():
    data = load_competitors_and_sources()
    known = set()
    for comp in data["competitors"]:
        known.add(comp["name_zh"])
        for alias in comp.get("aliases", []):
            known.add(alias)
    return known


def is_known(name, known_aliases):
    return any(alias in name for alias in known_aliases)


def load_rows():
    if not os.path.exists(_RESULTS_PATH):
        return []
    with open(_RESULTS_PATH, "r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def get_new_entrants():
    """Return Counter of competitor names not in the foundation."""
    rows = load_rows()
    known = build_known_aliases()
    new = Counter()
    for row in rows:
        comps = row.get("competitors_named", "")
        for name in comps.split(";"):
            name = name.strip()
            if name and not is_known(name, known):
                new[name] += 1
    return new


def main():
    new_entrants = get_new_entrants()
    if not new_entrants:
        print("No new entrants to review. Everything is already tracked.")
        return

    # Show only ones named at least twice (skip one-off noise by default).
    candidates = [(name, count) for name, count in new_entrants.most_common()
                  if count >= 2]

    if not candidates:
        print("No new entrants named 2+ times. Nothing to review.")
        return

    # LLM pre-filter: remove obvious non-companies before you review.
    print("Pre-filtering candidates with LLM (removing non-companies)...")
    candidate_names = [name for name, count in candidates]
    real_names = filter_real_companies(candidate_names)
    candidates = [(name, count) for name, count in candidates
                  if name in real_names]

    if not candidates:
        print("No real companies found after filtering. Nothing to review.")
        return
    print(f"Filtered to {len(candidates)} likely-real companies.\n")

    print(f"Reviewing {len(candidates)} new entrants.")
    print("For each: type 'y' to add, 'n' to skip, or 'q' to quit reviewing.\n")

    to_add = []
    for name, count in candidates:
        answer = input(f"  Add '{name}' (named {count}x)?  [y/n/q]: ").strip().lower()
        if answer == "q":
            break
        if answer == "y":
            to_add.append(name)

    if not to_add:
        print("\nNothing approved. Foundation unchanged.")
        return

    # --- SAFETY: back up the foundation file before changing it ---
    backup_path = _FOUNDATION_PATH + ".backup"
    shutil.copy(_FOUNDATION_PATH, backup_path)
    print(f"\nBackup saved: {backup_path}")

    # Load, add the approved companies, save.
    with open(_FOUNDATION_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for name in to_add:
        data["competitors"].append({
            "name_zh": name,
            "name_en": "",
            "tier": "new-entrant",
            "oem_odm": False,
            "ai_mentions": new_entrants[name],
            "aliases": [name]
        })

    with open(_FOUNDATION_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nAdded {len(to_add)} new competitors to the foundation:")
    for name in to_add:
        print(f"  + {name}")
    print("\nThey will now be tracked and merged in future runs.")


if __name__ == "__main__":
    main()