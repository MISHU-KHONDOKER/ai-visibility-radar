"""
agent_brain.py
--------------
THE TOP LAYER - the agent's "brain".

Reads the engine's REAL findings (visibility scorecard, top competitors,
customer candidates, category breakdown), then asks the AI to:
  1. SUMMARIZE what the data shows
  2. RECOMMEND concrete next actions to improve HEIDSTAR's visibility

HONEST SCOPE: the brain PROPOSES; humans DECIDE. It does not act on its
own or modify the engine. It turns results into an executive summary +
recommendations for the next round.
"""

import csv
import os
import json
from collections import Counter, defaultdict
from ask_engine import ask_engine
from foundation_loader import load_buyer_questions

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
_RESULTS = os.path.join(_PROJECT_ROOT, "data", "results.csv")
_CANDIDATES = os.path.join(_PROJECT_ROOT, "data", "customer_candidates.json")


def gather_findings():
    """Collect the engine's real findings into a compact text summary."""
    facts = []

    # --- Visibility from results.csv ---
    if os.path.exists(_RESULTS):
        with open(_RESULTS, "r", newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))

        total_appeared = total_measured = 0
        comp_counter = Counter()
        appeared_questions = []

        for r in rows:
            freq = r.get("heidstar_appeared", "")
            if "/" in freq:
                a, _, b = freq.partition("/")
                if a.isdigit() and b.isdigit():
                    total_appeared += int(a)
                    total_measured += int(b)
                    if int(a) > 0:
                        appeared_questions.append(r.get("question", ""))
            comps = r.get("competitors_named", "")
            for c in comps.split(";"):
                c = c.strip()
                if c:
                    comp_counter[c] += 1

        pct = (total_appeared / total_measured * 100) if total_measured else 0
        facts.append(f"HEIDSTAR overall AI visibility: {total_appeared}/{total_measured} ({pct:.1f}%).")
        if appeared_questions:
            uniq = list(set(appeared_questions))
            facts.append(f"HEIDSTAR appeared in these questions: {'; '.join(uniq[:5])}")
        else:
            facts.append("HEIDSTAR did not appear in any neutral question.")

        top_comps = "; ".join(f"{name}({cnt})" for name, cnt in comp_counter.most_common(8))
        facts.append(f"Most-named competitors: {top_comps}")

    # --- Customer candidates ---
    if os.path.exists(_CANDIDATES):
        with open(_CANDIDATES, "r", encoding="utf-8") as f:
            data = json.load(f)
        cands = data.get("candidates", [])
        facts.append(f"Customer candidates found so far: {len(cands)}.")
        types = Counter(c.get("type", "?") for c in cands)
        type_str = "; ".join(f"{t}: {n}" for t, n in types.most_common())
        facts.append(f"Candidate types: {type_str}")

    return "\n".join(facts)


def think():
    """Ask the AI to summarize the findings and recommend next actions."""
    findings = gather_findings()
    if not findings.strip():
        print("No findings yet. Run the engine first.")
        return

    print("=" * 64)
    print("  AGENT BRAIN - reading the engine's findings...")
    print("=" * 64)
    print("\nFINDINGS THE BRAIN IS REASONING OVER:\n")
    print(findings)

    prompt = f"""你是 HEIDSTAR（海德星，数字病理扫描仪源头工厂，主营OEM/ODM）的AI营销分析师。
以下是我们的AI可见度引擎本轮的真实发现：

{findings}

请基于这些真实数据，提供：

1. 【本轮总结】用3-4句话总结当前HEIDSTAR在AI搜索中的可见度状况。

2. 【关键洞察】2-3条最重要的发现（基于数据，不要编造）。

3. 【下一步建议】3-5条具体、可执行的建议，帮助提升HEIDSTAR的AI可见度。
   要具体（例如针对某个细分市场、某类信息源），不要空泛。

请用中文回答，条理清晰。这些是给人类决策者参考的建议，不是自动执行的指令。"""

    print("\n" + "=" * 64)
    print("  BRAIN'S ANALYSIS & RECOMMENDATIONS")
    print("=" * 64 + "\n")

    result = ask_engine("deepseek", prompt, use_web_search=False)
    print(result)

    print("\n" + "=" * 64)
    print("  Note: these are RECOMMENDATIONS for human review,")
    print("  not actions the agent takes on its own.")
    print("=" * 64)


if __name__ == "__main__":
    think()