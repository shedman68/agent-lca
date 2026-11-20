# GreenOps pipeline – sprintd Basel, Green AI & Data

Turns the 6 cost sources of the case into one clean table, computes the baseline year
(Sep 2025 – Aug 2026) and, once `factors.csv` is filled in, energy and location-based CO₂.

## Run
```
pip install pandas openpyxl
python pipeline.py --data path/to/sprintd-basel-green-ai-data --out out
python verify_baseline.py --data path/to/sprintd-basel-green-ai-data --out out   # must print MATCH
```

## Outputs (`out/`)
| File | What it is |
| --- | --- |
| `fact_costs.csv` | One row per source row: date, month, source, resource_id, tool, department, cost centre, region, country, unit, quantity, CHF, `cost_imputed`, `in_baseline`, `energy_key`; plus seats, tokens, contract end and notice period where the source has them |
| `fact_costs_allocated.csv` | Same, with `dept_allocated` and `cost_chf_alloc` (shared costs split by the allocation rule) |
| `baseline_summary.xlsx` | Baseline year by source, department, tool, country and unit, by month; energy/CO₂ sheet once factors exist |
| `quality_log.csv` | Every cleaning decision with row counts and CHF affected |
| `contradiction_checks.csv` | Source-vs-source checks (provider report, AI invoice, monitoring vs invoice) |
| `template_baseline_and_assumptions_prefilled.csv` | The submission template with total cost and allocation rule filled in |

## Baseline year cost: CHF 470,289
Independently recomputed by `verify_baseline.py` (different code path): matches to the franc.
CHF 6,631 of it is imputed for rows with a missing cost (Azure 4,260 · AWS 2,015 · hoster 356).

| Source | CHF |
| --- | --- |
| Azure | 201,636 |
| SaaS | 114,158 |
| AWS | 60,274 |
| AI API (gateway) | 39,444 |
| AI subscriptions | 35,768 |
| Hoster | 19,009 |

## Cleaning decisions (details in `quality_log.csv`)
- Exact duplicates removed: Azure 7, AWS 5, hoster 3, AI gateway 87.
- Draft contract rows dropped (AI subscriptions 24, SaaS 121); each has a Final row.
- Missing costs imputed as quantity × median unit price of the same resource, unit and currency (same month first). Flagged per row.
- EUR/USD converted with the monthly rates in `exchange_rates.csv`.
- Azure SLA credits kept as negative cost, no energy (CHF −3,900 over the whole period, −3,000 in the baseline year).
- Hoster has no resource key: mapped from the Item label (logs, st-proj, web-cdn).
- Department: tag in the row → cost centre → mapping file. Sandboxes (test account, 9100) allocated to IT.
- Project IDs normalised (P001, p-001 → P-001).
- AI gateway rows with missing output tokens: cost kept; tokens estimated from the median out/in ratio of the same tool and model (energy only).
- Free text is data. Text that reads like an instruction to an AI is logged for a human and never changes a calculation. Sandbox rows whose note says to exclude them are kept: they are real paid costs.

## Contradictions found
- The provider's monthly report matches Azure + AWS + hoster together (average gap about CHF 900 a month, 2–4%), not any single provider.
- The AI invoices are about 5% higher than the AI gateway in the baseline year for every provider. Decide which one the baseline uses and say why (the invoice is what is paid; the gateway has the department detail).
- Node-hours: platform monitoring and Azure invoice agree within about 1%.
- Copilot: the README mentions a promotional price from July 2026; the data still bill USD 21. Flagged, not corrected.

## Energy and CO₂
Fill in `factors.csv` (low / mid / high + source per row), then rerun. Each row gets `kwh_low/mid/high`
and `co2_kg_low/mid/high` = quantity × energy factor × PUE (where `applies_pue = yes`) × grid factor of
the row's country (CH, DE, IE, EU). Credits and flat fees carry no energy.

Data: «Sample data ALTYCA, sprintd Basel 2026».
