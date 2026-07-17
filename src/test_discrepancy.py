from ask_engine import ask_engine

def check(answer):
    return "YES" if ("海德星" in answer or "HEIDSTAR" in answer.upper()) else "NO"

# The exact phrase you want to test (English, neutral - doesn't name HEIDSTAR):
question = "OEM and ODM pathology scanner manufacturers in China, please recommend good ones"

print("=== DeepSeek (no web search) ===")
ans1 = ask_engine("deepseek", question, use_web_search=False)
print("HEIDSTAR appeared:", check(ans1))
print(ans1[:800])
print()

print("=== Qwen (WITH web search) ===")
ans2 = ask_engine("qwen", question, use_web_search=True)
print("HEIDSTAR appeared:", check(ans2))
print(ans2[:800])