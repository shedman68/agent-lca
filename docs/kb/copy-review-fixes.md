# Copy and review fixes for the pitch (Vinzenz's review + pitch script)

- **Owner:** Rashed (with Claude, cloud session) · **Date:** 21./22.11.2026 · **Branch:** `copy/review-fixes` (on top of `copy/simple-english`, which sits on `rashed/R10-polish`; #75 not merged yet) · **Status:** PR open, not merged
- **Rules:** text, layout and sorting only. No number, factor, ID, data value or calculation changed. No edits in `pipeline/`, `measures/`, `factors/`, `data/`, `submission/`, `app/theme.py`, `app/static/`, `.streamlit/`.

## Checklist
- [x] **1 "optimisation(s)"** in user-facing text (titles, labels, table column, assistant answers). IDs, files, columns unchanged. German keeps «Massnahmen».
- [x] **2 Sort toggle** on Your plan: Biggest CO2 saving (default, picked factor set) · Biggest cost saving · CO2 and cost together (scatter: x CO2, y CHF, size person-days, ID + short name; cards by combined share). Ties: other metric, then ID. Licence optimisations stay (0 kg). Logic in `app/plan_sort.py`; gauges and budget unchanged across views (test). Choice kept in `st.session_state["plan_sort"]`.
- [x] **3 Connect:** "uploads" headline, upload wording, roadmap line (API / MCP, not built yet) – from `copy/simple-english`.
- [x] **4 Where you stand:** new location note; 3.7× is `grid_DE / grid_CH` (mid) from `factors/factors.csv` (test). Details caption reworded. Energy shown as 36 MWh (35,783 kWh ÷ 1,000, computed).
- [x] **5 March line:** source found – `data/it_tickets.csv` T-1204 (also `docs/protected.csv`): release freeze and acceptance test, 1–31 March 2026. Line rewritten with date, ticket and reason.
- [x] **6 Stay on track:** new headline; assistant tables fit the bubble (desktop) and scroll inside it (phone); plain column labels (German in German mode); table text readable in both themes.
- [x] **7 Simple English** pages 0–5 (Human in the loop, prompt injection, one-time, no «franc» idioms). Vinzenz's kb documents and `submission/path_to_operation.md` shown on page 5 are not edited (their owners' files).
- [x] **8 Checks:** 55 tests OK · MATCH · TRAP GUARD: PASS · headline numbers unchanged · T-1251 refused in one click.
- [x] **9 Screenshots** (1440×900, dark): `screenshots/pitch/` connect, where-you-stand, your-plan, your-plan-map, stay-on-track (.jpg).

## Presenter mode and About (22.11.2026, after the first PR round)
- [x] **A Presenter mode.** «Story mode» runs the pitch as 21 beats (`app/story.py`). Keys: → / PageDown / Space next, ← / PageUp back; fixed Back / Next buttons and a beat counter bottom right. Each beat spotlights one block (others at 35 %), scrolls it into view and sets the state itself (sample company, Low / High / Mid, sort, the T-1251 question). CSS-only animations (rise, ticks, ring reveal, button press, type-out), off under prefers-reduced-motion. Beat and mode live in the URL (`?story=1&beat=7`), so a refresh keeps the beat. Story mode off: the app as before. Tested: 21 beats forward and back (AppTest) and with real keys in Chromium. Close beat 21 = the «Scale it to every Basel SME» card on step 4.
- [x] **B About.** Team cards with round photos from `app/static/team/<name>.jpg`; no photos are in the repo yet, so initials show. Roles: Product lead · Energy and environment expert · Data expert. Even 29 px rhythm between hook, team, why and promise.
- New computed lines for the cue cards: «Germany: 11 % of the cost, 36 % of the CO2.» (map) and «8 % of the cost · 29 % of the CO2» (hotspot 1), both from `out/` via `data.impact_by` (test).
- Screenshots (1920×1080, story mode, dark): `screenshots/story/beat-02.jpg` … `beat-19.jpg`.
