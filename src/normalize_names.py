"""
normalize_names.py
------------------
Shared helper: normalizes a competitor name to a canonical 'key' so that
spelling variants of the same company collapse together.

e.g. "3DHISTECH（匈牙利）", "3D Histech", "3DHISTECH" -> all become "3dhistech"
"""

import re


# Common company-suffix words to strip (Chinese + English).
_SUFFIXES = [
    "有限公司", "股份有限公司", "科技有限公司", "医疗科技有限公司",
    "生物科技有限公司", "技术有限公司", "集团", "公司",
    "科技", "医疗", "生物", "技术", "电子",
    "co.,ltd", "co.ltd", "ltd", "inc", "corp", "company",
]


def normalize(name):
    """
    Reduce a name to a comparison key:
      - remove anything in brackets/parentheses (Chinese and English)
      - lowercase
      - remove spaces, dots, dashes
      - strip common company suffixes
    Returns a normalized string used only for MATCHING (not for display).
    """
    if not name:
        return ""

    s = name

    # 1. Remove bracketed content: （...）, (...), [...], 【...】
    s = re.sub(r"[（(\[【].*?[）)\]】]", "", s)

    # 2. Lowercase (affects English).
    s = s.lower()

    # 3. Remove spaces, dots, dashes, slashes.
    s = re.sub(r"[\s\.\-_/]+", "", s)

    # 4. Strip common suffixes.
    for suf in _SUFFIXES:
        s = s.replace(suf.lower(), "")

    return s.strip()


# Quick self-test.
if __name__ == "__main__":
    tests = [
        "3DHISTECH（匈牙利）", "3D Histech", "3DHISTECH", "3DHistech（3DH）",
        "Philips（飞利浦）", "Philips",
        "优纳科技", "优纳医疗",
        "丹吉尔（济南丹吉尔电子有限公司）", "丹吉尔",
    ]
    for t in tests:
        print(f"{t:35s} -> {normalize(t)}")