"""
run_summary.py
--------------
Groups logged API calls into "runs" by time proximity (time-gap clustering).
Calls close together in time = one engine run. A big gap = a new run.

Gives each run: start time, duration, calls, tokens, cost, web-searches.
No engine changes needed - reads the existing usage_log.csv.
"""

import csv
import os
from datetime import datetime

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
_USAGE_LOG = os.path.join(_PROJECT_ROOT, "data", "usage_log.csv")

# Calls more than this many minutes apart are treated as separate runs.
_GAP_MINUTES = 5


def load_calls():
    """Load all logged calls, parsed and sorted by time."""
    if not os.path.exists(_USAGE_LOG):
        return []
    calls = []
    with open(_USAGE_LOG, "r", newline="", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            try:
                dt = datetime.strptime(r["datetime"], "%Y-%m-%d %H:%M:%S")
                calls.append({
                    "dt": dt,
                    "engine": r.get("engine", ""),
                    "model": r.get("model", ""),
                    "tokens": int(r.get("total_tokens", 0) or 0),
                    "cost": float(r.get("est_cost_rmb", 0) or 0),
                })
            except (ValueError, KeyError):
                continue
    calls.sort(key=lambda c: c["dt"])
    return calls


def group_into_runs():
    """Cluster calls into runs by time gaps. Returns a list of run dicts."""
    calls = load_calls()
    if not calls:
        return []

    runs = []
    current = None

    for c in calls:
        if current is None:
            # start the first run
            current = _new_run(c)
        else:
            gap = (c["dt"] - current["end"]).total_seconds() / 60.0
            if gap > _GAP_MINUTES:
                # big gap -> close current run, start a new one
                runs.append(current)
                current = _new_run(c)
            else:
                _add_to_run(current, c)

    if current:
        runs.append(current)

    return runs


def _new_run(call):
    run = {
        "start": call["dt"], "end": call["dt"],
        "calls": 0, "tokens": 0, "cost": 0.0,
        "models": {},
    }
    _add_to_run(run, call)
    return run


def _add_to_run(run, call):
    run["end"] = call["dt"]
    run["calls"] += 1
    run["tokens"] += call["tokens"]
    run["cost"] += call["cost"]
    run["models"][call["model"]] = run["models"].get(call["model"], 0) + 1


def summarize_runs():
    """Print a per-run summary to the terminal."""
    runs = group_into_runs()
    if not runs:
        print("No runs logged yet.")
        return

    print("=" * 70)
    print("  PER-RUN COST SUMMARY (calls grouped by time)")
    print("=" * 70)

    total_cost = total_tokens = total_calls = 0
    # newest run first
    for i, run in enumerate(reversed(runs), 1):
        dur = (run["end"] - run["start"]).total_seconds() / 60.0
        models = ", ".join(f"{m}({n})" for m, n in run["models"].items())
        print(f"\nRun {len(runs) - i + 1}  |  {run['start'].strftime('%Y-%m-%d %H:%M')}")
        print(f"   duration: {dur:.1f} min   calls: {run['calls']}   "
              f"tokens: {run['tokens']:,}   cost: ¥{run['cost']:.6f}")
        print(f"   models: {models}")
        total_cost += run["cost"]
        total_tokens += run["tokens"]
        total_calls += run["calls"]

    print("\n" + "=" * 70)
    print(f"  TOTAL: {len(runs)} runs   {total_calls} calls   "
          f"{total_tokens:,} tokens   ¥{total_cost:.6f}")
    print("=" * 70)


if __name__ == "__main__":
    summarize_runs()