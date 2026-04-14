# 5 Agentic AI Patterns for Oil & Gas Operations on Databricks

*How we applied prompt chaining, parallelization, routing, orchestrator-workers, and evaluator-optimizer to real O&G scenarios using Claude Sonnet 4.6 on Databricks Foundation Models*

---

## The Problem

Oil and gas operations generate enormous volumes of data. SCADA systems record wellhead pressures and rates every 15 seconds. Control rooms process thousands of alarms per shift. Engineers write safe work procedures before every non-routine task. Wells send signals that take a trained eye to interpret.

The data exists. The domain knowledge exists. The gap is between raw operational data and a decision-ready output — an anomaly flagged, an alarm triaged, a procedure approved, a root cause identified.

Large language models can close that gap. But a single prompt asking a model to "analyze this well data and tell me what to do" is not reliable at scale. The five agentic patterns below are a more principled approach: each pattern is the right tool for a specific class of problem.

All five were built as Databricks notebooks, running on `databricks-claude-sonnet-4-6` via Databricks Foundation Models, and deployed as scheduled jobs using Databricks Asset Bundles.

---

## Pattern 1: Prompt Chaining — Sequential Data Transformation

**When to use it:** When a task requires multiple reasoning modes in sequence and a single prompt would degrade quality by conflating them.

### The O&G scenario

A field operator submits raw SCADA text at end of shift — mixed units, handwritten notes, flagged readings, some entries clearly wrong. The goal: a clean, prioritized daily operations report ready for the asset manager.

### How it works

We decomposed the task into four discrete steps, each feeding into the next:

1. **Extract** — faithful transcription only. The model pulls structured data from unstructured text without interpreting or correcting anything.
2. **Normalize** — unit conversion with an audit trail. m³ to bbl, Mscf to MMscfd, kPa to psi. Every conversion is logged.
3. **Flag** — anomaly detection. Each reading is compared against field targets. Values outside tolerance are flagged with severity and likely cause.
4. **Summarize** — executive report. A narrative summary with prioritized action items, the right engineer assigned to each.

### What it found

On the Permian Basin Block 7 test dataset:

- **Well C-22**: Tubing pressure dropped 54% overnight with concurrent rate decline — flagged as probable liquid loading, assigned to production engineer
- **Well A-17**: Gas rate reported as 18,500 Mscf/d against a 450 Mscf/d target — flagged as physically implausible, likely a units error or transcription mistake
- **Well B-09**: GOR rising month-over-month on a new well — flagged for reservoir engineer review

### Why not one prompt?

Each step requires a different cognitive mode: faithful transcription, arithmetic, comparative analysis, narrative synthesis. Asking for all four in one prompt produces output that compromises between them. Chaining keeps each step honest.

---

## Pattern 2: Parallelization — Fleet-Scale Operations

**When to use it:** When the same analysis needs to run across many assets and sequential execution is too slow.

### The O&G scenario

A midstream operator needs to screen the health of every compressor in their fleet — vibration trends, pressure differentials, temperature exceedances, maintenance history — and produce a prioritized intervention list before the morning shift meeting.

Sequential LLM calls across a 200-compressor fleet would take hours. Parallelization runs all of them simultaneously.

### How it works

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=8) as executor:
    futures = {executor.submit(screen_compressor, c): c for c in compressors}
    results = [futures[f].result() for f in futures]
