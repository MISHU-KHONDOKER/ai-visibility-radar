"""
cleanup_oem_flags.py
--------------------
One-time cleanup: removes the unreliable 'oem_odm_ai_assessed' field
and marks each competitor's oem_odm status honestly as needing manual
verification (unless it was already manually set with confidence).
"""

import os
import json
import shutil
from foundation_loader import load_competitors_and_sources

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
_FOUNDATION_PATH = os.path.join(_PROJECT_ROOT, "foundation", "competitors_and_sources.json")

# The original competitors whose OEM/ODM we set from research (more trustworthy).
# These keep their flag; everything else is marked "unverified".
RESEARCH_BASED = {
    "江丰生物", "麦克奥迪", "优纳科技", "泰立瑞", "颂明医疗",
    "希森", "生强科技",
}


def main():
    data = load_competitors_and_sources()

    for comp in data["competitors"]:
        # Remove the unreliable AI-assessed field if present.
        comp.pop("oem_odm_ai_assessed", None)

        name = comp["name_zh"]
        # Record honest verification status.
        if name in RESEARCH_BASED:
            comp["oem_odm_status"] = "research-based (verify before relying)"
        else:
            comp["oem_odm_status"] = "UNVERIFIED - needs manual check"

    backup = _FOUNDATION_PATH + ".backup3"
    shutil.copy(_FOUNDATION_PATH, backup)
    print(f"Backup saved: {backup}")

    with open(_FOUNDATION_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Cleanup done. Removed AI-assessed field; added honest 'oem_odm_status'.")
    print("Competitors now carry their true verification status.")


if __name__ == "__main__":
    main()