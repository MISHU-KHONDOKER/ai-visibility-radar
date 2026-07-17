from openai import OpenAI
from config_loader import load_config
import csv
import os
from datetime import datetime

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
_USAGE_LOG = os.path.join(_PROJECT_ROOT, "data", "usage_log.csv")


# Standard published prices, in RMB (yuan) per 1,000,000 tokens.
# These are approximate standard rates - used to ESTIMATE cost.
# (Your free quota currently covers actual usage at no charge.)
_PRICES_RMB_PER_M = {
    # model:          (input_price, output_price) per 1M tokens (RMB, standard rates)
    "qwen-plus":      (0.8, 2.0),
    "qwen-turbo":     (0.3, 0.6),
    "qwen-max":       (2.4, 9.6),
    "qwen3.7-plus":   (0.8, 4.8),   # Plus-tier reference rate (estimate; 8折 promo may apply)
    "qwen-math-turbo":(0.3, 0.6),
    "deepseek-chat":  (1.0, 2.0),
}


def _log_usage(engine_name, model, usage):
    """Append one row of token-usage + estimated cost to the usage log."""
    try:
        prompt_tokens = getattr(usage, "prompt_tokens", 0) or 0
        completion_tokens = getattr(usage, "completion_tokens", 0) or 0
        total_tokens = getattr(usage, "total_tokens", 0) or 0

        # Estimate cost at standard rates (input + output priced separately).
        in_price, out_price = _PRICES_RMB_PER_M.get(model, (0.0, 0.0))
        cost_rmb = (prompt_tokens / 1_000_000 * in_price
                    + completion_tokens / 1_000_000 * out_price)

        # Make sure the data folder exists.
        os.makedirs(os.path.dirname(_USAGE_LOG), exist_ok=True)

        # Write header if the file is new.
        new_file = not os.path.exists(_USAGE_LOG)
        with open(_USAGE_LOG, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            if new_file:
                writer.writerow(["datetime", "engine", "model",
                                 "prompt_tokens", "completion_tokens",
                                 "total_tokens", "est_cost_rmb"])
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                engine_name, model,
                prompt_tokens, completion_tokens, total_tokens,
                round(cost_rmb, 6),
            ])
    except Exception as e:
        # Logging must never break the main call.
        print(f"  (usage log warning: {e})")


def ask_engine(engine_name, question, use_web_search=False):
    """
    Ask a question to a chosen engine ('deepseek' or 'qwen').
    If use_web_search is True (Qwen only), the model searches the web first.
    Also logs token usage + estimated cost for each call.
    """
    cfg = load_config()

    if engine_name not in cfg:
        raise ValueError(
            f"Engine '{engine_name}' is not configured. "
            f"Available: {list(cfg.keys())}"
        )

    settings = cfg[engine_name]

    client = OpenAI(
        api_key=settings["api_key"],
        base_url=settings["base_url"],
    )

    extra = {}
    if use_web_search:
        extra["extra_body"] = {"enable_search": True}

    response = client.chat.completions.create(
        model=settings["model"],
        messages=[{"role": "user", "content": question}],
        **extra,
    )

    # Log token usage (real numbers from the API response).
    if getattr(response, "usage", None) is not None:
        _log_usage(engine_name, settings["model"], response.usage)

    answer = response.choices[0].message.content
    return answer


if __name__ == "__main__":
    test_q = "你好，请用一句话介绍你自己。"

    print("=== DeepSeek (no web search) ===")
    print(ask_engine("deepseek", test_q))
    print()

    print("=== Qwen (WITH web search) ===")
    print(ask_engine("qwen", test_q, use_web_search=True))

    print("\n(usage logged to data/usage_log.csv)")