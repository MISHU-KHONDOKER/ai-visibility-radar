import csv
import os
from datetime import datetime

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
_RESULTS_PATH = os.path.join(_PROJECT_ROOT, "data", "results.csv")

# Column headings - including the intelligence columns.
_COLUMNS = [
    "date", "engine", "question", "heidstar_appeared",
    "competitors_named", "sources_cited", "answer",
]


def save_result(engine, question, heidstar_appeared,
                competitors_named, sources_cited, answer):
    """Save one measurement (with intelligence) as a row in results.csv."""
    file_is_new = not os.path.exists(_RESULTS_PATH)

    with open(_RESULTS_PATH, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        if file_is_new:
            writer.writerow(_COLUMNS)

        today = datetime.now().strftime("%Y-%m-%d %H:%M")
        writer.writerow([
            today, engine, question, heidstar_appeared,
            competitors_named, sources_cited, answer,
        ])

    print(f"  (result saved to data/results.csv)")


if __name__ == "__main__":
    save_result(
        engine="test-engine",
        question="test question",
        heidstar_appeared="NO",
        competitors_named="江丰生物; 优纳科技",
        sources_cited="百度百科",
        answer="test answer",
    )
    print("Test save done. Check data/results.csv")