# What to upload at 15:00

Data citation for every table and screen: «Sample data ALTYCA, sprintd Basel 2026».

Upload four things. Numbers in the tables come from `out/` and from `measures/measures.csv`. The app does not need a network once the packages below are installed.

1. **The app, run offline.** Copy the repo (or at least `app/`, `out/`, `measures/`, `factors/`, `analysis/kb/`, `docs/`, `data/` and `requirements.txt`). From the repo root:

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python pipeline/pipeline.py --data data --out out
.venv/bin/python analysis/findings.py --data data --out out
.venv/bin/python measures/measures.py --out out
.venv/bin/python -m streamlit run app/app.py
```

Open the local URL Streamlit prints. The pages read `out/` and `measures/`. They do not call a model.

2. **Both tables.** `submission/template_baseline_and_assumptions.csv` and `submission/template_measures_package.csv`. Both files start with a UTF-8 BOM. Regenerate the measures table, and refill the baseline cells this script owns, with:

```
.venv/bin/python submission/build_templates.py
```

Run that after the pipeline. The measures table is M1–M8 and C1. Its market-based CO2 column stays blank. The baseline market-based company row is a bonus product of baseline kWh and `grid_market_based`, not a pipeline total. Cost has no factor range, so low, mid and high are the same total. The allocation rule is text: the value cells say `n/a (text rule)` and the rule is in the calculation. Company growth stays `n/a`; the T-1261 note is dp-prod only and is not in the baseline.

3. **`submission/path_to_operation.md`.** Still the 02:30 draft. The own-energy sentence has no team total. The Next year card shows `factors/kb/V6-our-ai-footprint.md`, which covers Vinzenz and Hakim only.

4. **This note**, so the four check lines travel with the upload.

## Check lines

```
Independent + imputed:              470,288.93
Pipeline total:                     470,288.93
MATCH
TRAP GUARD: PASS
```

`python -m unittest app.test_app`: 29 tests, OK.

Package (`measures/package_summary.csv`, and the same line from `measures/measures.py`): 14.5 PD, CHF 15,950, CHF 134,306 (−28.6 %), 12,603 kWh, CO2 mid 2,664 kg (−43.0 %), low −49.6 %, high −42.2 %.
