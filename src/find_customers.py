"""
find_customers.py
-----------------
Intelligence module: maps the CUSTOMER LANDSCAPE for HEIDSTAR -
buyer segments (categories), not specific named leads.
Covers both end-users (hospitals/labs) and OEM/ODM partners.

Reliable by design: asks the AI to CHARACTERIZE market segments
(something it does well), not to invent specific company facts.
"""

import json
from ask_engine import ask_engine
from foundation_loader import load_product_knowledge


def _build_prompt(focus_description):
    """Build a structured-output prompt for one customer landscape."""
    return f"""你是一位医疗器械行业市场分析师。HEIDSTAR（海德星）是一家数字病理切片扫描仪
（WSI/DPS）的源头工厂，提供 OEM/ODM 贴牌定制，约80%业务为ODM。

请分析以下客户群体：{focus_description}

针对这个方向，列出主要的【客户细分群体/类别】（不是具体公司名称，而是类别）。
对每一个细分群体，给出：
- segment: 细分群体名称
- who: 这类客户是谁（简短描述）
- needs: 他们最看重什么（采购关注点）
- growth: 增长趋势（"高"、"中"、或"低"）

只返回 JSON，不要任何其他文字或 markdown。格式严格如下：
{{"segments": [
  {{"segment": "...", "who": "...", "needs": "...", "growth": "..."}}
]}}
"""


def _ask_segments(focus_description):
    """Ask the AI for segments, parse the JSON, return a list."""
    prompt = _build_prompt(focus_description)
    try:
        raw = ask_engine("qwen", prompt, use_web_search=True)
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        data = json.loads(cleaned)
        return data.get("segments", [])
    except Exception as e:
        print(f"  (failed to get segments: {e})")
        return []


def find_customers():
    print("Mapping HEIDSTAR's customer landscape (segments)...\n")

    # Two landscapes to map.
    landscapes = [
        ("END-USERS (使用扫描仪的机构)",
         "数字病理扫描仪的【最终用户/使用机构】，例如医院、实验室、筛查项目等"),
        ("OEM/ODM PARTNERS (会贴牌定制的企业)",
         "会向源头工厂【贴牌定制/OEM/ODM】病理扫描仪的【企业类型】，"
         "例如诊断服务公司、AI病理软件公司、区域品牌商、IVD企业等"),
    ]

    for title, focus in landscapes:
        print("=" * 64)
        print(f"  {title}")
        print("=" * 64)
        segments = _ask_segments(focus)
        if not segments:
            print("  (no segments returned)\n")
            continue
        for seg in segments:
            name = seg.get("segment", "?")
            who = seg.get("who", "")
            needs = seg.get("needs", "")
            growth = seg.get("growth", "?")
            print(f"\n  • {name}   [growth: {growth}]")
            print(f"      who:   {who}")
            print(f"      needs: {needs}")
        print()

    print("=" * 64)
    print("Note: these are market SEGMENTS (reliable AI analysis),")
    print("not specific sales leads. Use to focus sales strategy.")


if __name__ == "__main__":
    find_customers()