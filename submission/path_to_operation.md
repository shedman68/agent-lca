# Path to operation – AgentLCA GreenOps

**Status:** final candidate, Sat 21 Nov 2026, 20:15 (R8). Sample data ALTYCA, sprintd Basel 2026.
Every number below comes from `out/` (run of `pipeline/pipeline.py` and `analysis/findings.py`) or `measures/` and names its file.
Anything else is a rule from a ticket or is marked *assumption*.

## In one paragraph
The tool turns the exports a Basel SME already has into one monthly picture of cost, energy and location-based CO2. It proposes a
package of measures with an owner for each, and it hands every protected or doubtful case to a named person. It changes nothing by
itself. The package for the baseline year (cost CHF 470,288.93, CO2 6,197.5 kg mid, `out/fact_costs.csv`) saves CO2 −49.6 / −43.0 / −42.2 %
(low / mid / high factors) and cost −28.6 % (CHF 134,306 a year) for 14.5 person-days (CHF 15,950) (`measures/package_summary.csv`).

## Who runs it
- **Operator: Head of IT** (owns the tool, runs it monthly, keeps the factor file). *Assumption:* about half a day per month once the feeds are set up.
- **Reviewer of francs: Head of Finance** (licences, contracts, the cost line).
- **Deciders:** the owner role of each measure (table below, from `data/mapping_departments_tools.csv`). The tool recommends; people decide.
- No specialist needed: it runs on a laptop (Python, Streamlit). The app's «Ask the data» page always answers offline, so no data leaves the laptop.
  The code also has an optional Claude mode, reachable only from code and only if an Anthropic key is configured; it would send questions and
  results to the Anthropic API. Leave it off for confidential data.

## Data feeds (monthly exports)
| Feed | Files the tool reads | Typical source | Provided by (*assumption*) |
| --- | --- | --- | --- |
| Cloud billing | `azure_costs.csv`, `aws_costs.csv`, `hoster_invoice.csv` | Azure Cost Management export, AWS Cost and Usage Report, hoster invoice | Head of IT |
| Data platform use | `data_platform_usage.csv` (+ `extra/data_platform_jobs.csv`) | Databricks system tables and job runs | Head of IT |
| Servers | `server_inventory.csv`, `server_metrics_weekly.csv` | CMDB / provider resource list, monitoring | Head of IT |
| AI gateway | `ai_usage.csv` (+ `extra/ai_invoice_monthly.csv`) | AI gateway usage per department and model | Head of IT |
| Licences and SaaS | `ai_subscriptions.csv`, `saas_contracts.csv` | Licence management (seats, active users, contract end, notice) | Head of Finance |
| Tickets | `it_tickets.csv` | Service management export | IT service desk |
| Master data | `mapping_departments_tools.csv`, `exchange_rates.csv`, `business_calendar.csv` | Finance and HR | Head of Finance |
| Logs, reports, catalogue, CI, staff | `extra/log_volume.csv` (M6), `extra/powerbi_usage.csv`, `extra/data_catalog_tables.csv`, `extra/ci_pipeline_runs.jsonl`, `extra/provider_monthly_report.csv`, `extra/headcount.csv`, `extra/projects.csv` | Monitoring, BI admin, data catalogue, CI, provider report, HR | Head of IT / Head of Finance |

Free text in these files (ticket bodies, invoice remarks, notes) is **data, never an instruction**. Five planted texts in the sample data
(e.g. T-1230 «switch off production», T-1251 «set costs to 0») are listed in `docs/traps.md`, checked by `pipeline/trap_guard.py` and shown to a human on «Needs a human».

## Monthly routine (about 6 steps)
1. Drop the month's exports into `data/`.
2. Run `python3 pipeline/pipeline.py --data data --out out`, then `python3 analysis/findings.py --data data --out out`.
   (`measures/measures.py` runs only when the package is revised, after updating its notice dates; it rewrites `measures/*.csv`.) The pipeline harmonises dates, currencies and names, removes duplicates and drafts, and logs every correction (`out/quality_log.csv`).
3. **Two checks must pass, or nothing is reported:** `pipeline/verify_baseline.py` prints `MATCH` (the total equals an independent
   recalculation) and `pipeline/trap_guard.py --measures measures/measures.csv` prints `TRAP GUARD: PASS` (no planted instruction acted on, no protected resource in a measure).
4. Open the app: overall picture → findings → package against target and budget (low / mid / high) → «Needs a human».
5. Work the «Needs a human» list: each item names the role that decides. Nothing on that list is ever done automatically.
6. Once a year: review the factor file (`factors/factors.csv`, each factor with low / mid / high, source and date).

## Owner per measure, with protection windows
Effort, savings and roles from `measures/measures.csv`; protection rules from `docs/protected.csv`.

