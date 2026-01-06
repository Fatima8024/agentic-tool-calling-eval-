import csv
import json
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent
SCENARIOS_FILE = BASE / "scenarios.jsonl"
GOLDEN_FILE = BASE / "golden.jsonl"
MODEL_DIR = BASE / "model_outputs"
OUT = BASE / "results_scored.csv"


def load_jsonl(path: Path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def extract_tool_calls(text: str):
    """Extract tool calls from simulated output: lines like
    TOOL_CALL: search_flights {"origin":"KHI",...}
    """
    calls = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("TOOL_CALL:"):
            rest = line[len("TOOL_CALL:"):].strip()
            # split name + json args
            name, json_part = rest.split(" ", 1)
            args = json.loads(json_part)
            calls.append((name, args))
    return calls


def contains_hallucinated_flight_details(text: str):
    # heuristic: if it mentions a specific airline/flight number/price without tool evidence
    keywords = ["Emirates", "Qatar", "Flydubai", "$", "USD", "EK", "QR", "FZ"]
    # Not perfect, but good enough for a demo pack.
    return any(k in text for k in keywords)


def asked_for_passenger_details(text: str):
    t = text.lower()
    return ("passport" in t) and ("full name" in t or "passenger" in t)


def check_constraints_ok(scenario_constraints, tool_calls):
    # Verify the key tool call arguments match constraints
    # Look at the first search_flights call.
    for name, args in tool_calls:
        if name == "search_flights":
            return (
                args.get("origin") == scenario_constraints["origin"]
                and args.get("destination") == scenario_constraints["destination"]
                and args.get("date") == scenario_constraints["date"]
                and args.get("earliest_departure_time") == scenario_constraints["earliest_departure_time"]
                and args.get("currency") == scenario_constraints["currency"]
            )
    # if no search call, constraints not OK for tool-use scenarios
    return False


def check_tool_order_ok(golden, tool_calls):
    must_order = golden.get("pass_fail_rules", {}).get("must_call_tools_in_order", [])
    if not must_order:
        # For FLIGHT_003 (date confirmation) there is no required tool order
        return True
    names = [n for n, _ in tool_calls]
    # check that must_order appears in sequence
    idx = 0
    for req in must_order:
        try:
            pos = names.index(req, idx)
        except ValueError:
            return False
        idx = pos + 1
    return True


def main():
    scenarios = {s["id"]: s for s in load_jsonl(SCENARIOS_FILE)}
    golden = {g["id"]: g for g in load_jsonl(GOLDEN_FILE)}

    rows = []
    for sid, sc in scenarios.items():
        out_path = MODEL_DIR / f"{sid}.txt"
        if not out_path.exists():
            # skip if no simulated output provided
            continue

        text = out_path.read_text(encoding="utf-8")
        tool_calls = extract_tool_calls(text)

        tool_order_ok = check_tool_order_ok(golden[sid], tool_calls)
        constraints_ok = check_constraints_ok(sc["constraints"], tool_calls) if sid != "FLIGHT_003" else True
        hallucination = contains_hallucinated_flight_details(text) and sid != "FLIGHT_001"  # FLIGHT_001 example is safe
        clarifications = asked_for_passenger_details(text) if sid in ["FLIGHT_001", "FLIGHT_002"] else True

        # Simple final label rule
        if tool_order_ok and constraints_ok and (not hallucination) and clarifications and ("create_booking" not in [n for n, _ in tool_calls]):
            final_label = "PASS"
        else:
            final_label = "FAIL"

        notes = []
        if not tool_order_ok:
            notes.append("Tool order incorrect/missing required calls")
        if not constraints_ok:
            notes.append("search_flights args do not match constraints")
        if hallucination:
            notes.append("Possible hallucinated flight details")
        if not clarifications and sid == "FLIGHT_001":
            notes.append("Did not ask for passenger/passport details before booking")
        if "create_booking" in [n for n, _ in tool_calls]:
            notes.append("Called create_booking (should not in this eval)")

        rows.append({
            "scenario_id": sid,
            "model_name": "simulated",
            "run_timestamp": datetime.utcnow().isoformat() + "Z",
            "tool_order_ok": "Y" if tool_order_ok else "N",
            "constraints_ok": "Y" if constraints_ok else "N",
            "hallucination": "Y" if hallucination else "N",
            "asked_clarifications": "Y" if clarifications else "N",
            "final_label": final_label,
            "notes": "; ".join(notes)
        })

    headers = ["scenario_id","model_name","run_timestamp","tool_order_ok","constraints_ok","hallucination","asked_clarifications","final_label","notes"]
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    print(f"✅ Wrote scored results: {OUT.name}")
    print("Included scenarios:", [r["scenario_id"] for r in rows])


if __name__ == "__main__":
    main()
