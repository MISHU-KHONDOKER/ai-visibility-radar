"""
source_mapping.py
-----------------
Intelligence module: maps which SOURCES are cited alongside each
competitor - revealing WHERE competitors win their AI visibility.
Reads real cited-source data from results.csv (reliable, no guessing).
Shows English labels beside known Chinese source AND company names.
"""

import csv
import os
from collections import defaultdict, Counter
from foundation_loader import load_competitors_and_sources

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
_RESULTS_PATH = os.path.join(_PROJECT_ROOT, "data", "results.csv")


# Known source translations: Chinese keyword -> English label.
_SOURCE_EN = {
    "仪器信息网": "Instrument.com.cn",
    "百度百科": "Baidu Baike",
    "中国制造网": "Made-in-China",
    "天眼查": "Tianyancha",
    "爱企查": "Aiqicha",
    "企查查": "Qichacha",
    "中国医疗器械行业协会": "China Medical Device Industry Assoc.",
    "中国光学学会": "Chinese Optical Society",
    "政府采购": "Gov procurement",
    "中标公告": "Bid-winning notice",
    "公司官网": "Company website",
    "企业官网": "Company website",
    "行业报告": "Industry report",
    "行业信息": "Industry info",
    "公开资料": "Public records",
    "产品认证信息": "Product certification",
    "企业资质": "Company credentials",
    "医院": "(hospital - likely a customer, not a source)",
}


def with_english(source):
    """Add an English label beside a Chinese source name if we know it."""
    for zh, en in _SOURCE_EN.items():
        if zh in source:
            return f"{source}  [{en}]"
    return source  # unknown source - show as-is


def build_alias_map():
    """alias -> canonical name, from the foundation."""
    data = load_competitors_and_sources()
    alias_map = {}
    for comp in data["competitors"]:
        canonical = comp["name_zh"]
        alias_map[canonical] = canonical
        for alias in comp.get("aliases", []):
            alias_map[alias] = canonical
    return alias_map


def build_english_names():
    """canonical Chinese name -> English name, from the foundation."""
    data = load_competitors_and_sources()
    en_map = {}
    for comp in data["competitors"]:
        en = comp.get("name_en", "").strip()
        en_map[comp["name_zh"]] = en
    return en_map


def comp_with_english(canonical, en_map):
    """Show 'Chinese (English)' if we have an English name, else just Chinese."""
    en = en_map.get(canonical, "")
    if en:
        return f"{canonical} ({en})"
    return canonical


def canonicalize(name, alias_map):
    for alias, canonical in alias_map.items():
        if alias in name:
            return canonical
    return name


def load_rows():
    if not os.path.exists(_RESULTS_PATH):
        print("No results.csv found. Run a measurement first.")
        return []
    with open(_RESULTS_PATH, "r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def map_sources():
    rows = load_rows()
    if not rows:
        return

    alias_map = build_alias_map()
    en_map = build_english_names()

    # For each competitor, count the sources that appeared in the SAME answer.
    competitor_sources = defaultdict(Counter)
    all_sources = Counter()

    for row in rows:
        comps_raw = row.get("competitors_named", "")
        srcs_raw = row.get("sources_cited", "")

        # Canonical competitors named in this answer.
        comps = set()
        for name in comps_raw.split(";"):
            name = name.strip()
            if name:
                comps.add(canonicalize(name, alias_map))

        # Sources cited in this answer.
        sources = [s.strip() for s in srcs_raw.split(";") if s.strip()]
        for s in sources:
            all_sources[s] += 1

        # Associate each competitor with each source in this answer.
        for comp in comps:
            for s in sources:
                competitor_sources[comp][s] += 1

    # --- Report 1: overall most-cited sources ---
    print("=" * 60)
    print("SOURCE MAPPING - where competitors win their visibility")
    print("=" * 60)

    print("\n--- Most-cited sources overall ---")
    if all_sources:
        for src, count in all_sources.most_common(12):
            print(f"  {count:3d}  {with_english(src)}")
    else:
        print("  (no sources recorded yet - need more runs with cited sources)")

    # --- Report 2: top competitors and their associated sources ---
    print("\n--- Sources associated with top competitors ---")
    ranked = sorted(competitor_sources.items(),
                    key=lambda kv: sum(kv[1].values()), reverse=True)

    if not ranked:
        print("  (no competitor-source associations yet)")
    else:
        for comp, src_counter in ranked[:8]:
            if not src_counter:
                continue
            print(f"\n  {comp_with_english(comp, en_map)}:")
            for src, count in src_counter.most_common(5):
                print(f"     {count:2d}x  {with_english(src)}")

    print("\n" + "=" * 60)
    print("Strategic read: the sources clustered around visible competitors")
    print("are the ones HEIDSTAR most needs presence on.")


if __name__ == "__main__":
    map_sources()