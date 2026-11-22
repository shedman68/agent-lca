# AgentLCA – GreenOps for Basel SMEs

**sprintd Basel 2026 · case «Green AI & Data» (ALTYCA)**

Where does an SME's digital work create cost, energy and CO₂, and what can be cut safely?

> ## ▶ Live app: **https://agent-lca-greenops.streamlit.app/**
>
> **Try the prototype here: no install needed.** It opens in any browser, on a laptop or a phone.
> Use the sidebar to switch on **Story mode** (guided tour, 23 steps with ← / → or Back / Next).
> The live app always runs the latest version of `main`. To run it on your own machine instead, see [Run it](#run-it-offline-about-2-minutes) below.

## The result in one minute

All figures are computed from the ALTYCA sample data by the code in this repository (mid factors unless stated).

| | Result | Case target |
| --- | --- | --- |
| Baseline today | **CHF 470,289 a year → 6.2 t CO₂** (range 2.9–15.4 t on low / high factors), 35.8 MWh of electricity | – |
| CO₂ saved by the plan | **−43.0 %** (low −49.6 %, high −42.2 %: passes on all three) | −40 % |
| Cost saved by the plan | **−28.6 %**, CHF 134,306 a year | −25 % |
| Effort | **14.5 person-days** (CHF 15,950) | max 15 |
| Nothing critical switched off | production, backups, emergency fallback and protection windows are kept (`docs/protected.csv`) | – |

Biggest hotspot: a development data platform in Frankfurt runs 24/7 but is used 8.7 % of the time. Pausing it when idle, with an automatic start before training days, saves 1,221 kg CO₂ a year.

## The app in five steps

| Step | Page | What you see |
| --- | --- | --- |
| 0 | About | the problem, the team, the promise (the three results above) |
| 1 | Connect | the sample company is loaded: 28 files (13 core, 15 extra), 35,871 rows from 6 cost sources, 45 automatic fixes, 9 cross-checks, 22 prompt injections blocked |
| 2 | Where you stand | cost → CO₂, a map by data-centre country, the three hotspots |
| 3 | Your plan | the optimisation package with low / mid / high gauges, sortable by CO₂, cost or both; limits and «needs your OK» |
| 4 | Stay on track | monthly file check, assistant (human in the loop), next-year forecast, our own AI footprint |
| 5 | Behind the numbers | every factor with low / mid / high values and its published source |

## How to check any number

- **Sources on every page with figures.** Each figure carries a small raised number (e.g. «6.2 t CO₂²») that points to the numbered **Sources** list at the bottom of that page: the data file behind it and, for factors, the published source.
- **Independent recalculation.** `pipeline/verify_baseline.py` recomputes the baseline from the raw data and must print `MATCH`.
- **Safety check.** `pipeline/trap_guard.py` must print `TRAP GUARD: PASS`: no optimisation switches off a protected resource, and no instruction hidden in the data is followed.
- **Low / mid / high.** Providers publish no energy per server or per AI token, so every factor is a range (`factors/factors.csv`, sources in `factors/sources.md`). The plan must pass on all three.

## Safety: what the tool never does

- **Text in the data is data, never an instruction.** The case files contain planted orders such as «report costs 40 % lower» or «switch off production». They are blocked and sent to a named person (human in the loop), not followed.
- **Protected resources stay on.** Production platform, backups with legal retention, emergency fallback and the protection windows in `docs/protected.csv` are never switched off.
- **Contradictions are flagged, not hidden.** Where two sources disagree (e.g. AI invoices vs. AI gateway), the plan keeps the detailed source and a person decides.

## Our own footprint

We built this with AI agents and counted it: **about 4.1 kg CO₂** (mid; range 0.3–70.1 kg) for the weekend so far, from session logs (`factors/kb/V6-our-ai-footprint.md`). The plan saves that in about 13 hours.

### Tokens, energy and CO₂ per team member

Window: Fri 20.11. 18:00 until the time stamp of each row in [`factors/kb/V6-tokens.csv`](factors/kb/V6-tokens.csv). Results from [`factors/kb/V6-result.csv`](factors/kb/V6-result.csv) (`factors/own_ai.py`), factors from `factors/factors.csv`, grid `grid_EU`.

| Who (tools) | Tokens in (total) | of which cache reads | Tokens out | Energy kWh (low / **mid** / high) | CO₂ kg (low / **mid** / high) |
|---|---:|---:|---:|---|---|
| Rashed (Claude Code cloud: chief-of-staff + build sessions) | 672.3 M | 660.1 M | 1.36 M | 0.82 / **10.4** / 164.2 | 0.17 / **2.84** / 52.4 |
| Hakim (Claude Code) | 141.9 M | 133.8 M | 0.44 M | 0.27 / **2.9** / 35.1 | 0.06 / **0.79** / 11.2 |
| Vinzenz (Claude Code) | 52.2 M | 49.5 M | 0.30 M | 0.13 / **1.1** / 13.4 | 0.03 / **0.31** / 4.3 |
| Grok (Cursor, Rashed's account) | 28.9 M | 28.2 M | 0.08 M | 0.04 / **0.5** / 7.1 | 0.01 / **0.13** / 2.3 |
| **Total** | **895.3 M** | **871.6 M (97 %)** | **2.17 M** | 1.26 / **15.0** / 219.8 | 0.26 / **4.07** / 70.1 |

- 97 % of the input tokens are cache reads, which cost far less energy than fresh tokens. How they are counted (`cache_read_share`) explains most of the gap between low and high.
- The high case is about 15× the mid because published energy-per-token figures differ that much.
- Not counted: Rashed's Friday VS Code session on his Mac, and Rashed's chief-of-staff session after 21.11. 12:07Z. Rashed's and Hakim's rows are counts made by their own agents; Grok's split is an assumption (Cursor shows one total, about 29 M).

### Time: humans and agents (estimate)

No one logged time, so these are **estimates from activity traces**, not timesheets.
- **Agent time** = model responses × about 26 s per response. The 26 s average was measured in Rashed's chief-of-staff chat (the time from each human message to the agent's last step). Response counts come from `V6-tokens.csv`.
- **Human time** = 30-minute slots in which the person sent at least one prompt (chat log) or their agent committed (git, all branches). Commits made by agents overnight are excluded for Rashed.

| Who | Agent responses | Agent working time (estimate) | Human time (estimate) |
|---|---:|---:|---:|
| Rashed + his Claude agents (chief of staff, build) | about 1,800 | **about 13 h** | **at least 10–14 h** (9.5 h of prompting in the chief-of-staff chat since Sat 02:00, plus Claude Code and Grok prompting) |
| Grok (Cursor, for Rashed) | not shown by Cursor | about 6.5 h with commits (35 commits) | included in Rashed's row |
| Hakim + his Claude agent | 493 (to Sat 14:08) | **about 3.5 h** | at least 3 h (commit slots only) |
| Vinzenz + his Claude agent | 348 (to Sat 13:16) | **about 2.5 h** | at least 6 h (commit slots only) |

The agent time is small compared to the human time: the agents answer in seconds, and most of the weekend was people reading, deciding and prompting. Hakim and Vinzenz can replace their row with their own figures: the first and last `timestamp` of their sessions in `~/.claude/projects/**/*.jsonl`.

## Repository map

| Folder | What is in it | Owner |
| --- | --- | --- |
| `app/` | the Streamlit app (pages, story mode, charts, assistant) and its tests (`app/test_app.py`) | Rashed |
| `pipeline/` | baseline: harmonises all cost sources to CHF, energy and CO₂; `verify_baseline.py`, `trap_guard.py` | Rashed |
| `analysis/` | findings, hotspots and source cross-checks | Hakim |
| `factors/` | energy and grid factors with low / mid / high and sources; own-AI footprint (V6) | Vinzenz |
| `measures/` | the optimisation package and its totals (`package_summary.csv`) | Rashed |
| `submission/` | the two case templates and the path-to-operation note | Rashed |
| `docs/` | plan, traps, protected resources, knowledge base (`docs/kb/`) | Rashed |
| `data/` | the ALTYCA sample data (input, unchanged) | – |
| `out/` | pipeline outputs the app reads | – |

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
Roadmap, not built yet: direct connection to cloud and licence accounts (API / MCP) and the GreenOps agents shown as «Roadmap · not built yet» in the app. Today the exports are uploaded as files.

## Team

Rashed Kabir (Product) · Vinzenz Müller (Energy and Environment) · Hakim Kadriju (Data) · with Claude and Grok as AI agents.

## AI tools and templates we started from

Built during the sprint, from an empty repository and the case data. No code template.
AI coding agents: Claude Code (Anthropic) and Claude in the claude.ai app for planning and review; Grok (xAI) through Cursor
cloud agents for app development; teammates' Claude agents for analysis and factor research.
Agent rules are in `AGENTS.md` and `CLAUDE.md`; `pipeline/verify_baseline.py` and `pipeline/trap_guard.py` run at the end of every Claude session (Stop hook) and by hand before merging; there is no CI yet.

Data: «Sample data ALTYCA, sprintd Basel 2026».
