"""
extract_intel.py
----------------
Reads an AI answer and extracts intelligence from it:
  - which known competitors are named
  - which known high-trust sources are cited
Uses simple known-name matching (fast, free, predictable).
Later this can be upgraded to LLM-powered extraction.
"""

# Known competitors, from our baseline data. Each entry is a list of
# spellings/aliases for the SAME company - if ANY alias appears, we count it.
KNOWN_COMPETITORS = {
    "江丰生物 (KFBIO)": ["江丰", "KFBIO", "KF-PRO", "KF-SCAN", "Konfoong"],
    "优纳科技 (Una)": ["优纳", "UNIC", "Una", "PRECICE"],
    "麦克奥迪 (Motic)": ["麦克奥迪", "Motic", "EasyScan"],
    "帝麦克斯 (DMax)": ["帝麦克斯", "DMax", "D-Max", "Dimax"],
    "泰立瑞 (TerryDr)": ["泰立瑞", "TerryDr", "Tailirui"],
    "谱华森 (Puhuasen)": ["谱华森", "Puhuasen", "PowerScin"],
    "舜宇 (Sunny)": ["舜宇", "Sunny", "SOPTOP"],
    "颂明医疗 (Songming)": ["颂明", "Songming"],
    "志盈 (Zhiying)": ["志盈", "Zhiying"],
    "滨松 (Hamamatsu)": ["滨松", "Hamamatsu"],
    "迪英加 (Deepwise)": ["迪英加", "Deepwise", "D-Scanner"],
    "华大智造 (MGI)": ["华大", "MGI", "BGI", "华大智造"],
    "生强科技 (Shengqiang)": ["生强", "Shengqiang", "SQS"],
    "永新光学 (Yongxin)": ["永新", "Yongxin", "Nexcope"],
    "兰丁高科 (Landing)": ["兰丁"],
    "徕卡 (Leica)": ["徕卡", "Leica", "Aperio"],
    "海康 (Hikvision)": ["海康"],
    "大华 (Dahua)": ["大华"],
}

# Known high-trust sources that AI engines cite.
KNOWN_SOURCES = {
    "仪器信息网 (Instrument.com.cn)": ["仪器信息网", "instrument.com"],
    "Made-in-China": ["made-in-china", "中国制造网"],
    "百度百科 (Baidu Baike)": ["百度百科", "baike.baidu"],
    "天眼查 (Tianyancha)": ["天眼查"],
    "爱企查 (Aiqicha)": ["爱企查"],
    "企查查 (Qichacha)": ["企查查"],
    "政府采购 (Gov procurement)": ["政府采购", "采购公告"],
    "NMPA / 药监局": ["药监", "NMPA", "医疗器械注册"],
    "公司官网 (Company website)": ["官网", ".com"],
    "CMEF / 展会 (Expo)": ["CMEF", "展会", "Medtec"],
}


def find_matches(answer, known_dict):
    """Return the list of known items whose aliases appear in the answer."""
    found = []
    for name, aliases in known_dict.items():
        for alias in aliases:
            if alias.lower() in answer.lower():
                found.append(name)
                break  # found this one, no need to check its other aliases
    return found


def extract_competitors(answer):
    """Return the list of known competitors named in the answer."""
    return find_matches(answer, KNOWN_COMPETITORS)


def extract_sources(answer):
    """Return the list of known sources cited in the answer."""
    return find_matches(answer, KNOWN_SOURCES)


# Self-test with a small sample.
if __name__ == "__main__":
    sample = "国内有江丰生物、优纳科技和麦克奥迪。信息来源：百度百科、天眼查。"
    print("Competitors found:", extract_competitors(sample))
    print("Sources found:", extract_sources(sample))