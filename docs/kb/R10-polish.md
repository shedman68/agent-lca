# R10 – Final polish of app v2

- **Task:** R10 · **Owner:** Rashed (with Claude, cloud session) · **Date:** 21.11.2026 23:15–00:30 · **Branch:** `rashed/R10-polish` · **Status:** done, PR open
- **Rules:** no number changes; no edits in `pipeline/`, `measures/`, `factors/`, `data/`, `submission/`; Grok's theme files (`app/theme.py`, `app/static/`, `.streamlit/config.toml`, chart palette) not edited.

## Checklist
- [x] **1 Number + unit spacing.** Real space in `ui.card` and `ui.kpis`. Done when: no `\d<span` in rendered HTML (test `R10FormatTests`).
- [x] **2 Contrast.** Popover button and code chips use theme vars in both modes. Done when: popover renders card bg + ink text (checked in browser, dark and light).
- [x] **3 /about.** About is the default page (`/`), `/about` is an alias; no "Page not found". Done when: test `R10RoutingTests`.
- [x] **4 Robustness line.** Under the gauges: low, high and the paused-servers-at-idle case, from `measures/package_summary.csv` and `factors/kb/V2-idle-impact.csv` (`B_pct`). Done when: test `R10RobustnessLineTests` rebuilds the line from the files.
- [x] **5 Fewer words.** No measure ids, ticket id or file names in visible blocks (moved to details); hotspot evidence lines dropped from the cards (still in the findings details); forecast notes moved into the popover; product names removed from the Basel card. Done when: scan of visible blocks finds no ids outside sidebar/details.
- [x] **6 Own AI card.** Reads `factors/kb/V6-result.csv` TOTAL (2.45 kg mid, shown 2.4), says "counted so far".
- [x] **7 Light mode + phone.** All six pages at `?light=1` and at 390 px: no exceptions; screenshots in `screenshots/r10/after-light/` and `after-phone/`.
- [x] **8 Team cards.** Three equal name cards (Rashed – Product Lead · Vinzenz – Energy & Environment Expert · Hakim – Data Analysis Expert) and one small line "with AI agents (Claude, Grok)".
- [x] **R9 review follow-ups.** File count from `data.connect_stats()` (no typed 28); stronger photo scrim on phones; kb README status rows.

## Evidence
`python -m unittest app.test_app` → 47 tests OK · `verify_baseline.py` → MATCH · `trap_guard.py` → TRAP GUARD: PASS ·
PACKAGE: 14.5 PD (CHF 15,950) | cost -28.6 % | CO2 mid -43.0 % | low -49.6 % | high -42.2 % (unchanged).
Screenshots: `screenshots/r10/before/` (main at 28eeb57), `after/`, `after-light/`, `after-phone/`.
