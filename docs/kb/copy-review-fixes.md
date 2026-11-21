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
