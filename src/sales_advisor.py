"""
sales_advisor.py
----------------
CEO Instruction #2 (the buildable, honest part): a sales strategy advisor.

Reads the engine's real findings (visibility, competitors, customer
segments/candidates) and asks the AI to produce:
  1. Sales strategy per buyer segment (how to approach, what to lead with)
  2. Competitive positioning (how to position vs named rivals)
  3. LEGITIMATE channel routing (how to REACH each segment via proper
     organizational routes - NOT fake personal contacts)

HONEST SCOPE: this gives strategy + legitimate channels. It does NOT
invent personal contact details (names/emails/phones) - real contacts
require real data sources (company CRM, paid B2B data providers, official
listings) and privacy/compliance care. AI guessing would produce fakes.
"""

import csv
import os
import json
from collections import Counter
from ask_engine import ask_engine

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
_RESULTS = os.path.join(_PROJECT_ROOT, "data", "results.csv")
_CANDIDATES = os.path.join(_PROJECT_ROOT, "data", "customer_candidates.json")


def gather_findings():
    """Compile real findings: visibility, top competitors, candidate types."""
    facts = []

    if os.path.exists(_RESULTS):
        with open(_RESULTS, "r", newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
        total_a = total_m = 0
        comp_counter = Counter()
        appeared = []
        for r in rows:
            freq = r.get("heidstar_appeared", "")
            if "/" in freq:
                a, _, b = freq.partition("/")
                if a.isdigit() and b.isdigit():
                    total_a += int(a); total_m += int(b)
                    if int(a) > 0:
                        appeared.append(r.get("question", ""))
            for c in r.get("competitors_named", "").split(";"):
                c = c.strip()
                if c:
                    comp_counter[c] += 1
        pct = (total_a / total_m * 100) if total_m else 0
        facts.append(f"HEIDSTAR AI visibility: {total_a}/{total_m} ({pct:.1f}%).")
        if appeared:
            facts.append(f"HEIDSTAR's proven niche (where it appears): {'; '.join(set(appeared))}")
        facts.append("Top competitors: " +
                     "; ".join(f"{n}({c})" for n, c in comp_counter.most_common(6)))

    if os.path.exists(_CANDIDATES):
        with open(_CANDIDATES, "r", encoding="utf-8") as f:
            cands = json.load(f).get("candidates", [])
        types = Counter(c.get("type", "?") for c in cands)
        facts.append(f"Customer candidates: {len(cands)} total; types: " +
                     "; ".join(f"{t}:{n}" for t, n in types.most_common()))

    return "\n".join(facts)


def advise():
    findings = gather_findings()
    if not findings.strip():
        print("No findings yet. Run the engine first.")
        return

    print("=" * 64)
    print("  SALES STRATEGY ADVISOR")
    print("=" * 64)
    print("\nBased on these real findings:\n")
    print(findings)

    prompt = f"""你是 HEIDSTAR（海德星，数字病理扫描仪源头工厂，主营OEM/ODM，
已在县域医院宫颈癌筛查场景有成功案例）的资深销售策略顾问。

以下是我们引擎的真实发现：
{findings}

请基于这些真实数据，提供一份销售策略建议，包含三部分：

1. 【分客户群销售策略】针对主要客户类型（如三甲医院、县域医院、第三方实验室、
   AI病理软件公司/OEM伙伴），分别说明：应主打什么卖点、用什么角度切入。

2. 【竞争定位】面对江丰生物等领先对手，HEIDSTAR应如何差异化定位（例如性价比、
   OEM灵活性、源头工厂优势）。

3. 【合规的触达渠道】针对每类客户，说明可通过哪些【正规的组织渠道/平台】去触达
   （例如政府采购平台、医学会、行业展会、行业媒体、B2B平台等）。
   【重要】不要编造任何具体的个人联系人姓名、电话或邮箱——只给出正规的组织级渠道。
   真实的联系人需要通过公司CRM、正规商业数据服务或官方公开信息获取。

请用中文回答，条理清晰、具体可执行。这是给人类销售团队参考的建议。"""

    print("\n" + "=" * 64)
    print("  SALES STRATEGY & CHANNELS (for human sales team)")
    print("=" * 64 + "\n")

    result = ask_engine("deepseek", prompt, use_web_search=False)
    print(result)

    print("\n" + "=" * 64)
    print("  Note: strategy + legitimate channels only. Real personal")
    print("  contacts require company CRM / proper data sources, not AI.")
    print("=" * 64)


if __name__ == "__main__":
    advise()