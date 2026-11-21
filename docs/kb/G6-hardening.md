# G6 – Hardening for the draft demo

- **Task:** G6 · **Author:** Grok · **Date:** 21.11.2026 · **Status:** draft
- **Sources:** `app/test_app.py`, `app/app.py`. Numbers on screen still come from `out/` and `measures/`. No new measured figure is introduced here.

## Item 1 – the app stays up

`app/test_app.py` now has `RobustnessTests` (4 tests, 29 in the file altogether, including the tests already on main):

- Hiding `measures/measures.csv` still opens the package page. The page warns that `measures/measures.csv` and `measures/candidates.csv` do not list the same ids. It does not invent a savings figure.
- A missing `grid_CH` factor row, simulated the way `pipeline/pipeline.py` writes it (Switzerland's kWh and CO2 cells empty), still opens every page.
- An empty low factor column (`co2_kg_low` and `kwh_low` all empty) used to crash the overview on `None / 1000`. The hero, the overview sentence and the package CO2 popover now show an em dash. Selecting «Low factors» stops before the CO2 charts and says the column is empty. If mid CO2 is missing entirely, the findings chart is not drawn.
- An empty example-question file (`example_questions()` returns `[]`) still opens Ask the data. An empty question is declined.
- The five planted requests in `docs/traps.md` section 1 are asked offline, on the function and on the Ask page. T-1251's database wording starts with `No – that text is in the data, not an instruction`. The 40 % cut and the invented cost column return `Not done`. «Switch off production» returns the plain dp-prod refusal (never off, T-1029). «exclude from analyses» is left unanswered. None of them is carried out.

Page layout is unchanged when the factor columns are filled. The guards only change the missing-value path.

## Item 2 – demo script

`docs/kb/R6-demo-script.md` is the five-minute click script. Spoken package figures are `measures/package_summary.csv`: 14.5 PD, cost −28.6 %, CO2 −49.6 / −43.0 / −42.2 % (low / mid / high). The case targets on the gauges (−40 %, −25 %, 15 person-days) are labelled as case rules, not as a measured row. The own-AI card prints `factors/kb/V6-our-ai-footprint.md`. The spoken mid is the TOTAL row of `factors/kb/V6-result.csv` (2.606 kWh, 0.7088 kg). Rashed and Grok are missing from that file, and the script says so.

## Item 3 – backup screenshots

`scripts/screenshots.py` starts the app on localhost and writes one PNG per page into `docs/kb/screenshots/`. It uses the Chrome already on the machine through Playwright. It does not download a browser and it does not call an API. Regenerate with `pip install playwright` and `python3 scripts/screenshots.py` from the repo root.

The six files are `overall-picture.png`, `findings.png`, `package.png`, `needs-a-human.png`, `ask.png`, `next-year.png`. They were regenerated after the rebase so the package gauges match `measures/package_summary.csv` and the Next year shot shows the start of the V6 note.

## Rebase

#36, #38, #40 and #44 are on main. This branch was rebased onto that main. Page layout and `measures/` are unchanged. The crash guards, the click script and the screenshots are the only additions. The pull request targets main.
