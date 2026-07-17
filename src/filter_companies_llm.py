"""
filter_companies_llm.py
-----------------------
Uses an LLM to filter a list of extracted names, keeping only the ones
that are real COMPANIES (removing categories, generic terms, noise).
Reuses the 'structured output' technique (LLM returns clean JSON).
"""

import json
from ask_engine import ask_engine


_FILTER_INSTRUCTION = """你是一个信息筛选助手。下面是从AI回答中提取出来的一组名称。
请判断每一个是否是一个【真实的公司/厂商名称】。

保留：真实的公司、厂商、品牌名称（中文或英文均可）。
删除：不是公司的内容，例如：
- 行业类别或产品类别（如"数字病理"、"病理扫描仪"）
- 通用词语或描述（如"公开资料"、"行业信息"、"测量"、"检测"）
- 医院、医学院等非厂商机构
- 明显残缺或无意义的片段

只返回 JSON，不要任何其他文字或 markdown。
格式严格如下：
{"companies": ["真实公司1", "真实公司2"]}

需要筛选的名称列表如下：
"""


def filter_real_companies(names):
    """
    Take a list of names, return only the ones the LLM judges to be real
    companies. Returns the filtered list. On any failure, returns the
    original list unchanged (fail-safe - never lose data).
    """
    if not names:
        return []

    # Build the prompt: rules + the list of names as text.
    names_text = "\n".join(f"- {n}" for n in names)
    full_prompt = _FILTER_INSTRUCTION + names_text

    try:
        raw = ask_engine("deepseek", full_prompt, use_web_search=False)

        # Clean possible ```json fences.
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

        data = json.loads(cleaned)
        kept = data.get("companies", [])

        # Safety: only keep names that were actually in the original list
        # (so the LLM can't invent or alter names).
        kept = [n for n in kept if n in names]
        return kept

    except Exception as e:
        print(f"  (filter failed, keeping all names: {e})")
        return names  # fail-safe: never lose candidates on error


# Self-test with a mix of real companies and noise.
if __name__ == "__main__":
    sample = [
        "华银健康", "数字病理", "莱测测量", "安必平",
        "公开资料", "广州明美", "病理扫描仪", "3DHISTECH",
    ]
    print("Original:", sample)
    print("Filtered:", filter_real_companies(sample))