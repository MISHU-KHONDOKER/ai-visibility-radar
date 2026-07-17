"""
extract_intel_llm.py
--------------------
Uses an LLM (DeepSeek) to READ an AI answer and extract structured
intelligence: the companies named and the sources cited.

This teaches 'structured output' - making an LLM return clean JSON
that code can use, instead of chatty prose.
"""

import json
from ask_engine import ask_engine


# This is the INSTRUCTION (the "prompt") we give DeepSeek.
# Sharpened to clearly separate real SOURCES from customers/hospitals/noise.
_EXTRACTION_INSTRUCTION = """你是一个信息提取助手。请阅读下面的文本，提取出两类信息：

1. competitors: 文本中提到的所有公司/厂商/品牌名称（数组）。
   只提取真实的公司或品牌，不要提取产品类别、技术名词或医院。

2. sources: 文本中明确引用的【信息来源】（数组）。
   【信息来源】指信息从哪里来，例如：
   - 网站或平台（如：仪器信息网、百度百科、中国制造网、天眼查、企查查）
   - 行业报告、新闻报道、公开资料
   - 招标公告、中标结果、政府采购记录、产品备案/认证资料
   - 公司官网

   【重要】以下内容【不是】信息来源，不要放进 sources：
   - 医院、医学院、医疗机构（如：华山医院、江苏省中医院）——这些是客户或应用案例，不是信息来源
   - 公司或厂商名称（它们属于 competitors）
   - 产品名称、技术名词、产品类别

只返回 JSON，不要返回任何其他文字、解释或 markdown 标记。
格式必须严格如下：
{"competitors": ["公司1", "公司2"], "sources": ["来源1", "来源2"]}

如果某一类没有内容，返回空数组 []。

需要分析的文本如下：
"""


def extract_intel(answer):
    """
    Send an answer to DeepSeek and get back {"competitors": [...], "sources": [...]}.
    Returns a Python dictionary.
    """
    # 1. Build the full instruction: the rules + the actual text to analyse.
    full_prompt = _EXTRACTION_INSTRUCTION + answer

    # 2. Ask DeepSeek (no web search needed - it's just reading text).
    raw_reply = ask_engine("deepseek", full_prompt, use_web_search=False)

    # 3. Clean the reply - LLMs sometimes wrap JSON in ```json ... ``` markers.
    cleaned = raw_reply.strip()
    if cleaned.startswith("```"):
        # remove the first line (```json) and the last line (```)
        cleaned = cleaned.split("\n", 1)[-1]      # drop first line
        cleaned = cleaned.rsplit("```", 1)[0]     # drop closing ```
        cleaned = cleaned.strip()

    # 4. Parse the JSON text into a real Python dictionary.
    try:
        data = json.loads(cleaned)
        competitors = data.get("competitors", [])
        sources = data.get("sources", [])
        return {"competitors": competitors, "sources": sources}
    except json.JSONDecodeError:
        # If the LLM returned something unparseable, fail safely.
        print("  (warning: could not parse extraction, got:", repr(raw_reply[:100]), ")")
        return {"competitors": [], "sources": []}


# Self-test on a real-ish sample.
if __name__ == "__main__":
    sample = (
        "国内病理扫描仪厂家有江丰生物、优纳科技、麦克奥迪等。"
        "这些设备已在华山医院、江苏省中医院装机使用。"
        "信息来源：百度百科、仪器信息网、天眼查、招标公告。"
    )
    result = extract_intel(sample)
    print("Competitors:", result["competitors"])
    print("Sources:", result["sources"])