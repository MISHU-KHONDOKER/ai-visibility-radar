"""
show_candidates.py
------------------
Prints the accumulated customer candidates in a readable way.
"""

import os
import json

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
_CANDIDATES_PATH = os.path.join(_PROJECT_ROOT, "data", "customer_candidates.json")


def show():
    if not os.path.exists(_CANDIDATES_PATH):
        print("No candidates file yet. Run find_customers_wide.py first.")
        return

    with open(_CANDIDATES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    candidates = data.get("candidates", [])
    print(f"{len(candidates)} customer candidate(s):\n")

    for i, c in enumerate(candidates, 1):
        print(f"{i}. {c.get('name', '?')}  [{c.get('status', '?')}]")
        print(f"   type:   {c.get('type', '')}")
        print(f"   country:{c.get('country', '')}")
        print(f"   detail: {c.get('detail', '')}")
        print(f"   found by: {c.get('source_query', '')}")
        print()


if __name__ == "__main__":
    show()