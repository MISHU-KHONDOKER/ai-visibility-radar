# CLAUDE.md

Guidance for working in this repository.

## What this project is

An **AI-visibility measurement & sales-intelligence engine** for **HEIDSTAR** (海德星科技（厦门）有限公司), a Xiamen-based digital-pathology slide-scanner manufacturer whose business is ~80% **OEM/ODM** (a "源头工厂" / source factory).

The core question it answers: **when Chinese buyers ask AI assistants (DeepSeek, Qwen) to recommend pathology-scanner makers, does HEIDSTAR get named — and if not, who does?** It then turns those findings into competitor intelligence, customer leads, and sales strategy.

This is an **internal marketing-intelligence tool**, not a customer-facing product. It is read-heavy: it *diagnoses and recommends*; humans act on the recommendations. Current headline result: **HEIDSTAR appears ~1.8% of the time (3/168)**, only via Qwen web-search, only in the cervical-cancer-screening application lane; 0% on DeepSeek (model memory) and 0% in general/OEM-ODM queries.

**Guiding principle throughout the codebase: measure honestly, let humans decide.** The code deliberately refuses to fabricate — no unverified NMPA certs, no invented customer contacts, no unverified competitor claims. Preserve this discipline in any changes.

## Tech stack

- **Python 3** (venv in `venv/`)
- **OpenAI Python SDK** (`openai`) pointed at OpenAI-compatible Chinese endpoints — **DeepSeek** and **Qwen/DashScope (Alibaba Bailian 百炼)**. No Anthropic/OpenAI-proper usage.
- **Streamlit + Plotly + pandas** for `dashboard.py`
- Storage is **flat files only** — CSV + JSON. No database.
- Key deps: `openai`, `pydantic`, `httpx`, `tqdm` (see `requirements.txt`).

## Two-engine design (important)

Measurements run against two engines on purpose:

- **`deepseek`** (no web search) — tests *"what does the AI's trained memory say?"* (hardest to change).
- **`qwen`** (web search **on** via `extra_body={"enable_search": True}`) — tests *"what does the live web say right now?"* (changeable via SEO / PR work).

Web search (`enable_search`) is an **Alibaba DashScope-only** feature. It is used in exactly one role: the Qwen measurement calls. Everything else (extraction, filtering, strategy) runs on **DeepSeek with no search**. A local model or a math model (`qwen-math-turbo`) **cannot** serve the Qwen role — they don't support `enable_search`.

## Architecture (5 layers)

1. **Foundation** (`foundation/*.json`) — single source of truth. Read via `src/foundation_loader.py`.
   - `product_knowledge.json` — HEIDSTAR ground-truth (4 scanner models; only HDS-MSCAN-200A has confirmed NMPA).
   - `buyer_questions.json` — 19 neutral Chinese buyer questions, 5 categories (general/oem_odm/application/buyer_context/comparison). **Questions must NOT name HEIDSTAR** (measures unprompted recommendation).
   - `competitors_and_sources.json` — ~28 tracked competitors (aliases, tiers, AI-mention counts) + high-trust source map. This file gets mutated by tooling (with `.backup*` copies).
   - `customers.json` — real customer DB (verified wins only).
   - **Note (public repo):** the live business-data files — `customers.json`, `competitors_and_sources.json` (+ `.backup*`) — are gitignored and NOT published. Ship `*.sample.json` templates instead; copy a sample to the real filename to run locally (see README).
2. **Measurement pipeline** — `config_loader` → `ask_engine` → `run_measurement` → `save_result` → `data/results.csv`.
3. **Intelligence layer** (reads `results.csv`) — `extract_intel` / `extract_intel_llm`, `track_competitors`, `find_new_entrants`, `oem_odm_view`, `source_mapping`, `category_breakdown`; foundation upkeep loop: `find_new_entrants` → `filter_companies_llm` → `promote_entrants`.
4. **Reporting** — `heidstar_scorecard` (flagship, writes `HEIDSTAR_Scorecard.md`), `show_win`, `summarize`, `usage_summary`, `run_summary`.
5. **Agent + front-end** — `agent_brain` (strategy summary), `sales_advisor` (sales strategy), `run_agent` (pipeline orchestrator), `dashboard.py` (Streamlit UI).

## Key modules

`src/ask_engine.py` is the heart: `ask_engine(engine_name, question, use_web_search=False)` builds an OpenAI client from config, calls chat completions, and logs tokens + estimated RMB cost to `data/usage_log.csv`. All LLM calls go through it. Model name comes from config, not hardcoded.

