---
name: greenops-measure
description: Calculate a GreenOps saving measure or the measures package for this case (effort, CHF, kWh, CO2 per year) against the target of CO2 -40 %, cost -25 %, max 15 person-days. Use for tasks R1, R2, R4 and any question like "what does pausing X save".
---

# GreenOps measure

Run the `trap-guard` skill first.

## One measure = one row in `measures/measures.csv` (template columns)
1. **Resource and today's use** from `out/fact_costs.csv` and the usage files (data platform, server
   metrics, AI usage, seats). Quote the baseline-year cost of exactly the rows you change.
2. **Change**: what, from when, and the windows it keeps (`docs/protected.csv`).
3. **Saving per year**: cost of the rows × share removed. Use the run-rate without one-off costs
   (`docs/one_off_costs.csv`). For contracts, savings start only after the notice date (`contract_end`,
   `notice_period_days`): count only the months left in a year after notice.
4. **Energy and CO2**: same share of the rows' `kwh_*` and `co2_kg_*` (low/mid/high) once factors exist.
   Location-based uses the country of the row (CH/DE/IE/EU). Moving a load between countries changes CO2,
   not just kWh.
5. **Effort in person-days** (1 PD = CHF 1,100) with a one-line reason. Be honest; the jury checks feasibility.
6. **Risks and exceptions**: cite every ticket that applies; write «needs human decision» + responsible role
   for anything with notice periods, quality risk (smaller AI model) or an owner to confirm (zombie servers).
7. **Assumptions and sources**: the calculation in one line, files used, factor rows used.

## The package
Pick measures by CO2 saved per person-day first (CO2 is the main target), then cost. Stop when CO2 ≥ 40 %,
cost ≥ 25 % and effort ≤ 15 PD. Show low/mid/high totals. Run `trap_guard.py --measures` and keep its
PASS line. Never reach the target by touching a protected resource or counting a one-off.
