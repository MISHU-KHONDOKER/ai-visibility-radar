# HEIDSTAR AI-Visibility & Sales-Intelligence Engine

An internal marketing-intelligence tool that measures **how often Chinese AI assistants (DeepSeek, Qwen) recommend HEIDSTAR** — a Xiamen-based digital-pathology slide-scanner manufacturer and OEM/ODM source factory — when buyers ask for scanner makers, and turns those findings into competitor intelligence, customer leads, and sales strategy.

The core question: *when a buyer asks an AI to recommend pathology-scanner manufacturers, does HEIDSTAR get named — and if not, who does?*

> **Guiding principle: measure honestly, let humans decide.** The code deliberately refuses to fabricate — no unverified NMPA certs, no invented customer contacts, no unverified competitor claims. It diagnoses and recommends; humans act on the recommendations.

## Two-engine design

Measurements run against two engines on purpose:

- **DeepSeek** (no web search) — tests *"what does the AI's trained memory say?"* (hardest to change).
- **Qwen / Alibaba DashScope** (web search on) — tests *"what does the live web say right now?"* (changeable via SEO / PR).

Web search (`enable_search`) is a DashScope-only feature, used only in the Qwen measurement role.

## Tech stack

- Python 3
- OpenAI Python SDK pointed at OpenAI-compatible Chinese endpoints (DeepSeek, Qwen/DashScope)
- Streamlit + Plotly + pandas for the dashboard
- Flat-file storage only (CSV + JSON) — no database

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API keys
cp config/config.example.ini config/config.ini
#   then edit config/config.ini and add your DeepSeek + Qwen/DashScope keys
#   (config/config.ini is gitignored and must never be committed)

# 4. Seed local data from the provided samples
cp foundation/customers.sample.json                foundation/customers.json
cp foundation/competitors_and_sources.sample.json  foundation/competitors_and_sources.json
cp data/customer_candidates.sample.json            data/customer_candidates.json
cp data/results.sample.csv                         data/results.csv
```

> Some networks require an outbound proxy to reach DeepSeek/Qwen/DashScope. If so, set
> `HTTP_PROXY` / `HTTPS_PROXY` before running any command that hits the internet.

## Running

Individual analysis tools (cheap; read existing data):

```bash
python src/heidstar_scorecard.py     # flagship scorecard
python src/track_competitors.py      # competitor visibility
python src/oem_odm_view.py           # OEM/ODM lens
python src/category_breakdown.py     # results by question category
```

Pipeline orchestrator:

```bash
python src/run_agent.py              # cheap: analysis on existing data
python src/run_agent.py --full       # EXPENSIVE: fresh measurement + wide customer search (real API cost)
```

Dashboard (password-gated; password comes from `config.ini` → `[dashboard]`):

```bash
streamlit run dashboard.py
```

## Data & privacy note

This is an internal tool. The public repository ships with **illustrative `*.sample.*` data only** — real customer records, sales leads, competitor tracking, and measurement results are **not** included and are gitignored. Populate your own data from real, verified sources.

## Architecture (5 layers)

1. **Foundation** (`foundation/*.json`) — single source of truth (product ground-truth, neutral buyer questions, competitor/source map, customer DB).
2. **Measurement pipeline** — `config_loader` → `ask_engine` → `run_measurement` → `save_result` → `data/results.csv`.
3. **Intelligence layer** — competitor tracking, new-entrant discovery, OEM/ODM view, source mapping, category breakdown.
4. **Reporting** — scorecard, wins, usage/cost summaries.
5. **Agent + front-end** — strategy summaries, sales advisor, pipeline orchestrator, Streamlit dashboard.

See `CLAUDE.md` for detailed developer guidance.

## License

Copyright © 2026 HEIDSTAR CO., LTD (海德星科技（厦门）有限公司). All Rights Reserved.
Proprietary — see [LICENSE](LICENSE). Provided for reference only; no reuse without written permission.
