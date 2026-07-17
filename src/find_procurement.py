"""
find_procurement.py
-------------------
Searches (via Qwen web-search) for recent procurement/tender activity
for pathology scanners - surfacing REAL hospitals/institutions that are
buying, as candidate customers to review and add to the database.

HONEST LIMITS: web-search results are not comprehensive or guaranteed
current. Treat every result as a CANDIDATE to verify, not a confirmed fact.
"""

import json
from ask_engine import ask_engine


# Search queries aimed at real procurement records.
_PROCUREMENT_QUERIES = [
    "最近 数字病理扫描仪 医院 招标 中标 公告",
    "病理切片扫描仪 政府采购 中标结果",
    "宫颈癌筛查 病理扫描仪 采购项目 中标",
]


_EXTRACT_INSTRUCTION = """你是一个采购信息提取助手。请阅读下面的文本，找出其中提到的
【真实的医院/机构采购病理扫描仪】的记录。

对每一条，提取：
- buyer: 采购方名称（医院/机构）
- product: 采购的设备（如有）
- supplier: 中标供应商（如有，可为空）
- date: 时间（如有）
- detail: 简短说明

只提取文本中【明确出现】的采购记录。不要编造。如果没有明确记录，返回空数组。

只返回 JSON，格式严格如下：
{"procurements": [
  {"buyer": "...", "product": "...", "supplier": "...", "date": "...", "detail": "..."}
]}

需要分析的文本如下：
"""


def search_procurement():
    print("Searching for recent pathology-scanner procurement records...")
    print("(Web-search results - treat each as a CANDIDATE to verify.)\n")

    all_records = []

    for query in _PROCUREMENT_QUERIES:
        print(f"--- Query: {query} ---")
        try:
            # 1. Web-search for procurement activity.
            answer = ask_engine("qwen", query, use_web_search=True)

            # 2. Extract structured procurement records from the answer.
            prompt = _EXTRACT_INSTRUCTION + answer
            raw = ask_engine("deepseek", prompt, use_web_search=False)
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
            data = json.loads(cleaned)
            records = data.get("procurements", [])

            if not records:
                print("  (no clear procurement records found)\n")
                continue

            for r in records:
                print(f"  • Buyer:    {r.get('buyer','?')}")
                print(f"    Product:  {r.get('product','')}")
                print(f"    Supplier: {r.get('supplier','')}")
                print(f"    Date:     {r.get('date','')}")
                print(f"    Detail:   {r.get('detail','')}")
                print()
                all_records.append(r)

        except Exception as e:
            print(f"  (search/extract failed: {e})\n")

    print("=" * 60)
    if all_records:
        print(f"Found {len(all_records)} candidate procurement record(s).")
        print("REVIEW each one. For real ones, add the buyer to your")
        print("customer database with: python add_customer.py")
    else:
        print("No candidate records found this run. Procurement data is")
        print("patchy via web-search; the comprehensive way needs direct")
        print("access to procurement platforms (a larger future build).")
    print("=" * 60)


if __name__ == "__main__":
    search_procurement()