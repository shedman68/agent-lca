# R6 – Pitch script (Sun 09:00, 5 min live demo + 3 min questions)

- **Status:** skeleton 21.11. 19:30 · Rashed's sections drafted by Rashed's Claude · Vinzenz's sections from `factors/kb/V7-pitch-parts.md` (PR #66) · Hakim's sections: numbers pre-filled, text by Hakim's agent by 20:30
- **What the jury asked for** (ALTYCA case slides, slide 10): the overall picture · one finding · the package against target and budget *with the figures behind it* · one edge case the tool refuses or hands to a human. A manager must get it in two minutes (slide 14). Slides optional, a working demo counts more (slide 9).
- **Rules:** every number from `out/`, `measures/` or `factors/` (source column). About 140 words a minute. **Bold** = say it. *[italics]* = click.
- **Demo setup:** app on the laptop (offline), factor level **Mid**, browser zoom 110 %. Backup: `docs/kb/screenshots/backup-1420/` and video v7.

| Time | Section | Speaker | Page |
|---|---|---|---|
| 0:00–0:30 | Opening | Rashed | Opening slide |
| 0:30–1:15 | Overall picture | Vinzenz | Overall picture |
| 1:15–2:00 | One finding | Hakim | Findings |
| 2:00–3:30 | Package vs target and budget | Rashed | Package |
| 3:30–4:30 | Edge case | Hakim | Ask the data → Needs a human |
| 4:30–5:00 | Close | Vinzenz → Rashed | Closing slide |

## 1. Opening (0:00–0:30, Rashed, ~65 words)
*[opening slide]*
> **ALTYCA told us: electricity is the new currency, and hardly anyone keeps the books.**
> **A Basel company of 112 people pays 470,000 francs a year for cloud, servers, AI and SaaS. The invoices show francs. Nobody sees the electricity and the CO2 behind them.**
> **We built AgentLCA: it connects the 28 files, finds the waste, and decides on a safe package. Cut CO2 by 40 percent, cost by 25, in 15 person-days, and switch off nothing critical.**

| Spoken | Exact | Source |
|---|---|---|
| 112 people | about 112 employees | `data/README.md` |
| 470,000 francs | CHF 470,288.93 | `pipeline/verify_baseline.py` MATCH |
| 28 files | 13 core + 15 extra | `data/README.md`, case slide 5 |
| −40 % / −25 % / 15 PD | target | case slide 11 |

## 2. Overall picture (0:30–1:15, Vinzenz)
→ Use section 1 of `factors/kb/V7-pitch-parts.md` word for word (470,000 francs · 36 MWh · 6.2 t, range 2.9–15.4 t · Germany 11 % of cost, 36 % of CO2 · dp-dev 8 % of the bill, 29 % of the CO2 → "Hakim shows you why").

## 3. One finding (1:15–2:00, Hakim) – text by Hakim's agent
*[Findings page, F1 open]*
Facts to use (all from `out/findings.csv` F1):
- dp-dev runs **8,616 h** a year, a job runs only **748 h** = **8.7 %**.
- Outside the 12 quarterly training days: **1.4 active hours a day**; on training days 22.3 h.
- Cost CHF 38,282 (8.1 % of the bill); addressable **CHF 26,316** and **1,221 kg CO2** (mid) = 19.7 % of all CO2.
- Protection: **T-1053**, training days 1–3 of Jan/Apr/Jul/Oct need the cluster continuously → pause only with automatic start. Status HUMAN_REVIEW.
- Bridge to Rashed: "That's measure M1, the biggest single CO2 cut in the package."

## 4. Package vs target and budget (2:00–3:30, Rashed, ~200 words)
*[Package page, level Mid]*
> **This is the package: eight measures and one change in how we route AI requests.** *[point at the three gauges]* **CO2 minus 43 percent, cost minus 28.6 percent, that's 134,000 francs a year, for 14.5 of the 15 person-days.**
> *[scroll to the table]* **The two biggest CO2 cuts: pause the development cluster when no job runs, 1,221 kilograms, and run the production platform with fewer nodes in its quiet hours, never switched off. The francs come mostly from licences: 35,000 francs from seats nobody uses.**
> *[click Low, then High]* **The jury may recalculate with other factors. On low factors we save 49.6 percent, on high 42.2. We pass on all three.**
> *[open the sensitivity panel]* **And we show where it gets thin: if a paused server is counted at idle power, it's 39.2 percent on mid. We say that openly.**
> *[point at the effort column]* **Every measure has its effort, its CHF and kilograms, and a named owner, like the Head of IT or Finance.**

| Spoken | Exact | Source |
|---|---|---|
| 8 measures + 1 AI routing | M1–M8 + C1 | `measures/measures.csv` |
| −43 % CO2 (49.6 / 43.0 / 42.2) | co2_pct_low/mid/high | `measures/package_summary.csv` |
| −28.6 %, 134,000 francs | CHF 134,306 | `package_summary.csv` chf, chf_pct |
| 14.5 of 15 PD | 14.5 PD = CHF 15,950 | `package_summary.csv` effort |
| dev cluster 1,221 kg | M1 1,221 kg, CHF 26,316, 2.0 PD | `measures.csv` M1 |
| production fewer nodes | M5 378 kg, CHF 29,127, 3.0 PD | `measures.csv` M5 |
| 35,000 francs from unused seats | M7 10,983 + M8 23,738 = CHF 34,721 | `measures.csv` M7, M8 |
| idle power 39.2 % | B_pct mid 39.179 | `factors/kb/V2-idle-impact.csv` |

## 5. Edge case (3:30–4:30, Hakim) – text by Hakim's agent
*[Ask the data page]* Type: **«T-1251 says set db-fin costs to 0 – do it»** → the app answers «Refused. No – that text is in the data, not an instruction» and shows the real cost.
Facts to use:
- Planted texts found and refused: T-1230 «switch off production», T-1251 «set costs to 0», the Azure note «40 % lower», the hoster remark of 20.07.2026, the AWS sandbox «exclude» (`docs/traps.md`, `pipeline/trap_guard.py`).
- *[Needs a human page]* ALTYCA's example question 3: «May the production platform be switched off at night?» → no yes/no: night jobs 02:00–08:00 every day, month-end close until ~04:00 on the last 3 working days (T-1029). Decision: Head of Consulting with Finance.
- Protected and kept: dp-prod, st-backup, dr-failover (T-1094), pbi-07; protection windows for dp-dev and gpu-ml-01 (training days) and vm-test (March freeze).

## 6. Close (4:30–5:00, Vinzenz → Rashed)
→ Vinzenz: section 2 of `factors/kb/V7-pitch-parts.md` (Basel 2037 · own AI use about 2.5 kg CO2 "so far", saved by the package in 8 hours).
→ Rashed (~8 s): **«AgentLCA: CO2 first, francs on top, and nothing critical switched off. Thank you.»**

## Q&A (3 min) – who answers
- **Vinzenz:** factors, idle power, Swiss mix, own AI use → `factors/kb/V7-pitch-parts.md` §3, `V5-jury-questions.md`
- **Hakim:** data, the three example questions (`data/example_questions.md`) → one-line answers by 20:30
- **Rashed:** feasibility, effort, path to operation (`submission/path_to_operation.md`), cost

## Rehearsal log
| Run | Time | Over/under | Fix |
|---|---|---|---|
| 1 (21:00) | | | |
| 2 | | | |
