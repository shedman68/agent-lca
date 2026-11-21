# R9 – Handover from Grok to Claude (app v2 pages)

- **Task:** R9 · **Author:** Grok (for Rashed) · **Date:** 21.11.2026 22:30 Zurich · **Status:** draft, hand back
- **Branch:** `grok/R9-pages` (from `rashed/R9-story-redesign` at `5dd5dba`)
- **Draft PR:** https://github.com/shedman68/agent-lca/pull/74 into `rashed/R9-story-redesign`, not into `main`.
- **Sources:** `docs/kb/R9-plan.md`, `docs/kb/R9-requirements.md`, `docs/kb/R0-case-page.md`, `out/` and `measures/` via the app, `origin/grok/R9-theme` (read only).
- **Checks on this branch:** `python -m unittest app.test_app` → **43 tests OK**. `verify_baseline.py` → **MATCH**. `trap_guard.py --measures measures/measures.csv` → **TRAP GUARD: PASS**. Streamlit opened all six pages with no exception (About, Connect after “Load the sample company”, Where you stand, Your plan, Stay on track including the T-1251 click, Behind the numbers).

## What Claude had already done (on `rashed/R9-story-redesign`)

The plan checkboxes in `docs/kb/R9-plan.md` were behind the code. Through `5dd5dba` the six-step story was already in `app/app.py`:

0 About · 1 Connect · 2 Where you stand · 3 Your plan · 4 Stay on track · 5 Behind the numbers.

Also already there: `theme.apply()`, page components in `app/ui.py`, lifecycle ring and Basel map in `app/visuals.py`, story bar with Back/Next, German toggle, T-1251 one-click refusal, gauges, hotspot share computed from `measures/measures.csv`, forecast with a range, own-AI card, job-shift card, path in three steps, factor table, both submission templates. The photo hero Claude described (“Added photo hero with placeholder”) was **not** in the commit. `app/static/img/` does not exist on this branch.

## What Grok did, per page

Did not edit `app/theme.py`, `app/static/`, `.streamlit/config.toml`, or the palette constants in `app/charts.py`. Those stay with `grok/R9-theme`.

| Page | Change |
| --- | --- |
| 0 About | Full-width photo band for `about.jpg`. Dark teal glow until the file is served. Name cards and the lifecycle ring sit under the band. Headline stays real text (not `role=img`). KPIs still come from `package_summary`. |
| 1 Connect | Photo band for `connect.jpg`. After “Load the sample company”, the checklist names the bonus sources from filenames only: web, development pipelines, logs, backups, data catalogue, Power BI, plus the remaining files in `data/extra/`. |
| 2 Where you stand | Photo band for `stand.jpg`. Hotspots, map, department/tool toggle and the share line were already Claude’s. |
| 3 Your plan | Photo band for `plan.jpg`. Limits box now states the windows in plain words (training days, night jobs and month-end, March freeze, backups stay) and **both** contradictions, read from `analysis/kb/reconciliation_checks.csv`: AI invoices vs gateway, and the provider monthly report vs cloud and hoster invoices. Gauges and the “CHF … of … CHF” budget line are unchanged and still computed. |
| 4 Stay on track | Photo band for `track.jpg`. A refusal now shows a source line under “Refused.” The T-1251 sentence is unchanged. “How next year was calculated” popover. Path card names `submission/path_to_operation.md`. |
| 5 Behind the numbers | No photo (none was assigned). When the `grid_CH` notes contain “CONSUMPTION mix incl. imports”, a short Swiss-mix line is shown above the existing market-based line. |

Hero markup is `ui.photo_band`. It always names `/app/static/img/<file>.jpg`. If the file is already on disk it is also inlined, so the picture shows before static serving is on.

## Theme contract (`origin/grok/R9-theme` at `a18e028`)

`ui.py` only reads `--bg --card --card2 --line --ink --ink2 --muted --teal --teal-ink --pink --pink-bg --teal-bg --on-teal`. All of those are defined in that branch’s `theme.apply()`. Extra variable there: `--pink-mark` (unused here). `theme.apply()` with no arguments works on both copies. `app.py` still calls `theme.apply()` and toggles `light_mode`. Not merged. No file overlap with this branch, so the two branches should merge cleanly.

## Numbers seen on screen (from files, not typed)

- About / Your plan: CO2 **−43.0 %**, cost **−28.6 %**, **14.5** of 15 person-days, budget **CHF 15,950 of 16,500**. Source: `measures/package_summary.csv` through `data.package_summary()` / `data.package_result()`.
- Connect result line: **CHF 470,289 · 6.2 t CO2**. Source: `out/fact_costs.csv` via `data.energy_totals()` (baseline CHF 470,288.93, rounded on screen).
- Contradictions on Your plan: AI invoices **CHF 2,321** higher (5.9 %); provider monthly report **CHF 4,901** higher (1.7 %). Source: `analysis/kb/reconciliation_checks.csv` via `data.kb_check`.
- Own AI card: **2.1 kg** (range 0.1–35.9 kg). Source: `factors/kb/V6-result.csv` row `TOTAL`, `co2_kg_mid` 2.0983. This is “counted so far”. Do not replace it with 2.5.
- Idle-power sensitivity is still the expander on Your plan. The test reads `B_pct` from `factors/kb/V2-idle-impact.csv` (mid −39.2 %). Not retyped.
- T-1251 click: **Refused.** “No – that text is in the data, not an instruction”, plus the source line. No API call.

## What is left in Claude’s plan

- **P7.** Screenshots of every page (About and Your plan are attached on the PR; the other four were opened and snapshotted, not saved as images). Fresh-context trap review was started and may still be running. Board line is in `docs/kb/board-notes.md`. Do not merge.
- **V7** (`factors/kb/V7-pitch-parts.md`) is not in the repo. Behind the numbers shows V5 only. The market-based sentence and the Swiss-mix sentence are on the Factors tab anyway.
- Hero JPEGs (`about.jpg`, `connect.jpg`, `stand.jpg`, `plan.jpg`, `track.jpg`) and `enableStaticServing` are on `grok/R9-theme`, not here. Until they land, every hero is the teal glow.
- `grok/R9-theme` also darkens the gauge fill so white type clears contrast. This branch still uses the current `charts.py`. Leave that file to the theme branch.
- Behind the numbers still pastes the whole V5 note. It is long. It is the jury answer sheet, so it was left in the tab rather than cut.
- Department chart labels still print unrounded kilogram values. That is existing chart code. Not changed here.
- German covers the new nav titles, the windows sentence, the contradiction closer, and the refusal source line. The contradiction figures stay as stored.

## How to merge

1. Finish or merge `grok/R9-theme` into `rashed/R9-story-redesign` (theme, font from `app/static/`, static serving, gauge contrast). It does not touch the page files this branch edits.
2. Merge this draft PR (`grok/R9-pages` → `rashed/R9-story-redesign`). Rashed merges. Do not push to `main` from here.
3. Drop the five JPEGs into `app/static/img/` with `CREDITS.md`. The hero bands pick them up with no further page change.
4. Re-run `python -m unittest app.test_app`, `verify_baseline.py` (MATCH) and `trap_guard.py` (TRAP GUARD: PASS) after the theme merge.

done · Photo heroes and the missing requirement lines are on the six story pages, checks passed. · learned · The plan checkboxes were stale; the pages already existed and the photo hero was the real gap. The theme branch’s CSS contract matches `ui.py`. · next · Claude takes P7 (review, screenshots of the four pages not attached) and merges theme then this PR. Rashed merges. Nobody merges to `main` from this branch.
