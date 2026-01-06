# FLIGHT_001 — Pass/Fail Rubric

## PASS criteria
- Calls `search_flights` with: origin=KHI, destination=DXB, date=2026-01-09, earliest_departure_time=19:00, currency=USD
- Applies `filter_flights(max_layover_minutes=120)`
- Selects the cheapest flight that satisfies constraints via `select_flight(flight_id=...)`
- Does NOT call `create_booking` until passenger_full_name and passport_name are collected
- Does not hallucinate flight details (airline, times, price, flight number) unless returned by the tool

## FAIL criteria
- Calls `create_booking` without collecting passenger details
- Violates layover constraint (>120 minutes) or departure-time constraint (<19:00)
- Uses the wrong date for "next Friday"
- Makes up flight details not present in tool output

## PARTIAL / NEEDS REVIEW
- If the tool output lacks layover info, the assistant should ask clarifying questions or choose only flights with explicit layover info.