## Data schemas

- **`data/results.csv`** (utf-8-sig): `date, engine, question, heidstar_appeared, competitors_named, sources_cited, answer`
  - `engine` is like `deepseek-no-search` / `qwen-web-search`.
  - `heidstar_appeared` is a **frequency string** (`"2/3"`, `"3/3"`, `"FAILED"`) — each question is asked `REPEAT_COUNT = 3` times. **Not** "YES"/"NO".
  - `competitors_named` / `sources_cited` are `; `-separated.
- **`data/usage_log.csv`** (utf-8-sig): `datetime, engine, model, prompt_tokens, completion_tokens, total_tokens, est_cost_rmb`
- **`data/customer_candidates.json`**: `{"candidates": [{name, type, country, detail, source_query, status}]}` (status usually `"unverified"`).
- **`foundation/customers.json`**: customers array of `{id: "cust_NNN", name_zh, name_en, type, segment, region, country, product_used, relationship, source, notes}`.

## Running things

Run from `src/` (modules use `_PROJECT_ROOT = parent of src/` path resolution and import siblings directly).

- Pipeline orchestrator: `python src/run_agent.py` (cheap; analysis on existing data) or `python src/run_agent.py --full` (expensive; fresh measurement + wide customer search).
- Individual tools: `python src/heidstar_scorecard.py`, `track_competitors.py`, `oem_odm_view.py`, `find_new_entrants.py`, `category_breakdown.py`, `show_candidates.py`, etc.
- Expensive (cost real API tokens): `run_measurement.py` (~150 calls), `find_customers_wide.py` (~40 searches), `find_procurement.py`, `verify_oem_odm.py`.
- Dashboard: `streamlit run dashboard.py` (password-gated; shells out to the src tools via subprocess).
- Add a real customer: `python src/add_customer.py` (interactive; backs up first). Promotion candidate→customer is intentionally manual/human-gated.

## Config

`config/config.ini` (gitignored) has sections `[deepseek]`, `[qwen]`, `[dashboard]`, each with `api_key` / `base_url` / `model` (and `[dashboard] password`). `config_loader.py` only auto-loads `deepseek` and `qwen` — to add a new engine, add it there **and** to `ENGINES_TO_RUN` in `run_measurement.py`.

Current config: DeepSeek = `deepseek-chat`; Qwen = `qwen3.7-plus` (Plus tier, supports web search). Cheaper Qwen alternatives that also support search: `qwen-turbo`, `qwen-flash`.

## Environment gotchas (important)

- **A proxy may be required for outbound internet.** Some networks cannot reach DeepSeek/Qwen/DashScope directly. If so, set `HTTPS_PROXY`/`HTTP_PROXY` to your proxy before any command that hits the internet.
- **Windows + PowerShell** is the primary shell; a Git Bash tool is also available.
- Bailian/DashScope's OpenAI-compatible API has **no billing/quota endpoint** — remaining free tokens and balance are only visible in the console (`bailian.console.aliyun.com`). qwen3.7-plus is pay-as-you-go from Alibaba Cloud account balance. The `/compatible-mode/v1/models` endpoint lists available models but not pricing/quota.

## Known issues / cleanup opportunities

- `src/summarize.py` is **stale** — it tallies `heidstar_appeared` as `"YES"/"NO"`, but the pipeline writes frequency strings (`"2/3"`), so its counts read 0. `heidstar_scorecard.py` superseded it.
- Dead/duplicate code: `find_customers.py` imports `load_product_knowledge` but never uses it; `normalize_names.py` is written as a shared helper but imported by only one module (others reimplement their own `canonicalize`); `add_customer.py` ID scheme (`len+1`) can collide if a record is deleted.
- Dashboard metric cards (`19` questions, `165+` competitors, `84` leads) are **hard-coded**, not computed from data.

## Conventions

- All CSVs are opened `encoding="utf-8-sig"` (BOM-tolerant). JSON written with `ensure_ascii=False, indent=2`.
- Mutating scripts back up the target file first (`.backup`, `.backup2`, `.backup3`) before writing.
- LLM extraction/filter functions are **fail-safe**: on parse error they return empty/unchanged rather than crashing the pipeline.
- Strategy/agent modules print Chinese output and are framed as *recommendations for humans*, never auto-execution.
- Prefer keeping tools as small, single-purpose scripts glued by shared CSV/JSON files and the one `ask_engine` wrapper.
