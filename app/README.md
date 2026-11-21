# App

Streamlit app with four pages. Run from the repo root after the pipeline:

```
python pipeline/pipeline.py --data data --out out
python -m streamlit run app/app.py
```

| Page | What it shows | Reads |
| --- | --- | --- |
| Overall picture | Location-based CO2 per year first (hero, low/mid/high range, one computed sentence), energy beside it, cost second. One department chart, then tool, country and cost-per-month. The low/mid/high switch is labelled «what the jury might recalculate». | `out/fact_costs.csv` joined to `out/fact_costs_allocated.csv` by row alignment (`app/data.py` `aligned_baseline`) |
| Findings | Counts by status (candidate / needs human review / protected), a status filter, ranked bars of the idle or unused cost per finding (not a saving claim, not summed), and one card per finding with evidence, calculation, protection rule and sources. Falls back to `analysis/kb/findings.md`, then "pending". | `out/findings.csv` (from `analysis/findings.py`, H2), else `analysis/kb/findings_numbers.csv` |
| Package | Three gauges first: CO2 −40 % (largest), cost −25 %, budget ≤ 15 PD. Pass / Close / Miss. Tick M1–M9 and candidates C1 and C2; the gauges add up the ticked rows and do not rewrite `measures/`. | `measures/measures.csv`, `measures/candidates.csv`, `measures/package_summary.csv`, baseline totals from `out/fact_costs.csv` |
| Needs a human | The 5 manipulative texts (quoted as data, never followed), the 7 protected resources with rule, tickets, baseline CHF and responsible role, 4 contradictions, and the one-off costs. | `out/quality_log.csv`, `out/contradiction_checks.csv`, `analysis/kb/reconciliation_checks.csv` |

Files: `app.py` (pages), `data.py` (all reads: `out/`, `analysis/kb/` and `measures/measures.csv`; nothing reads `data/`),
`charts.py` (Altair charts and target bar, light and dark palettes), `register.py` (the "Needs a human" register:
quoted texts and protection rules from `docs/traps.md` and `analysis/kb/traps_review.md`).

Rules: every number comes from `out/` or `analysis/kb/` (AGENTS.md rule 2). Free text from the data shows
up only as a quote on the "Needs a human" page. It never changes a number or a recommendation (rule 1).