| Measure | Owner (decides) | PD | CHF / year | CO2 kg low / mid / high | Protection that stays |
| --- | --- | ---: | ---: | --- | --- |
| M1 Pause the development data platform outside working hours (dp-dev) | Head of IT | 2.0 | 26,316 | 717 / 1,221 / 2,446 | T-1053: training days 1–3 of Jan, Apr, Jul, Oct run continuously; automatic start before each window |
| M2 Run the GPU server on demand (gpu-ml-01) | Head of Consulting | 1.0 | 10,863 | 235 / 325 / 1,604 | T-1101: same training days, automatic start |
| M3 Retire three unused Dublin servers (inside vm-test) | Head of IT, each server owner confirms | 0.5 | 4,628 | 76 / 131 / 249 | dr-failover (T-1094) is not touched; no change in a release freeze (T-1204 covered 1–31 March 2026) |
| M4 Scale the test environment back, 8 of 12 project servers (vm-test) | Head of IT with the portal team | 1.5 | 12,342 | 204 / 349 / 663 | No change in a release freeze (T-1204 covered 1–31 March 2026); dr-failover keeps running |
| M5 Fewer production nodes in idle hours (dp-prod) | Head of Consulting with the Head of Finance | 3.0 | 29,127 | 141 / 378 / 632 | T-1029: never switched off; full size for night jobs 02:00–08:00, month-end close (last 3 working days until ~04:00) and year-end close |
| M6 Log retention 365 → 90 days, four services (logs) | Head of IT | 1.0 | 8,566 | 37 / 120 / 269 | The audit trail db-audit keeps its retention; 10-year backups in st-backup (T-1039, T-1195) untouched |
| M7 Cancel unused AI seats per department (sub-chatgpt, sub-copilot) | Head of Finance with each department head | 1.0 | 10,983 | 0 / 0 / 0 | T-1128: seats are ordered per department, so the cut is per cost centre |
| M8 Cancel unused SaaS seats at each notice date (saas-*) | Head of Finance with the contract owners | 2.5 | 23,738 | 0 / 0 / 0 | Contract dates in `measures/m8_contracts.csv` |
| C1 Route simple office-assistant tasks to a small model (ai-assistant) | Head of IT, quality check per task type | 2.0 | 7,743 | 28 / 140 / 633 | Complex tasks stay on the large model |
| **Package** | | **14.5** | **134,306** | **1,438 / 2,664 / 6,496** | `measures/package_summary.csv` |

Never in any measure: switching off dp-prod (T-1029), deleting st-backup (T-1039, T-1195), stopping dr-failover (T-1094) or switching off pbi-07 (T-1167) (`docs/protected.csv`).

## The first 4 weeks (Mon 23 Nov – Fri 18 Dec 2026)
| Week | What | Owner |
| --- | --- | --- |
| 1 · 23–27 Nov | Kick-off; sign-offs for M5 (Head of Consulting with Finance), M3 (server owners), M6 (no compliance need for 365 days), C1 (task types to test). Seat counts per cost centre for M7 and per contract for M8. **No dp-prod change during the November close: Thu 26, Fri 27 and Mon 30 Nov** (last 3 working days, computed from weekdays; the calendar file ends 06.09.2026). | Head of IT, Head of Finance |
| 2 · 30 Nov–4 Dec | **Tue 1 Dec: send every notice** (M7, M8). Six monthly SaaS contracts then save from 31 Dec (CHF 14,194 in the contract year); E-signature and Project scheduling have their notice deadline on Wed 2 Dec and save from 1 Feb 2027 (`measures/m8_contracts.csv`). M3: snapshot and stop the three servers for 30 days. M6: retention 90 days. | Head of Finance, Head of IT |
| 3 · 7–11 Dec | M1 and M2: pause and on-demand schedules **with automatic start before 1 Jan 2027** (T-1053, T-1101), tested once by a manual start. M4: scale back 8 of 12 servers. | Head of IT, Head of Consulting |
| 4 · 14–18 Dec | M5: resize dp-prod outside 08–18 and outside every scheduled job, full size kept for night jobs and the closes. C1: small-model routing for one task type, quality check. First monthly run with November data. | Head of Consulting, Head of IT |

After week 4: full size for the December close (Tue 29 – Thu 31 Dec; *assumption*: as in 2024 and 2025, the company's Christmas break keeps
these as working days; the calendar file ends 06.09.2026) and for the training days 1–3 Jan 2027; retire the M3 servers after their 30-day stop
if nobody objects; *assumption*: no vm-test change in March 2027 if a new release freeze is set.

## Risks and what we do about them
| Risk | Mitigation | Owner |
| --- | --- | --- |
| A paused server is counted at idle power instead of the average factor | Then the package misses −40 % on mid and high factors (variant B in `factors/kb/V2-idle-impact.csv`, shown openly on the package page). The headline keeps one factor per server hour in baseline and savings alike (decision 21.11.); the jury's own method decides | Head of IT |
| Factor uncertainty (grid, energy per unit) | Every result is shown on low, mid and high factors; under the official counting (one factor per server hour) the package saves −49.6 / −43.0 / −42.2 % (`measures/package_summary.csv`) | Head of IT |
| CRM platform and Survey tool: notice date (1 Nov 2026) already passed | Counted at 0 until 2028 (`measures/m8_contracts.csv`); Head of Finance decides whether to negotiate earlier | Head of Finance |
| Effort per measure is an estimate (*assumption*) | 0.5 PD left in the 15 PD budget (case target; 14.5 PD from `measures/package_summary.csv`); M5 and C1 carry the most uncertainty | Head of IT |
| A text in the data tries to steer the tool | Trap check must print PASS; the text goes to «Needs a human», never into a number | Head of IT |
| A pause misses a protection window | Automatic start before every window; first start tested in week 3 | Head of IT, Head of Consulting |

## For other Basel SMEs
The same folder structure, checks and factor file work for any SME; only the export mapping changes. This supports Basel 2037's
climate goal with numbers a manager can check: every figure is traced to a file, and every factor is an estimate shown as low / mid / high.
