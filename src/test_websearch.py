from openai import OpenAI
from config_loader import load_config

cfg = load_config()
settings = cfg["qwen"]

client = OpenAI(api_key=settings["api_key"], base_url=settings["base_url"])

# Ask something that REQUIRES fresh web info, to force a search.
response = client.chat.completions.create(
    model=settings["model"],
    messages=[{"role": "user", "content": "海德星科技（厦门）有限公司是做什么的？请介绍这家公司，并说明信息来源。"}],
    extra_body={"enable_search": True},
)

print("=== ANSWER ===")
print(response.choices[0].message.content)
print()
print("=== SEARCH INFO (did it actually search?) ===")
# The search results often come back in the raw response. Let's inspect it.
print(response.model_dump_json(indent=2)[:3000])