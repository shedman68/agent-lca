# GreenOps Basel – sprintd GreenTech 2026, Green AI & Data case

Where does an SME's digital work create cost, energy and CO2 – and what can be cut safely?

Start with `AGENTS.md` (rules for people and agents), then `docs/plan.md` and `docs/traps.md`.

## Run it (offline, about 2 minutes)

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python pipeline/pipeline.py --data data --out out
.venv/bin/python analysis/findings.py --data data --out out
.venv/bin/python measures/measures.py --out out
.venv/bin/python pipeline/verify_baseline.py --data data --out out    # must print MATCH
.venv/bin/python pipeline/trap_guard.py --data data --out out --measures measures/measures.csv   # must print TRAP GUARD: PASS
.venv/bin/python -m streamlit run app/app.py
```

Open the local URL Streamlit prints. The app reads `out/` and `measures/` and makes no network or model calls.
The two case templates and the path-to-operation note are in `submission/` (see `submission/README.md`).

## What is real and what is mocked

Real: every cost, energy and CO2 number is computed from the case sample data by `pipeline/`, `analysis/` and `measures/`
(baseline CHF 470,288.93, checked by an independent recalculation). Assumptions: energy and grid factors (low / mid / high, sources in `factors/`),
realisation shares and person-days per measure. Limited: the «Ask the data» assistant runs offline as a keyword router that calls the same calculations on `out/`; a Claude mode exists in the code but is off for the demo. Nothing is mocked with invented numbers.

## AI tools and templates we started from

Built during the sprint, from an empty repository and the case data. No code template.
AI coding agents: Claude Code (Anthropic) and Claude in the claude.ai app for planning and review; Grok (xAI) through Cursor
cloud agents for app development; teammates' Claude agents for analysis and factor research.
Agent rules are in `AGENTS.md` and `CLAUDE.md`; `pipeline/verify_baseline.py` and `pipeline/trap_guard.py` run at the end of every Claude session (Stop hook) and by hand before merging; there is no CI yet.

Data: «Sample data ALTYCA, sprintd Basel 2026».
