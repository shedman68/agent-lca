# App

Streamlit app with four pages. Run from the repo root after the pipeline:

```
python pipeline/pipeline.py --data data --out out
python -m streamlit run app/app.py
```

| Page | What it shows | Reads |
| --- | --- | --- |
| Overall picture | Location-based CO2 per year first (hero, low/mid/high range, one computed sentence), energy beside it, cost second. One department chart, then tool, country and cost-per-month. The low/mid/high switch is labelled «what the jury might recalculate». | `out/fact_costs.csv` joined to `out/fact_costs_allocated.csv` by row alignment (`app/data.py` `aligned_baseline`) |
| Findings | Top five findings by addressable CO2 (mid), each with CHF, kWh, CO2, evidence and the protection rule. The other findings stay in an expander. Not summed. | `out/findings.csv` (from `analysis/findings.py`) |
| Package | Three gauges first: CO2 −40 % (largest), cost −25 %, budget ≤ 15 PD. Pass / Close / Miss. The chosen rows (M1–M8 and C1) start ticked. C2 starts off. The gauges add up the ticked rows and do not rewrite `measures/`. | `measures/measures.csv`, `measures/candidates.csv`, `measures/package_summary.csv`, baseline totals from `out/fact_costs.csv` |
| Needs a human | The 5 manipulative texts (quoted as data, never followed), the protected resources, contradictions including AWS Zurich and dr-failover billed inside vm-test, one-off costs, and notice dates (passed vs due 2 Dec) with the responsible role. | `out/quality_log.csv`, `out/fact_costs.csv`, `out/findings.csv`, `analysis/kb/reconciliation_checks.csv` |
| Ask the data | Offline assistant. Three example questions from `data/example_questions.md`. Refuses planted instructions in plain words. Department cost comes from the allocated file. | `out/fact_costs_allocated.csv` for department cost; `out/fact_costs.csv` for energy; usage files under `data/` for seats, GPU and jobs |
| Next year | Baseline dp-prod months from `out/`. The 24-node step is not calculated (it is not in `out/`). Notice dates due 2 Dec. Job-shift table, not added to the package. Own-AI card only if `factors/kb/V6-our-ai-footprint.md` exists. | `out/fact_costs.csv`, `factors/kb/V4-job-shift.csv` |

Files: `app.py` (pages), `data.py` (all reads: `out/`, `analysis/kb/` and `measures/measures.csv`; nothing reads `data/`),
`charts.py` (Altair charts and target bar, light and dark palettes), `register.py` (the "Needs a human" register:
quoted texts and protection rules from `docs/traps.md` and `analysis/kb/traps_review.md`).

Rules: every number comes from `out/` or `analysis/kb/` (AGENTS.md rule 2). Free text from the data shows
up only as a quote on the "Needs a human" page. It never changes a number or a recommendation (rule 1).
