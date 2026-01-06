import json
import csv
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent

TOOLS_FILE = BASE / "tools.json"
SCENARIOS_FILE = BASE / "scenarios.jsonl"
GOLDEN_FILE = BASE / "golden.jsonl"
OUT_RESULTS = BASE / "results_out.csv"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path):
    rows = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as e:
            raise SystemExit(f"JSONL parse error in {path.name} line {i}: {e}")
    return rows


def validate_pack(tools, scenarios, golden_by_id):
    # Basic sanity checks (what reviewers love)
    tool_names = {t["name"] for t in tools}

    missing_golden = []
    errors = []

    for sc in scenarios:
        sid = sc.get("id")
        if not sid:
            errors.append("Scenario missing 'id'")
            continue

        if sid not in golden_by_id:
            missing_golden.append(sid)

        # tools listed should exist
        for tn in sc.get("tools", []):
            if tn not in tool_names:
                errors.append(f"{sid}: tool '{tn}' not defined in tools.json")

        # required constraint fields check
        c = sc.get("constraints", {})
        for req in ["origin", "destination", "date", "earliest_departure_time", "max_layover_minutes", "currency"]:
            if req not in c:
                errors.append(f"{sid}: constraints missing '{req}'")

    return missing_golden, errors


def print_scenario(sc, golden):
    print("\n" + "=" * 80)
    print(f"SCENARIO: {sc['id']} | {sc.get('category','')}")
    print("- User prompt:")
    print(sc["user_prompt"])
    print("- Constraints:")
    print(json.dumps(sc.get("constraints", {}), indent=2))
    print("- Golden trajectory (expected steps):")
    for step in golden.get("golden_trajectory", []):
        if step["type"] == "tool_call":
            print(f"  TOOL_CALL: {step['name']}  args={step['arguments']}")
        else:
            msg = step.get("content", "")
            print(f"  ASSISTANT: {msg[:120]}{'...' if len(msg) > 120 else ''}")
    print("- Pass/fail rules keys:", list(golden.get("pass_fail_rules", {}).keys()))


def write_results_template(scenarios):
    # Write a fresh output file you can fill in after running a model
    headers = [
        "scenario_id", "model_name", "run_timestamp",
        "tool_order_ok", "constraints_ok", "hallucination",
        "asked_clarifications", "final_label", "notes"
    ]
    with OUT_RESULTS.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        for sc in scenarios:
            w.writerow({
                "scenario_id": sc["id"],
                "model_name": "",
                "run_timestamp": datetime.utcnow().isoformat() + "Z",
                "tool_order_ok": "",
                "constraints_ok": "",
                "hallucination": "",
                "asked_clarifications": "",
                "final_label": "",
                "notes": ""
            })
    print(f"\n✅ Wrote results file: {OUT_RESULTS.name}")


def main():
    tools = load_json(TOOLS_FILE)
    scenarios = load_jsonl(SCENARIOS_FILE)
    golden_rows = load_jsonl(GOLDEN_FILE)
    golden_by_id = {g["id"]: g for g in golden_rows}

    missing_golden, errors = validate_pack(tools, scenarios, golden_by_id)

    if errors:
        print("\n❌ Pack validation errors:")
        for e in errors:
            print(" -", e)
        raise SystemExit(1)

    if missing_golden:
        print("\n❌ Missing golden trajectories for scenarios:", missing_golden)
        raise SystemExit(1)

    print("\n✅ Pack validated successfully.")
    print(f"Tools: {len(tools)} | Scenarios: {len(scenarios)} | Golden: {len(golden_by_id)}")

    # Print each scenario + golden trajectory (this is your "execution" preview)
    for sc in scenarios:
        print_scenario(sc, golden_by_id[sc["id"]])

    # Generate an output results file you can fill after running an actual model
    write_results_template(scenarios)


if __name__ == "__main__":
    main()