```

Same prompt, many inputs, concurrent execution. The wall time is bounded by the slowest single call, not the sum of all calls.

### What it enables

- Fleet-wide compressor health screening
- Multi-well production optimization runs
- Portfolio-level regulatory compliance checks
- Daily anomaly detection across all assets

The pattern scales linearly with workforce capacity. Eight compressors or 800 — same wall time.

---

## Pattern 3: Routing — Mixed-Domain Alarm Triage

**When to use it:** When a single input stream contains signals that require fundamentally different handling, and the correct handler depends on the content of the signal.

### The O&G scenario

A control room operator monitors alarms from drilling, production, pipelines, and facilities simultaneously. A high-pressure alarm on a Christmas tree needs a different response than a motor overtemperature on a compressor, which needs a different response than an H2S detection at the separator.

Each alarm type has its own response template, urgency classification, and escalation path. Routing automates the dispatch.

### How it works

Step 1: A classifier LLM reads the alarm text and outputs structured XML:

```xml
<reasoning>Sudden casing pressure spike with associated gas reading...</reasoning>
<route>wellbore_integrity</route>
<urgency>critical</urgency>
```

Step 2: The classified route selects a specialized prompt — each with the right response structure, regulatory references, and escalation contacts for that domain.

### The five routes we built

| Route | Trigger examples | Response focus |
|---|---|---|
| `wellbore_integrity` | Casing pressure spike, annulus gas | Well control, barrier integrity |
| `process_safety` | H2S detection, overpressure, fire/gas | Evacuation, PSM compliance |
| `equipment_fault` | Motor overtemperature, pump cavitation | Maintenance dispatch, derate |
| `environmental` | Pit level high, flare ignition failure | Regulatory notification, containment |
| `pipeline_integrity` | Pressure drop, flow imbalance | Leak detection, isolation |

### Why it matters

A single generic "alarm response" prompt produces mediocre output for every alarm type. Domain-specific prompts produce expert-quality output for their specific domain. Routing gets you the latter without maintaining a separate entry point for each alarm type.

---

## Pattern 4: Orchestrator-Workers — Dynamic Well Performance Investigation

**When to use it:** When the optimal analysis depends on what the input data actually shows, and the right subtasks can't be defined in advance.

### The O&G scenario

An asset manager flags three wells as underperforming. "Why?" Each well has a different root cause. You don't know which diagnostic lens is relevant until you look at the data.

- Well C-22: Tubing pressure dropped 54% in a week, slugging at surface every 20 minutes
- Well A-17: Water cut accelerated from 22% to 67% over 12 months, choke already at 48/64"
- Well B-09: GOR rising on a new well with strong reservoir pressure, far above zone norm

A good reservoir engineer wouldn't run every possible test on every well. They'd look at the data and decide which investigations are warranted. The orchestrator-workers pattern does the same.

### How it works

**Step 1 — Orchestrator:** A senior-engineer-persona LLM reads the well data and produces a structured investigation plan:

```xml
<orchestrator_assessment>
  Tubing pressure dropped 54% concurrent with slugging reports. 
  Casing-tubing differential of 1,340 psi with no artificial lift 
  suggests liquid loading as the primary mechanism.
</orchestrator_assessment>
<investigations>
  <investigation>
    <type>liquid_loading</type>
    <hypothesis>Well loading up with produced liquids...</hypothesis>
    <worker_prompt>Analyze the pressure/rate correlation...</worker_prompt>
  </investigation>
  <investigation>
    <type>artificial_lift</type>
    <hypothesis>ESP or gas lift could recover deferred production...</hypothesis>
    <worker_prompt>Evaluate artificial lift candidates...</worker_prompt>
  </investigation>
</investigations>
```

**Step 2 — Workers:** Each investigation runs as an independent LLM call — focused, specialized, producing a CONFIRMED / PARTIALLY CONFIRMED / NOT SUPPORTED verdict with evidence and a recommended action.

**Step 3 — Synthesis:** A final LLM call combines all worker findings into a root cause assessment, recommended intervention (prioritized), and monitoring plan.

### What it produced

| Well | Orchestrator chose | Root cause identified |
|---|---|---|
| C-22 | liquid_loading, artificial_lift | Liquid loading confirmed; gas lift candidate |
| A-17 | water_source, choke_optimization | Water channeling from offset zone; choke already maxed |
| B-09 | gas_coning, decline_curve | Early gas breakthrough from cap; monitor GOR trend |

Three different investigation plans from three different data profiles. This is the key distinction from parallelization — the subtasks aren't predefined, they emerge from the data.

---

## Pattern 5: Evaluator-Optimizer — HSE Safe Work Procedure Drafting

**When to use it:** When quality can be assessed against defined criteria and iterative refinement produces meaningfully better output than a single pass.

### The O&G scenario

Before any non-routine task on a well site — hot work near H2S, confined space entry, high-pressure testing — a Safe Work Procedure must be drafted that will withstand a field HSE audit. First drafts almost always miss something: a permit reference, a specific PPE requirement, an emergency response step tailored to the location.

The evaluator-optimizer pattern automates the review-revise cycle that a senior HSE engineer would normally perform manually.

### How it works

```
Generate SWP draft
    ↓
