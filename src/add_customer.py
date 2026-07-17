"""
add_customer.py
---------------
Interactive helper to add a customer to the customer database
(foundation/customers.json) without hand-editing JSON.
Backs up the file before changing it (safety).
Only add REAL customers with a real source.
"""

import os
import json
import shutil
from foundation_loader import load_customers

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
_CUSTOMERS_PATH = os.path.join(_PROJECT_ROOT, "foundation", "customers.json")


def ask(field, hint=""):
    """Prompt for one field. Returns the typed value (stripped)."""
    prompt = f"  {field}"
    if hint:
        prompt += f" ({hint})"
    prompt += ": "
    return input(prompt).strip()


def main():
    data = load_customers()
    existing = data["customers"]

    print("Add a new customer to the database.")
    print("Only add REAL customers with a real source. Press Enter to skip a field.\n")

    name_zh = ask("Name (Chinese)")
    if not name_zh:
        print("No name given. Aborting - nothing added.")
        return

    # Build the next id automatically.
    next_num = len(existing) + 1
    new_id = f"cust_{next_num:03d}"

    customer = {
        "id": new_id,
        "name_zh": name_zh,
        "name_en": ask("Name (English)"),
        "type": ask("Type", "end_user / oem_odm_partner"),
        "segment": ask("Segment", "e.g. 基层/县域医院"),
        "region": ask("Region", "e.g. 云南 (Yunnan)"),
        "country": ask("Country", "e.g. China"),
        "product_used": ask("Product used", "HEIDSTAR model or competitor"),
        "relationship": ask("Relationship", "HEIDSTAR customer / competitor's customer / prospect"),
        "source": ask("Source", "REQUIRED - how do we know? e.g. 中标公告 2025"),
        "notes": ask("Notes", "optional"),
    }

    # Require a source - keeps the database honest.
    if not customer["source"]:
        print("\nNo source given. Not adding (every customer needs a source).")
        return

    # Show what will be added and confirm.
    print("\nAbout to add:")
    for k, v in customer.items():
        print(f"  {k}: {v}")
    confirm = input("\nAdd this customer? [y/n]: ").strip().lower()
    if confirm != "y":
        print("Cancelled. Nothing added.")
        return

    # Backup, then save.
    backup = _CUSTOMERS_PATH + ".backup"
    shutil.copy(_CUSTOMERS_PATH, backup)

    data["customers"].append(customer)
    with open(_CUSTOMERS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nAdded {new_id}: {name_zh}")
    print(f"(Backup saved: {backup})")
    print(f"Database now has {len(data['customers'])} customers.")


if __name__ == "__main__":
    main()