"""
show_win.py
-----------
Finds the measurements where HEIDSTAR appeared and prints the full
answer + sources, so we can understand WHY it surfaced.
"""

import csv
import os

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
_RESULTS_PATH = os.path.join(_PROJECT_ROOT, "data", "results.csv")


def show_wins():
    with open(_RESULTS_PATH, "r", newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    # Find rows where HEIDSTAR appeared (frequency not "0/..." and not "FAILED").
    wins = []
    for row in rows:
        freq = row.get("heidstar_appeared", "")
        # appeared if the first number is greater than 0
        if "/" in freq:
            appeared_count = freq.split("/")[0]
            if appeared_count.isdigit() and int(appeared_count) > 0:
                wins.append(row)

    if not wins:
        print("No measurements where HEIDSTAR appeared.")
        return

    print(f"Found {len(wins)} measurement(s) where HEIDSTAR appeared:\n")
    for row in wins:
        print("=" * 70)
        print(f"Date:    {row['date']}")
        print(f"Engine:  {row['engine']}")
        print(f"Question:{row['question']}")
        print(f"Result:  HEIDSTAR appeared {row['heidstar_appeared']}")
        print(f"Sources: {row.get('sources_cited', '(none)')}")
        print("-" * 70)
        print("ANSWER:")
        print(row.get("answer", ""))
        print()


if __name__ == "__main__":
    show_wins()