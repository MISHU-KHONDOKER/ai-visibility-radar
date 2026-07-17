"""
run_agent.py
------------
THE ORCHESTRATOR - the agent's brain. Runs the whole pipeline in order
with ONE command, instead of running each tool by hand.

Two modes:
  python run_agent.py            -> analysis only (cheap: uses existing data)
  python run_agent.py --full     -> full run (expensive: fresh measurement + customer search)

This is what turns a folder of tools into an AGENT.
"""

import sys
import subprocess
import os

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))


def run_step(name, script, description):
    """Run one pipeline step (another script) and report on it."""
    print("\n" + "=" * 66)
    print(f"  STEP: {name}")
    print(f"  {description}")
    print("=" * 66)
    try:
        # Run the script as a subprocess, from the src folder.
        result = subprocess.run(
            [sys.executable, script],
            cwd=_THIS_DIR,
            check=False,
        )
        if result.returncode == 0:
            print(f"  [OK] {name} complete.")
        else:
            print(f"  [!] {name} finished with issues (continuing anyway).")
    except Exception as e:
        print(f"  [!] {name} failed: {e} (continuing).")


def main():
    full = "--full" in sys.argv

    print("\n" + "#" * 66)
    print("#  HEIDSTAR SALES & MARKETING AGENT - PIPELINE RUN")
    print(f"#  Mode: {'FULL (fresh data - costs API quota)' if full else 'ANALYSIS ONLY (cheap - uses existing data)'}")
    print("#" * 66)

    # --- EXPENSIVE data-gathering steps (only in --full mode) ---
    if full:
        run_step("Measure Visibility", "run_measurement.py",
                 "Ask AI engines the buyer questions; record HEIDSTAR visibility + intel.")
        run_step("Find Customers (wide)", "find_customers_wide.py",
                 "Cast a wide net for candidate customer institutions.")

    # --- CHEAP analysis steps (always run) ---
    run_step("Visibility Scorecard", "heidstar_scorecard.py",
             "HEIDSTAR's visibility score - overall, by engine, by category, over time.")

    run_step("Competitor Tracking", "track_competitors.py",
             "Competitor mentions over time (duplicates merged).")

    run_step("New Entrants", "find_new_entrants.py",
             "Competitors not yet in our foundation (early warning).")

    run_step("OEM/ODM Lane", "oem_odm_view.py",
             "Competitors in HEIDSTAR's OEM/ODM battleground.")

    run_step("Category Breakdown", "category_breakdown.py",
             "Which question-lanes HEIDSTAR wins vs loses.")

    print("\n" + "#" * 66)
    print("#  AGENT RUN COMPLETE")
    if not full:
        print("#  (Run 'python run_agent.py --full' to also gather fresh data.)")
    print("#" * 66 + "\n")


if __name__ == "__main__":
    main()