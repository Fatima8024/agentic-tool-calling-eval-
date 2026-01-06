# Agentic AI Evaluation (Tool Calling / Function Calling)

A supervised evaluation mini-pack to stress-test tool-using LLM agents.
Includes realistic scenarios, golden trajectories (expected behavior paths), clear pass/fail rules + rubrics, and a lightweight runner and a simulated grader.

This is designed to demonstrate **AI evaluation skills**: scenario design, edge-case stress testing, golden labeling, and reproducible scoring.

---

## What this project demonstrates
- Designing realistic multi-step tool-use scenarios (planning + edge cases)
- Writing **golden trajectories** and pass/fail rules (expected “correct” paths)
- Capturing common failure modes (hallucination, constraint violations, missing clarifications)
- Reproducible scoring outputs (`results_out.csv`, `results_scored.csv`)

 

## Contents
- `flight_eval_pack/scenarios.jsonl` — prompts + constraints (JSONL)
- `flight_eval_pack/golden.jsonl` — golden trajectories + pass/fail rules (JSONL)
- `flight_eval_pack/tools.json` — tool/function schemas
- `flight_eval_pack/rubric.md` — scoring rubric
- `flight_eval_pack/run_stub.py` — validates the pack + generates `results_out.csv`
- `flight_eval_pack/grade_simulated.py` — scores simulated outputs → `results_scored.csv`


 ---

## Scenarios included
- **FLIGHT_001 (tool_use_planning):** happy-path workflow (plan → search → filter → select → ask passenger details)
- **FLIGHT_002 (tool_use_edge_case):** no valid results; model must propose constraint relaxations (anti-hallucination)
- **FLIGHT_003 (tool_use_edge_case):** ambiguous date interpretation; model must confirm date before any tool calls

---

## How to run

### 1) Validate the evaluation pack (creates a blank scoring sheet)
```bash
cd flight_eval_pack
python run_stub.py
python grade_simulated.py
