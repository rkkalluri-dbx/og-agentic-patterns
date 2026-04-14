# Agentic Patterns for Oil & Gas — Databricks + Claude

Practical notebooks demonstrating five LLM agentic patterns applied to real Oil & Gas operational scenarios, running on **Databricks Foundation Models** (Claude Sonnet 4.6).

## Why These Patterns?

Raw O&G operational data — SCADA telemetry, alarm feeds, well logs, incident reports — is rarely decision-ready. These patterns bridge the gap between raw data and actionable insight, at field scale.

## Patterns & Notebooks

| Pattern | Notebook | O&G Use Case |
|---|---|---|
| **Prompt Chaining** | [`og_chaining.ipynb`](databricks/og_chaining.ipynb) | SCADA telemetry → extract → normalize → flag anomalies → executive summary |
| **Parallelization** | [`og_parallelization.ipynb`](databricks/og_parallelization.ipynb) | Fleet-wide compressor health screening across all assets simultaneously |
| **Routing** | [`og_routing.ipynb`](databricks/og_routing.ipynb) | Control room alarm triage → wellbore integrity / process safety / equipment fault / environmental |
| **Orchestrator-Workers** | [`og_orchestrator_workers.ipynb`](databricks/og_orchestrator_workers.ipynb) | Dynamic well performance investigation — orchestrator decides which analyses to run at runtime |
| **Evaluator-Optimizer** | [`og_evaluator_optimizer.ipynb`](databricks/og_evaluator_optimizer.ipynb) | Iterative safe work procedure drafting against 7 HSE golden rules |

## Setup

### Prerequisites
- Databricks workspace with Foundation Model endpoints enabled
- Claude Sonnet 4.6 endpoint: `databricks-claude-sonnet-4-6`

### Running on Databricks (via Asset Bundles)

```bash
# Clone and deploy all jobs
git clone https://github.com/rkkalluri-dbx/og-agentic-patterns.git
cd og-agentic-patterns

databricks bundle validate
databricks bundle deploy

# Run individual patterns
databricks bundle run og_chaining
databricks bundle run og_parallelization
databricks bundle run og_routing
databricks bundle run og_orchestrator_workers
databricks bundle run og_evaluator_optimizer
```

### Running Locally (for testing)
```bash
pip install openai jupyter

export DATABRICKS_HOST="your-workspace.azuredatabricks.net"
export DATABRICKS_TOKEN="your-pat-token"

jupyter notebook databricks/og_chaining.ipynb
```

## How `util.py` Works

Databricks Foundation Models expose an **OpenAI-compatible** endpoint. `util.py` auto-detects credentials whether running inside a Databricks notebook or locally:

```python
from util import llm_call

result = llm_call(
    prompt="Analyze this well data...",
    system_prompt="You are a production engineer.",
    model="databricks-claude-sonnet-4-6"  # default
)
```

Inside a Databricks notebook, credentials are fetched automatically via `dbutils` — no manual configuration needed.

## Available Claude Endpoints

| Endpoint | Model |
|---|---|
| `databricks-claude-sonnet-4-6` | Claude Sonnet 4.6 (default) |
| `databricks-claude-opus-4-6` | Claude Opus 4.6 |
| `databricks-claude-haiku-4-5` | Claude Haiku 4.5 |

## Pattern Deep Dive

### Prompt Chaining (`og_chaining.ipynb`)
Four sequential steps, each building on the last:
1. **Extract** — faithful transcription from raw SCADA text, no interpretation
2. **Normalize** — unit conversions (m³→bbl, Mscf→MMscfd) with conversion audit trail
3. **Flag** — compare against field targets, identify anomalies and data quality issues
4. **Summarize** — executive-ready daily report with prioritized actions

A single prompt attempting all four degrades quality. Chaining keeps each step focused on one reasoning mode.

### Parallelization (`og_parallelization.ipynb`)
Runs the same analysis concurrently across all assets using `ThreadPoolExecutor`. Eight compressors screened simultaneously — same wall time as one. Scales directly to hundreds of wells or facilities.

### Routing (`og_routing.ipynb`)
An LLM classifier first categorizes the incoming alarm signal (5 routes: wellbore integrity, process safety, equipment fault, environmental, pipeline integrity), then a specialized prompt handles it. Each route gets the right response template and escalation path automatically.

### Orchestrator-Workers (`og_orchestrator_workers.ipynb`)
Unlike parallelization, the subtasks are not predefined — they emerge from what the data shows. The orchestrator reads well data and selects 2–4 investigations at runtime (liquid loading, water source, gas coning, decline curve, etc.). Workers execute each independently; a synthesis step produces a root cause recommendation.

### Evaluator-Optimizer (`og_evaluator_optimizer.ipynb`)
Generator → Evaluator → loop until score ≥ 80/100. The evaluator checks each draft against 7 HSE golden rules (permit specificity, PPE detail, LOTO steps, emergency coverage, regulatory citations, stepwise controls, sign-off authority). Typical progression: 55–65 on the first draft → 80+ after 2–3 iterations.

## License
MIT