Evaluate against HSE golden rules → score + structured gaps
    ↓
Score ≥ 80/100? → ACCEPT
Score < 80/100? → Feed gaps back to generator → Revise
    ↓
Repeat (max 4 iterations)
```

The evaluator checks each draft against 7 HSE golden rules:

1. **PERMIT** — All non-routine work requires a valid permit-to-work referenced in the procedure
2. **PPE** — PPE must be specific (H2S monitor rated >20 ppm, not "wear gas detector")
3. **LOTO** — Energy isolation must reference LOTO procedure with verification steps
4. **EMERGENCY** — Emergency response must cover the top 3 hazards for the specific task
5. **REGULATORY** — At least one specific standard must be cited (OSHA 1910.119, API RP 500)
6. **STEPWISE** — Work instructions must be sequential, numbered, with safety control at each step
7. **SIGN-OFF** — Procedure must specify who reviews and approves before work commences

The evaluator returns structured XML gaps — not vague feedback, but specific: what rule was violated, what text failed it, and exactly what must change.

### What it produced

We tested three HSE scenarios: hot work welding near H2S, confined space tank entry, and nitrogen pressure testing to 3,000 psi.

Typical first-draft score: **55–65/100**. Common gaps on the first pass: PPE described generically, no permit number format specified, emergency response not tailored to the specific hazard profile.

After 2–3 iterations: **80+/100** — the threshold for a procedure that would pass a field HSE audit.

This mirrors exactly how a senior HSE engineer reviews a junior draft: structured critique, specific redlines, iterative revision. The difference is it runs in minutes on every planned non-routine task across the portfolio.

---

## The Technical Setup

Databricks Foundation Models expose an OpenAI-compatible endpoint:

```
POST https://{host}/serving-endpoints/{model}/invocations
```

We built a `util.py` wrapper that auto-detects credentials — inside a Databricks notebook it picks up the session token via `dbutils` automatically, no manual configuration:

```python
from util import llm_call

result = llm_call(
    prompt="Analyze Well C-22 performance data...",
    system_prompt="You are a senior reservoir engineer.",
    model="databricks-claude-sonnet-4-6"
)
```

Databricks Asset Bundles handle deployment and scheduling:

```bash
databricks bundle deploy
databricks bundle run og_orchestrator_workers
```

Each pattern runs as a serverless notebook job. No cluster configuration, no node type selection — just deploy and run.

---

## What Surprised Us

Claude's petroleum engineering domain knowledge is deeper than expected. It understood GOR calculations, liquid loading diagnostics, allocation reporting constraints, PSM regulatory structure, and HSE procedure conventions without being explicitly taught. The prompts direct that existing knowledge to specific operational data — you're not teaching the model O&G from scratch, you're pointing it at the right data with the right framing.

The other surprise: the evaluator-optimizer pattern's quality improvement was consistent. The first draft always had gaps; the second draft always addressed them. The loop converged reliably rather than cycling.

---

## Where to Go From Here

These notebooks use mock data. The natural next step for each pattern:

- **Prompt Chaining** → Connect to live SCADA Delta tables in Unity Catalog
- **Parallelization** → Run nightly across all wells, write results to a monitoring dashboard
- **Routing** → Wire to a real alarm management system (OSIsoft PI, Honeywell Experion)
- **Orchestrator-Workers** → Add offset well comparison by querying a nearby-wells dataset
- **Evaluator-Optimizer** → Load your company's actual HSE golden rules as the evaluation rubric; export accepted procedures to SAP PM or IBM Maximo

---

## Code

All five notebooks and Databricks Asset Bundles configuration are open source:

**[github.com/rkkalluri-dbx/og-agentic-patterns](https://github.com/rkkalluri-dbx/og-agentic-patterns)**

Each notebook runs end-to-end on mock data. The `util.py` wrapper handles Databricks credential detection automatically.

---

*Built with Claude Sonnet 4.6 on Databricks Foundation Models*

*#AI #OilAndGas #Databricks #LLM #AgenticAI #DigitalOilfield #Claude #FoundationModels #HSE #Reservoir*
