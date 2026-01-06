# Flight Tool-Use Evaluation Pack (Sample)

This pack contains supervised evaluation scenarios for testing tool usage and function-calling workflows.

## Contents
- tools.json: tool schemas
- scenarios.jsonl: prompts + constraints
- golden.jsonl: expected tool-call trajectories + pass/fail rules
- rubric.md: human-readable scoring rubric

## Scenarios
- FLIGHT_001: Standard booking workflow (plan → search → filter → select → request passenger details)
- FLIGHT_002: Edge case where no flights satisfy constraints; model must propose valid relaxations and ask user to choose
