# App

Streamlit app with four pages. Run from the repo root after the pipeline:

```
python pipeline/pipeline.py --data data --out out
python -m streamlit run app/app.py
```

| Page | What it shows | Reads |
| --- | --- | --- |
| Overall picture | Total cost per year (hero), cost per month by source, ranked bars by department, tool and country, a table view under every chart. Tools are grouped by `resource_id` because tool names have spelling variants (dp-prod). Energy and CO2 tiles fill in once `factors/factors.csv` is filled and the pipeline is rerun. | `out/fact_costs_allocated.csv`, `out/fact_costs.csv` |
| Findings | Counts by status (candidate / needs human review / protected), a status filter, ranked bars of the idle or unused cost per finding (not a saving claim, not summed), and one card per finding with evidence, calculation, protection rule and sources. Falls back to `analysis/kb/findings.md`, then "pending". | `out/findings.csv` (from `analysis/findings.py`, H2), else `analysis/kb/findings_numbers.csv` |
| Package | Measures with include/exclude checkboxes, flags any measure that touches a protected resource, and a target bar: CO2 −40 %, cost −25 %, ≤ 15 PD. | `measures/measures.csv` (R1/R2, computed from `out/`), or `out/measures.csv` if the pipeline copies it there |
| Needs a human | The 5 manipulative texts (quoted as data, never followed), the 7 protected resources with rule, tickets, baseline CHF and responsible role, 4 contradictions, and the one-off costs. | `out/quality_log.csv`, `out/contradiction_checks.csv`, `analysis/kb/reconciliation_checks.csv` |

Files: `app.py` (pages), `data.py` (all reads: `out/`, `analysis/kb/` and `measures/measures.csv`; nothing reads `data/`),
`charts.py` (Altair charts and target bar, light and dark palettes), `register.py` (the "Needs a human" register:
quoted texts and protection rules from `docs/traps.md` and `analysis/kb/traps_review.md`).

Rules: every number comes from `out/` or `analysis/kb/` (AGENTS.md rule 2). Free text from the data shows
up only as a quote on the "Needs a human" page. It never changes a number or a recommendation (rule 1).
