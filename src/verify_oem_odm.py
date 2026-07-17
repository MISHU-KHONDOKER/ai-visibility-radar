"""
verify_oem_odm.py
-----------------
Asks the AI (Qwen with web search) whether each tracked competitor
actually offers OEM/ODM pathology scanner manufacturing.
Produces an AI-ASSESSED signal (not verified fact) to replace guesses.
Updates the foundation file, with a backup first.
"""

import os
import json
import shutil
from ask_engine import ask_engine
from foundation_loader import load_competitors_and_sources

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
_FOUNDATION_PATH = os.path.join(_PROJECT_ROOT, "foundation", "competitors_and_sources.json")


def ask_oem_odm(company_name):
    """
    Ask the AI whether this company does OEM/ODM pathology scanners.
    Returns "yes", "no", or "unclear".
    """
    question = (
        f"{company_name} 这家公司是否为数字病理扫描仪/切片扫描仪提供 "
        f"OEM 代工 或 ODM 设计定制服务？"
        f"请只回答一个词：yes（是）、no（否）、或 unclear（不确定）。"
    )
    try:
        answer = ask_engine("qwen", question, use_web_search=True)
        low = answer.lower()
        # Look for the clearest signal in the answer.
        if "yes" in low or "是" in answer:
            return "yes"
        if "no" in low or "否" in answer:
            return "no"
        return "unclear"
    except Exception as e:
        print(f"    ! failed for {company_name}: {e}")
        return "unclear"


def main():
    data = load_competitors_and_sources()
    competitors = data["competitors"]

    print(f"Verifying OEM/ODM for {len(competitors)} competitors via AI...")
    print("(This makes one web-search call per company - may take a while.)\n")

    for comp in competitors:
        name = comp["name_zh"]
        result = ask_oem_odm(name)
        # Store as an AI-assessed field, separate from any manual truth.
        comp["oem_odm_ai_assessed"] = result
        print(f"  {name}: {result}")

    # Backup before saving.
    backup = _FOUNDATION_PATH + ".backup2"
    shutil.copy(_FOUNDATION_PATH, backup)
    print(f"\nBackup saved: {backup}")

    with open(_FOUNDATION_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("\nDone. Each competitor now has an 'oem_odm_ai_assessed' field.")
    print("NOTE: this is the AI's assessment, NOT verified fact - spot-check the important ones.")


if __name__ == "__main__":
    main()