"""
heidstar_scorecard.py
---------------------
HEIDSTAR's visibility report card - one focused view of OUR visibility:
overall score, by engine, by category, where we appeared, and over time.
Prints to terminal AND saves a shareable markdown file to the project root.
"""

import csv
import os
from collections import defaultdict
from datetime import datetime
from foundation_loader import load_buyer_questions

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
_RESULTS_PATH = os.path.join(_PROJECT_ROOT, "data", "results.csv")
_REPORT_PATH = os.path.join(_PROJECT_ROOT, "HEIDSTAR_Scorecard.md")


def build_question_categories():
    questions = load_buyer_questions()
    return {q["text"]: q["category"] for q in questions}


def load_rows():
    if not os.path.exists(_RESULTS_PATH):
        print("No results.csv found. Run a measurement first.")
        return []
    with open(_RESULTS_PATH, "r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def parse_freq(freq):
    """'3/3' -> (3, 3). Returns (0,0) if unparseable."""
    if "/" in freq:
        a, _, b = freq.partition("/")
        if a.isdigit() and b.isdigit():
            return int(a), int(b)
    return 0, 0


def pct(appeared, total):
    return (appeared / total * 100) if total else 0.0


def bar(percentage):
    return "#" * int(percentage / 5)  # one # per 5%


def scorecard():
    rows = load_rows()
    if not rows:
        return

    q_cat = build_question_categories()

    total_appeared = total_measured = 0
    by_engine = defaultdict(lambda: [0, 0])
    by_category = defaultdict(lambda: [0, 0])
    by_date = defaultdict(lambda: [0, 0])
    appearances = []

    for row in rows:
        appeared, total = parse_freq(row.get("heidstar_appeared", ""))
        if total == 0:
            continue
        total_appeared += appeared
        total_measured += total

        engine = row.get("engine", "")
        by_engine[engine][0] += appeared
        by_engine[engine][1] += total

        category = q_cat.get(row.get("question", ""), "uncategorized")
        by_category[category][0] += appeared
        by_category[category][1] += total

        day = row.get("date", "").split(" ")[0]
        by_date[day][0] += appeared
        by_date[day][1] += total

        if appeared > 0:
            appearances.append(row)

    # --- Build the report as a list of lines (so we can print AND save) ---
    lines = []
    lines.append("# HEIDSTAR AI Visibility Scorecard")
    lines.append("")
    lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    lines.append("")

    overall = pct(total_appeared, total_measured)
    lines.append(f"## Overall visibility: {total_appeared}/{total_measured} "
                 f"({overall:.1f}%)")
    lines.append("")

    lines.append("## By engine")
    lines.append("")
    lines.append("| Engine | Appeared | Rate |")
    lines.append("|--------|----------|------|")
    for engine in sorted(by_engine):
        a, t = by_engine[engine]
        lines.append(f"| {engine} | {a}/{t} | {pct(a,t):.1f}% |")
    lines.append("")

    lines.append("## By category (which lanes we win)")
    lines.append("")
    lines.append("| Category | Appeared | Rate |")
    lines.append("|----------|----------|------|")
    for cat in sorted(by_category):
        a, t = by_category[cat]
        lines.append(f"| {cat} | {a}/{t} | {pct(a,t):.1f}% |")
    lines.append("")

    lines.append("## Over time (the lift tracker)")
    lines.append("")
    lines.append("| Date | Appeared | Rate |")
    lines.append("|------|----------|------|")
    for day in sorted(by_date):
        a, t = by_date[day]
        lines.append(f"| {day} | {a}/{t} | {pct(a,t):.1f}% |")
    lines.append("")
    if len(by_date) < 2:
        lines.append("*(One date so far - re-measure after visibility work to see lift.)*")
        lines.append("")

    lines.append("## Where HEIDSTAR appeared")
    lines.append("")
    if appearances:
        for row in appearances:
            lines.append(f"- **{row.get('question','')}** "
                         f"({row.get('engine','')}) - result {row.get('heidstar_appeared','')}")
            lines.append(f"  - sources: {row.get('sources_cited','(none)')}")
    else:
        lines.append("*(HEIDSTAR has not appeared in any neutral measurement yet.)*")
    lines.append("")
    lines.append("---")
    lines.append("*This is the number to watch. Rising scores over time = "
                 "visibility work is paying off.*")

    report_text = "\n".join(lines)

    # Print to terminal (with simple bars for quick reading).
    print("=" * 64)
    print("        HEIDSTAR AI VISIBILITY SCORECARD")
    print("=" * 64)
    print(f"\n  OVERALL:  {total_appeared}/{total_measured}  ({overall:.1f}%)  {bar(overall)}")
    print("\n--- By engine ---")
    for engine in sorted(by_engine):
        a, t = by_engine[engine]
        print(f"  {engine:20s}  {a:2d}/{t:3d}  ({pct(a,t):5.1f}%)  {bar(pct(a,t))}")
    print("\n--- By category ---")
    for cat in sorted(by_category):
        a, t = by_category[cat]
        print(f"  {cat:16s}  {a:2d}/{t:3d}  ({pct(a,t):5.1f}%)  {bar(pct(a,t))}")
    print("\n--- Over time ---")
    for day in sorted(by_date):
        a, t = by_date[day]
        print(f"  {day}  {a:2d}/{t:3d}  ({pct(a,t):5.1f}%)  {bar(pct(a,t))}")
    print("\n--- Where HEIDSTAR appeared ---")
    if appearances:
        for row in appearances:
            print(f"  [{row.get('engine','')}] {row.get('question','')}")
            print(f"       result: {row.get('heidstar_appeared','')}  "
                  f"| sources: {row.get('sources_cited','(none)')}")
    else:
        print("  (none yet)")

    # Save the shareable markdown file.
    with open(_REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"\nShareable report saved: {_REPORT_PATH}")


if __name__ == "__main__":
    scorecard()