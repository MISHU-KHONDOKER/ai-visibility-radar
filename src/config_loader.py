import configparser
import os

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_THIS_DIR)
_CONFIG_PATH = os.path.join(_PROJECT_ROOT, "config", "config.ini")


def load_config():
    if not os.path.exists(_CONFIG_PATH):
        raise FileNotFoundError(
            f"\nCONFIG FILE MISSING. Expected at: {_CONFIG_PATH}\n"
            "FIX: copy config.example.ini to config.ini and add your keys.\n"
        )

    parser = configparser.ConfigParser()
    parser.read(_CONFIG_PATH, encoding="utf-8")

    settings = {}

    # Read each engine section we know about.
    for engine in ["deepseek", "qwen"]:
        if engine in parser:
            api_key = parser[engine].get("api_key", "").strip()
            base_url = parser[engine].get("base_url", "").strip()
            model = parser[engine].get("model", "").strip()

            # Only include it if the key was actually filled in.
            if api_key and not api_key.startswith(("PASTE", "sk-PASTE", "sk-YOUR")):
                settings[engine] = {
                    "api_key": api_key,
                    "base_url": base_url,
                    "model": model,
                }

    if not settings:
        raise ValueError(
            "No usable API keys found in config.ini. "
            "Open it and paste a real key into [deepseek] or [qwen]."
        )

    return settings


if __name__ == "__main__":
    try:
        cfg = load_config()
        print("Config loaded successfully. Engines found:")
        for engine, s in cfg.items():
            masked = s["api_key"][:6] + "..." + s["api_key"][-4:]
            print(f"  {engine}: key {masked}, model {s['model']}")
    except Exception as e:
        print("Config check FAILED:")
        print(e)