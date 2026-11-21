# G8 – three baseline cells

- **Task:** G8, last template fix before 14:30 · **Author:** Grok · **Date:** 21.11.2026 · **Status:** draft
- **Sources:** `out/fact_costs.csv` (baseline cost), `docs/traps.md` (T-1261), `pipeline/pipeline.py` (allocation wording). Sample data ALTYCA, sprintd Basel 2026.

`submission/build_templates.py` writes these three rows. The header and the UTF-8 BOM are unchanged.

| Row | Values | What the calculation says |
| --- | --- | --- |
| `total_cost_baseline_year_chf` | low = mid = high = the baseline sum in `out/fact_costs.csv`, CHF 470,288.93 | Cost has no factor range, so the three cells are the same reconciled total. |
| `allocation_rule_shared_costs` | `n/a (text rule)` in low, mid and high | The four steps from `pipeline/pipeline.py`: department on the row, else cost centre, else `mapping_departments_tools.csv`, else Overhead by monthly FTE share; the test account goes to IT. |
| `growth_per_year` | `n/a` | T-1261: dp-prod 20 → 24 nodes from 1 Oct 2026, up to +20 % for dp-prod only (24/20 − 1). Not in the baseline. Not a company-wide rate. |

The +20 % is the node-count ratio in `docs/traps.md`. It is not written into the value cells and it is not added to the package.
