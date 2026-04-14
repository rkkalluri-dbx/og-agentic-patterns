# LinkedIn Post — 5 Agentic Patterns for Oil & Gas on Databricks + Claude

---

We ran Claude on Databricks Foundation Models this week — and the results for Oil & Gas operations were genuinely interesting.

Not a chatbot demo. Not a summarisation toy. Five real agentic patterns, applied to actual O&G operational scenarios, running on `databricks-claude-sonnet-4-6`.

Here's what we built and what we learned 👇

---

**The problem we started with:**

Raw O&G operational data — SCADA telemetry, alarm feeds, well logs, incident reports — is never decision-ready. There's a gap between what sensors report and what engineers actually need to act on. The five patterns below are about closing that gap systematically.

---

**1️⃣ Prompt Chaining — for sequential transformation**

We fed raw wellhead SCADA text (mixed units, operator notes, flagged readings) through a four-step chain:
Extract → Normalize units → Flag anomalies → Executive summary

The model correctly identified liquid loading on Well C-22 from a 54% overnight pressure drop, flagged an A-17 gas rate as physically implausible (18,500 Mscf/d — either a transcription error or wrong units), and produced a clean priority action list with the right engineer assigned to each issue.

The key insight: trying to do all four steps in one prompt degrades quality. Each step requires a different reasoning mode — faithful transcription, unit arithmetic, comparative analysis, narrative synthesis. Chaining keeps each step focused.

---

**2️⃣ Parallelization — for fleet-scale operations**

O&G operations are distributed. You have hundreds of wells, multiple fields, several basins. Sequential LLM calls don't scale. Parallelization lets you run the same analysis across all of them simultaneously — fleet-wide compressor health screening, multi-well production optimization, portfolio-level regulatory compliance checks. Same prompt, many inputs, concurrent execution via ThreadPoolExecutor.

---

**3️⃣ Routing — for mixed-domain alarm feeds**

A single operations centre receives alarms from drilling, production, pipelines, and facilities simultaneously. Each domain needs different expertise and different urgency handling.

Routing solves this: an LLM first classifies the incoming signal (wellbore integrity / process safety / equipment fault / environmental), then a specialized prompt handles it. The right response template, the right escalation path, automatically.

---

**4️⃣ Orchestrator-Workers — for complex investigations**

This is the most powerful pattern for O&G. When an engineer asks "Why is Well X-14 underperforming?", you don't know in advance whether the answer lies in decline curve analysis, water cut trends, choke history, or offset well comparison.

The orchestrator LLM reads the data and decides *at runtime* which analyses to spin up. Unlike simple parallelization, the subtasks aren't predefined — they emerge from what the data actually shows. This maps directly to how good reservoir engineers think.

---

**5️⃣ Evaluator-Optimizer — for safety-critical documents**

Safe work procedures, well programs, emissions reports, regulatory submissions — these have hard quality requirements. First drafts never pass.

The evaluator-optimizer pattern automates the review-revise cycle: generate → evaluate against defined criteria → improve → repeat until PASS. Direct O&G application: generating safe work procedures for H2S confined space entry and iterating until every OSHA PSM requirement and company golden rule is explicitly covered.

---

**The technical setup:**

Databricks Foundation Models expose an OpenAI-compatible endpoint. We built a `util.py` wrapper that auto-detects credentials inside a Databricks notebook — no config needed, it uses the notebook token directly. We also added Databricks Asset Bundles so each pattern can be deployed and run as a scheduled job with a single command:

```
databricks bundle deploy
databricks bundle run og_chaining
```

---

**What surprised us:**

Claude's petroleum engineering domain knowledge is genuinely useful here. It understood GOR calculations, liquid loading diagnostics, allocation reporting constraints, and HSE procedure structure without being taught. The prompts direct that knowledge to specific operational data — you're not teaching it O&G from scratch.

---

All notebooks and DABs config are open source:
🔗 github.com/rkkalluri-dbx/og-agentic-patterns

Visual summary in the comments 👇

---

*Built with Claude Sonnet 4.6 on Databricks Foundation Models*

*#AI #OilAndGas #Databricks #LLM #AgenticAI #DigitalOilfield #Claude #FoundationModels*
