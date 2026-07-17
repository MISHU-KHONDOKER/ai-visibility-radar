"""
foundation_loader.py
--------------------
Reads the shared data foundation (the JSON files in foundation/).
Every module reads its data through here - one clean source of truth.
"""

import json
import os

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
_FOUNDATION_DIR = os.path.join(_PROJECT_ROOT, "foundation")


def _load_json(filename):
    """Read one JSON file from the foundation folder."""
    path = os.path.join(_FOUNDATION_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"\nFoundation file missing: {path}\n"
            "FIX: make sure the file exists in the foundation/ folder.\n"
        )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_buyer_questions():
    """Return the list of buyer questions from the foundation."""
    data = _load_json("buyer_questions.json")
    return data["questions"]


def load_product_knowledge():
    """Return HEIDSTAR's ground-truth product knowledge."""
    return _load_json("product_knowledge.json")


def load_competitors_and_sources():
    """Return the competitor and source map."""
    return _load_json("competitors_and_sources.json")


def load_customers():
    """Return the customer database (known buyers/users)."""
    return _load_json("customers.json")


if __name__ == "__main__":
    print("Loading the shared data foundation...\n")

    questions = load_buyer_questions()
    print(f"Buyer questions: {len(questions)} loaded")

    pk = load_product_knowledge()
    print(f"Product knowledge: {pk['company']['name_en']}, {len(pk['products'])} products")

    cs = load_competitors_and_sources()
    print(f"Competitors: {len(cs['competitors'])}, Sources: {len(cs['high_trust_sources'])}")

    print("\nFoundation loaded successfully.")