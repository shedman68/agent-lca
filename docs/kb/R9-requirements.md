# R9 – App v2: ALTYCA and Basel 2037 requirements, traced to pages (must tick every row)

Source: `docs/kb/R0-case-page.md` (the case page, verbatim). Each requirement must be **visible in the main story flow**, not only in the Behind the numbers page, unless marked "Q&A".
Flow: 0 About → 1 Connect → 2 Where you stand → 3 Your plan → 4 Stay on track → 5 Behind the numbers.

## Prototype requirements (must, case page «Prototype requirements»)
| # | Requirement (their words) | Page | What must be on screen | Data in app |
|---|---|---|---|---|
| 1 | Connect: cloud, servers, AI and SaaS in one overall picture **by department and tool** | 1, 2 | Connect checklist; on 2 a compact "by department" and "by tool" view (one toggle, not two charts) | `impact_by("department"/"tool")` |
| 2 | Find: biggest drivers and waste, **backed up by the data** | 2 | 3 hotspot cards, each with a one-line evidence ("runs 8,616 h, a job runs 748 h") | `out/findings.csv` evidence column |
| 3 | Decide: measures with effort and savings in CHF and CO2 (location-based); −40 % CO2, −25 % cost, ≤ CHF 16,500 (1 PD = CHF 1,100) | 3 | gauges + "CHF 15,950 of 16,500" spelled out + per-measure PD, CHF, kg | `package_summary.csv`, `measures.csv` |
| 4 | Know the limits: **protection windows respected, contradictions flagged, hand-over to a human** | 3 | box with all three: windows kept (training days, March freeze, night jobs) · **one contradiction** (AI invoices vs AI gateway, +CHF 2,321; provider report vs invoices) · "needs your OK" with named role | `quality_log`, `contradiction_checks.csv`, needs-a-human list |
| 5 | Two tables per the templates, all factors with source, range and calculation | 5 (Q&A) | download/view both `submission/template_*.csv` + factor table low/mid/high + source | `submission/`, `factors/factors.csv` |
| 6 | Every figure is an estimate with an **open calculation** | 2, 3 | each headline number has a small "how calculated" popover | existing popovers |
| 7 | Short note on the **path to operation** | 4 or 5 | 3 steps in plain words + link to `submission/path_to_operation.md` | |

## Key presentation elements (case page «Key presentation elements»)
| Element | Page |
|---|---|
| Overall picture by department and tool | 2 |
| One finding, backed by data | 2 (dp-dev card, opens the evidence) |
| The package vs target and budget | 3 |
| One edge case: not recommended or put to a human (protection window or contradiction) | 3 ("What we did not touch") + 4 (assistant refuses T-1251) |
| **Short statement of the team's own AI energy** | **4 or end of 3: one card, "Our own AI use this weekend: ~2.5 kg CO2 so far"** (`own_ai_result()`), not hidden in page 5 |

## Stretch goals (creativity 20 %)
| Goal | Page | Status |
|---|---|---|
| Chat assistant, every answer backed by a calculation or source | 4 | show the source line under each answer |
| Forecast with ranges, with and without the package | 4 | next-year view must show both lines + range |
| Market-based view, critically next to location-based | 5 (Q&A) | **not computed** (measures market-based column is empty): show one honest line "Market-based: every Swiss kWh has a guarantee of origin; we show location-based on purpose" from V7 |
| Carbon-aware load shifting | 4 | `job_shift()` table as one "shift jobs to cleaner hours" card |
| Bonus sources from extra/ | 1 | Connect checklist mentions the extra sources used |

## Who it serves and why (case page «Who it serves», «Business value», Basel 2037)
| Point | Page |
|---|---|
| IT managers, management, finance managers of Basel SMEs | 0 ("For IT, management and finance") and 3 (owner per measure) |
| "An overall picture in minutes instead of after weeks of data work" | 1 (the Connect result line) |
| "Targeted savings without risk to operations" | 3 |
| "CO2 at the centre, francs on top" | 2 and 3: CO2 always first, CHF second |
| "An approach other SMEs can adopt" | 0 and end of 4 |
| Basel 2037: net zero 2037 + indirect emissions of the Basel economy; a tested method for advising and funding SMEs | 0 (why it matters) and end of 4 (scale: every Basel SME; partnership with ALTYCA, method for Basel 2037) |
| Scope 3, data centres in Zurich, Frankfurt, Dublin; decisions made in Basel | 2 (one line + map or country bar) |
| Swiss mix: production vs consumption incl. imports | 5 (Q&A), V7 §3 |

## Jury lens (case page «How the jury scores»)
- Design 20 %: a manager understands the picture, the package and the reasoning in **two minutes**.
- Feasibility 15 %: "realistic for an SME **without a specialist department**": the path to operation in 3 simple steps.
- Robustness 15 %: windows, contradictions, traceable figures, hand-over.
- Data 20 %: the Connect step shows time, unit, currency and names harmonised.
