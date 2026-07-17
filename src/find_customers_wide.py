"""
find_customers_wide.py
----------------------
Stage 1 of the customer-finding robot: casts a WIDE net across many
buyer types (hospitals, labs, universities, SMEs, companies - domestic
and international) to surface as many candidate customers as possible.

Accumulates into a candidate list and deduplicates over time.

HONEST LIMITS: uses AI web-search, which is not exhaustive and not
guaranteed accurate. Every result is a CANDIDATE to verify, not a fact.
The truly internet-wide, always-on version needs direct data-source
integration + automation (a larger future build - for CEO discussion).
"""

import os
import json
from ask_engine import ask_engine

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
_CANDIDATES_PATH = os.path.join(_PROJECT_ROOT, "data", "customer_candidates.json")


# A WIDE set of searches, each targeting a different buyer type.
# Add more queries here anytime to widen the net further.
_SEARCH_QUERIES = [
    # --- "Cases/examples" phrasing (this is what WORKED - forces named institutions) ---
    "数字病理科 建设 医院 案例",
    "数字病理 落地 案例 哪些医院",
    "数字病理远程会诊 试点 医院 名单",
    "病理AI 临床应用 医院 案例",
    "数字病理 标杆 医院 有哪些",
    # --- By hospital tier ---
    "三甲医院 数字病理 装机 案例",
    "县级医院 数字病理 建设 案例",
    "妇幼保健院 数字病理 宫颈筛查 案例",
    # --- By region (provinces - widens coverage) ---
    "广东 医院 数字病理 建设 案例",
    "江苏 浙江 数字病理 医院 案例",
    "四川 重庆 数字病理 医院 案例",
    "山东 河南 数字病理 医院 案例",
    # --- Labs / third-party / research ---
    "第三方医学检验所 数字病理 案例 哪些",
    "区域病理诊断中心 名单 案例",
    "高校 医学院 数字病理平台 建设 案例",
    "科研院所 数字病理 装机 案例",
    # --- Screening programs (HEIDSTAR's beachhead) ---
    "宫颈癌筛查 项目 数字病理 案例 医院",
    "两癌筛查 数字病理 设备 项目 案例",
    # --- International (named examples) ---
    "digital pathology hospital deployment case examples",
    "hospitals using whole slide imaging examples list",
]


_EXTRACT_INSTRUCTION = """你是一个客户线索提取助手。请阅读下面的文本，找出其中提到的
【可能购买或使用数字病理扫描仪的机构/单位】作为潜在客户线索。

包括：医院、检验所、实验室、大学、研究院所、筛查项目单位、相关公司等
（国内或国外均可）。

对每一条，提取：
- name: 机构/单位名称
- type: 类型（医院/实验室/大学/研究所/公司/筛查项目/其他）
- country: 国家（如能判断）
- detail: 简短说明（如采购了什么、用途等）

只提取文本中【明确出现】的真实机构名称，不要编造。
如果没有，返回空数组。

只返回 JSON，格式严格如下：
{"leads": [
  {"name": "...", "type": "...", "country": "...", "detail": "..."}
]}

需要分析的文本如下：
"""


def load_candidates():
    """Load the accumulated candidate list (or empty)."""
    if os.path.exists(_CANDIDATES_PATH):
        with open(_CANDIDATES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"candidates": []}


def save_candidates(data):
    with open(_CANDIDATES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def already_have(name, candidates):
    """True if we already have this lead (simple name match)."""
    for c in candidates:
        if name and (name in c["name"] or c["name"] in name):
            return True
    return False


def find_wide():
    data = load_candidates()
    candidates = data["candidates"]
    start_count = len(candidates)

    print(f"Casting a wide net across {len(_SEARCH_QUERIES)} buyer-type searches.")
    print(f"(Currently have {start_count} candidates. New ones will be added.)\n")

    new_count = 0

    for i, query in enumerate(_SEARCH_QUERIES, 1):
        print(f"[{i}/{len(_SEARCH_QUERIES)}] {query}")
        try:
            answer = ask_engine("qwen", query, use_web_search=True)
            prompt = _EXTRACT_INSTRUCTION + answer
            raw = ask_engine("deepseek", prompt, use_web_search=False)
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
            leads = json.loads(cleaned).get("leads", [])

            added_here = 0
            for lead in leads:
                name = lead.get("name", "").strip()
                if name and not already_have(name, candidates):
                    lead["source_query"] = query
                    lead["status"] = "unverified"
                    candidates.append(lead)
                    added_here += 1
                    new_count += 1
            print(f"      found {len(leads)}, added {added_here} new")

        except Exception as e:
            print(f"      ! failed: {e}")

    save_candidates(data)

    print(f"\n{'='*60}")
    print(f"Done. Added {new_count} new candidates.")
    print(f"Total candidates now: {len(candidates)}")
    print(f"Saved to: {_CANDIDATES_PATH}")
    print("REMEMBER: these are UNVERIFIED leads. Verify before treating")
    print("as real customers or adding to the customer database.")
    print('='*60)


if __name__ == "__main__":
    find_wide()