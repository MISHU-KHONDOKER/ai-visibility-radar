from ask_engine import ask_engine
from save_result import save_result
from extract_intel_llm import extract_intel
from foundation_loader import load_buyer_questions

# How many times to ask each question (to handle noisy/borderline results).
REPEAT_COUNT = 3

# Load buyer questions from the shared data foundation (not hardcoded).
BUYER_QUESTIONS = [q["text"] for q in load_buyer_questions()]

ENGINES_TO_RUN = [
    {"name": "deepseek", "web_search": False},
    {"name": "qwen", "web_search": True},
]


def check_heidstar(answer):
    """Return True if HEIDSTAR appears in the answer."""
    return "海德星" in answer or "HEIDSTAR" in answer.upper()


def measure_once(engine_name, question, web):
    """
    Ask one question once. Returns (appeared_bool, answer) or (None, None) on failure.
    Wrapped in error handling so one bad call doesn't crash the whole run.
    """
    try:
        answer = ask_engine(engine_name, question, use_web_search=web)
        return check_heidstar(answer), answer
    except Exception as e:
        print(f"        ! call failed: {e}")
        return None, None


def run_all():
    total_q = len(BUYER_QUESTIONS)
    total_combos = total_q * len(ENGINES_TO_RUN)
    print(f"Running {total_combos} measurements x {REPEAT_COUNT} repeats each...\n")

    combo_count = 0
    for question in BUYER_QUESTIONS:
        for engine in ENGINES_TO_RUN:
            combo_count += 1
            name = engine["name"]
            web = engine["web_search"]
            tag = "web-search" if web else "no-search"

            print(f"[{combo_count}/{total_combos}] {name} ({tag})")
            print(f"        Q: {question}")

            # Ask the SAME question several times and count appearances.
            appeared_count = 0
            valid_runs = 0
            last_good_answer = ""

            for i in range(REPEAT_COUNT):
                appeared, answer = measure_once(name, question, web)
                if appeared is None:
                    continue  # this call failed; skip it, keep going
                valid_runs += 1
                if appeared:
                    appeared_count += 1
                    last_good_answer = answer
                elif not last_good_answer:
                    last_good_answer = answer  # keep an answer for intel extraction

            # Build a frequency result like "2/3".
            if valid_runs == 0:
                frequency = "FAILED"
                print(f"        Result: all calls failed")
            else:
                frequency = f"{appeared_count}/{valid_runs}"
                print(f"        Result: HEIDSTAR appeared {frequency} times")

            # Extract intelligence from one representative answer (if we have one).
            competitors = ""
            sources = ""
            if last_good_answer:
                try:
                    print(f"        Extracting intelligence...")
                    intel = extract_intel(last_good_answer)
                    competitors = "; ".join(intel["competitors"])
                    sources = "; ".join(intel["sources"])
                except Exception as e:
                    print(f"        ! extraction failed: {e}")

            # Save, with the frequency as the appearance result.
            save_result(
                engine=f"{name}-{tag}",
                question=question,
                heidstar_appeared=frequency,
                competitors_named=competitors,
                sources_cited=sources,
                answer=last_good_answer,
            )
            print()

    print(f"Done. All results saved to data/results.csv")


if __name__ == "__main__":
    run_all()