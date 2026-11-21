# G9 Mentor polish (phone)

- **Task:** G9 · **Author:** Grok (for Rashed) · **Date:** 21.11.2026 · **Status:** draft
- **Branch:** `grok/G9-mentor-polish`. Draft PR https://github.com/shedman68/agent-lca/pull/68 against `main`. Branched from #65; #65 merged while this was open, so the diff against `main` is only this work.
- **Sources:** presentation only. Figures stay in `out/` and `measures/`.

## Reused, not redone

- #65 already has the KPI tiles, percent spacing (`35.9 %`), darker ink (`#0F1512`), and the h1/h2/h3 sizes. Those stay.
- #58 builds `out/` at startup. This branch does not copy that block. A merge-tree onto #58 had no conflict markers.
- `claude/sharp-ritchie-kcwld1` (assistant refusals) is not merged and was not edited. The Ask page still uses that code as it is on #65's base.
- PR #51 is a tunnel log, not a tick-box checklist. R8 is the new list. The tunnel address is not copied.

## What is new

- `app/format_num.py`: `signed_pct` prints a reduction as `−28.4 %` and an increase as `+3.2 %`. The package caption, the CO2 popover and the idle table use it. The figure is unchanged.
- Plain words: CO2 card label is "CO2 per year", with a line that location-based means the electricity mix, not a certificate. PUE is glossed as extra electricity for cooling and the building. "Addressable" is glossed as the idle or unused part. Effort unit on the card is "person-days".
- Narrow screens (under 720px): columns stack, sidebar min-width is dropped, buttons wrap. KPI tiles can shrink to the screen width. Desktop type sizes from #65 stay.

## Checks

`python3 -m unittest app.test_app` — 33 tests OK (32 on #65, plus `FormatTests`).

Numbers were not edited. Package choice in `measures/measures.py` was not edited.
