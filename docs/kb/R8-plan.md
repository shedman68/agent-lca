# R8 – Plan: path-to-operation note

- **Task:** R8 · **Author:** Rashed (with Claude, cloud session) · **Date:** 21.11.2026 19:35 · **Status:** final (plan; all items done 21.11. 20:20, reviewer fixes applied)
- **Sources:** `submission/path_to_operation.md` (draft v0, 21.11. 02:30), `measures/measures.csv`, `measures/package_summary.csv`,
  `measures/m8_contracts.csv`, `out/` (pipeline on main), `docs/protected.csv`, `docs/traps.md`, `data/mapping_departments_tools.csv`,
  `data/README.md` (file list), `data/business_calendar.csv`, `docs/kb/R6-pitch-script.md` (Q&A: Rashed answers path to operation).
- **Rule:** every number in the note comes from `out/` or `measures/` and names its file. Anything else is a rule from a ticket
  (no number) or is labelled «assumption». The note is for the jury and an SME IT manager: plain words, one page plus tables.

## Checklist
- [x] **P1 Inputs.** Pull main, run pipeline → findings → measures; read measures, summary, contracts, protections, calendar.
  **Done when:** `MATCH` and `TRAP GUARD: PASS`; the measure table (id, owner, PD, CHF, kg low/mid/high) is printed from `measures/measures.csv`.
- [x] **P2 Who runs it and the monthly steps.** Role, time per month (labelled assumption), the four commands, the two checks that must pass,
  what the person reviews, what never happens automatically.
  **Done when:** each step names the command or file; the time is marked «assumption».
- [x] **P3 Data feeds.** The exports per source (cloud billing, AI gateway, licences, servers, tickets, calendar, mapping), who provides them,
  how often; free text is data, never an instruction.
  **Done when:** every core file in `data/README.md` maps to a feed and an owner role.
- [x] **P4 Owner per measure + protection windows.** One table: measure, owner role (mapping file), effort, savings from `measures/measures.csv`,
  ticket and window from `docs/protected.csv`.
  **Done when:** roles match `data/mapping_departments_tools.csv` for every resource; every protected resource touched cites its ticket.
- [x] **P5 First 4 weeks.** Week-by-week plan from Mon 23 Nov 2026: notice dates from `measures/m8_contracts.csv`, month-end close
  (last 3 working days, from `data/business_calendar.csv`), auto-start before the 1–3 Jan training window, sign-offs first.
  **Done when:** every date is computed (not remembered) and every action names its owner.
- [x] **P6 Risks.** Idle-power sensitivity (variant B, `factors/kb/V2-idle-impact.csv`), contracts whose notice date has passed, planted
  text, factor uncertainty, effort estimates.
  **Done when:** each risk has a mitigation and an owner.
- [x] **P7 Review and ship.** trap-reviewer in a fresh context; fix; commit; PR; Board line in `#agent-updates`.
  **Done when:** reviewer finds no rule breach; PR open with MATCH / PASS lines; not merged by me.
