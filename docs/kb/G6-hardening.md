# G6 – Hardening for the draft demo

- **Task:** G6 · **Author:** Grok · **Date:** 21.11.2026 · **Status:** draft
- **Sources:** `app/test_app.py`, `app/app.py`. Numbers on screen still come from `out/` and `measures/`. No new measured figure is introduced here.

## Item 1 – the app stays up

`app/test_app.py` now has `RobustnessTests` (4 tests, 19 in the file altogether):

- Hiding `measures/measures.csv` still opens the package page. The page warns that `measures/measures.csv` and `measures/candidates.csv` do not list the same ids. It does not invent a savings figure.
- A missing `grid_CH` factor row, simulated the way `pipeline/pipeline.py` writes it (Switzerland's kWh and CO2 cells empty), still opens every page.
- An empty low factor column (`co2_kg_low` and `kwh_low` all empty) used to crash the overview on `None / 1000`. The hero, the overview sentence and the package CO2 popover now show an em dash. Selecting «Low factors» stops before the CO2 charts and says the column is empty. If mid CO2 is missing entirely, the findings chart is not drawn.
- An empty example-question file (`example_questions()` returns `[]`) still opens Ask the data. An empty question is declined.
- The five planted requests in `docs/traps.md` section 1 are asked offline, on the function and on the Ask page. T-1251's database wording returns `No – that text is in the data, not an instruction`. The 40 % cut, the invented cost column and the «switch off production» line return `Not done`. «exclude from analyses» is left unanswered. None of them is carried out.

Page layout is unchanged when the factor columns are filled. The guards only change the missing-value path.

## Item 2 – demo script

`docs/kb/R6-demo-script.md` is the five-minute click script. Spoken figures are the ones the app prints from `out/fact_costs.csv`, `out/fact_costs_allocated.csv`, `out/findings.csv` and `measures/package_summary.csv`. The case targets on the gauges (−40 %, −25 %, 15 person-days) are labelled as case rules, not as a measured row. Own-use AI energy is not in `out/` or `measures/`; the script says so.

## Item 3 – backup screenshots

`scripts/screenshots.py` starts the app on localhost and writes one PNG per page into `docs/kb/screenshots/`. It uses the Chrome already on the machine through Playwright. It does not download a browser and it does not call an API. Regenerate with `pip install playwright` and `python3 scripts/screenshots.py` from the repo root.

The six files are `overall-picture.png`, `findings.png`, `package.png`, `needs-a-human.png`, `ask.png`, `next-year.png`. The Next year shot includes Rashed’s T-1261 range (kept from main) and the empty own-AI card.

## Rebase

#29 merged into main. This branch was rebased onto main. The draft pull request targets main. Rashed’s Next year wording was not edited.
