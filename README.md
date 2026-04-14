# Agentic Patterns for Oil & Gas — Databricks + Claude

Practical notebooks demonstrating five LLM agentic patterns applied to real Oil & Gas operational scenarios, running on **Databricks Foundation Models** (Claude Sonnet 4.6).

## Why These Patterns?

Raw O&G operational data — SCADA telemetry, alarm feeds, well logs, incident reports — is rarely decision-ready. These patterns bridge the gap between raw data and actionable insight, at field scale.

## Patterns & Notebooks

| Pattern | Notebook | O&G Use Case |
|---|---|---|
| **Prompt Chaining** | `og_chaining.ipynb` | SCADA telemetry → extract → normalize → flag anomalies → executive summary |
| **Parallelization** | `basic_workflows.ipynb` | Fleet-wide equipment screening across hundreds of wells simultaneously |
| **Routing** | `basic_workflows.ipynb` | Control room alarm triage → wellbore integrity / process safety / equipment fault |
| **Orchestrator-Workers** | `orchestrator_workers.ipynb` | Dynamic well performance investigation — orchestrator decides which analyses to run |
| **Evaluator-Optimizer** | `evaluator_optimizer.ipynb` | Iterative safe work procedure generation against HSE golden rules |

## Setup

### Prerequisites
- Databricks workspace with Foundation Model endpoints enabled
- Claude Sonnet 4.6 endpoint: `databricks-claude-sonnet-4-6`

### Running on Databricks
Upload notebooks to your workspace. The `util.py` auto-detects credentials:

```python
# Inside a Databricks notebook — no config needed
token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
host  = spark.conf.get("spark.databricks.workspaceUrl")
```

### Running Locally (for testing)
```bash
pip install openai jupyter

export DATABRICKS_HOST="your-workspace.azuredatabricks.net"
export DATABRICKS_TOKEN="your-pat-token"

jupyter notebook databricks/og_chaining.ipynb
```

## How `util.py` Works

Databricks Foundation Models expose an **OpenAI-compatible** endpoint at:
```
POST https://{host}/serving-endpoints/{model}/invocations
```

`util.py` wraps this with a simple `llm_call()` function that auto-detects whether it's running inside a Databricks notebook or locally:

```python
from util import llm_call

result = llm_call(
    prompt="Analyze this well data...",
    system_prompt="You are a production engineer.",
    model="databricks-claude-sonnet-4-6"
)
```

## Available Claude Endpoints (Azure Databricks)

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

### Orchestrator-Workers (`orchestrator_workers.ipynb`)
Unlike simple parallelization, the orchestrator determines *at runtime* which analyses to run based on the specific input. For well performance investigations, the subtasks (decline curve analysis, water cut review, choke correlation) depend on what the data actually shows — you can't predefine them.

### Evaluator-Optimizer (`evaluator_optimizer.ipynb`)
Generator → Evaluator → loop until PASS. In O&G, safety procedures, well programs, and regulatory submissions have hard quality requirements. This automates the review-revise cycle against defined criteria.

## Contributing
PRs welcome. See issues for planned additions:
- Parallelization: multi-well production screening notebook
- Routing: control room alarm triage notebook  
- Evaluator-Optimizer: HSE safe work procedure notebook

## License
MIT
