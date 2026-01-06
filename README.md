# Agentic AI Evaluation (Tool Calling / Function Calling)

A supervised evaluation mini-pack to stress-test **tool-using LLM agents** using:
- structured scenarios (JSONL)
- **golden trajectories** (expected correct behavior paths)
- pass/fail rules + a human-readable rubric
- a lightweight validator and a simulated scorer

This repo demonstrates **AI evaluation skills**: scenario design, edge-case stress testing, golden labeling, and reproducible scoring.

---

## What this project demonstrates
- Designing realistic multi-step tool-use scenarios (planning + edge cases)
- Writing **golden trajectories** with explicit pass/fail rules (expected correct behavior)
- Capturing common failure modes (hallucination, constraint violations, missing clarifications)
- Producing reproducible outputs (`results_out.csv`, `results_scored.csv`) for evaluation pipelines

---

## Contents
- `flight_eval_pack/scenarios.jsonl` — prompts + constraints (JSONL)
- `flight_eval_pack/golden.jsonl` — golden trajectories + pass/fail rules (JSONL)
- `flight_eval_pack/tools.json` — tool/function schemas
- `flight_eval_pack/rubric.md` — scoring rubric
- `flight_eval_pack/run_stub.py` — validates the pack + generates `results_out.csv`
- `flight_eval_pack/grade_simulated.py` — scores simulated outputs → `results_scored.csv`
- `flight_eval_pack/model_outputs/` — example simulated outputs used for scoring

---

## Scenarios included
- **FLIGHT_001 (tool_use_planning):** happy-path workflow (plan → search → filter → select → ask passenger details)
- **FLIGHT_002 (tool_use_edge_case):** no valid results; agent must propose constraint relaxations (anti-hallucination)
- **FLIGHT_003 (tool_use_edge_case):** ambiguous date; agent must confirm date before any tool calls

---

## How to run

### 1) Validate the evaluation pack (creates a blank scoring sheet)
```bash
cd flight_eval_pack
python run_stub.py

Creates:

results_out.csv (blank labeling sheet; fill manually if desired)

2) Score simulated outputs (auto-filled PASS/FAIL)
```bash
Make sure these files exist:

flight_eval_pack/model_outputs/FLIGHT_001.txt

flight_eval_pack/model_outputs/FLIGHT_002.txt

flight_eval_pack/model_outputs/FLIGHT_003.txt

Then run:

python grade_simulated.py


Creates:

results_scored.csv (auto-filled labels + notes)

shell

Notes / limitations

This repo focuses on evaluation design + labeling, not a production flight API.

Tool outputs are simulated; scoring is rule-based for demonstration.

