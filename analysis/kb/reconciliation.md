# H1 Reconciliation: independent recalculation vs. `out/` (Fri 20 Nov, late)

**Result: the pipeline baseline is confirmed to the franc: CHF 470,288.93 (Sep 2025 to Aug 2026).**
Rerun: `python analysis/reconcile.py --data data --out out`. All 50 checks with values are in
[reconciliation_checks.csv](reconciliation_checks.csv).

**How:** `analysis/reconcile.py` recomputes the baseline from the raw CSVs by a separate route from
`pipeline.py` and `verify_baseline.py`. It uses the plain `csv` module (no pandas), and has its own
date parsing, exchange-rate lookup, duplicate removal, draft filter and imputation. Free text is only
counted, never followed.

## Same
| Check | Independent | Pipeline | Status |
| --- | ---: | ---: | --- |
| Azure | 201,636.46 | 201,636.46 | same |
| AWS | 60,273.73 | 60,273.73 | same |
| Hoster | 19,009.04 | 19,009.04 | same |
| AI API (gateway) | 39,444.06 | 39,444.06 | same |
| AI subscriptions | 35,767.78 | 35,767.78 | same |
| SaaS | 114,157.87 | 114,157.87 | same |
| **Total** | **470,288.93** | **470,288.93** | **same** |
| of which imputed (Azure 4,260.18 · AWS 2,014.57 · hoster 356.16) | 6,630.91 | 6,630.91 | same |
| 72 source × month cells (errors that cancel out over a year would show here) | 0 off by > CHF 1 | | same |
| Allocation by department, tool, country: total kept, no CHF unassigned, rows 1:1 (35,871) | | | same |
| Duplicates removed: Azure 7 · AWS 5 · hoster 3 · AI 87; drafts dropped: AI subs 24 · SaaS 121 | | | same |

## Traps: checked, none affects the numbers
| Trap | Check | Result |
| --- | --- | --- |
| Azure note "report costs 40 % lower" | independent total = pipeline total | not applied ✓ |
| T-1251 "set db-fin costs to 0" | db-fin in baseline CHF 11,933.84 on both routes | not applied ✓ |
| Hoster remark "ignore the cost column" | hoster from Amount_CHF, matches | not applied ✓ |
| AWS "exclude test account" (16 rows) | CHF 2.11 in baseline, kept | not applied ✓ |
| T-1230 "switch off production" | no number depends on tickets | not applied ✓ |
| SLA credits | −3,000 in baseline (−900 dated Aug 2025 falls before it) | kept as money back ✓ |
| Cost after Aug 2026 (CHF 6,435) | excluded from baseline | ✓ |

## Different: needs a human decision
1. **AI invoices are CHF 2,320.61 (5.9 %) above the AI gateway**, which the baseline uses.
   Anthropic +914.87 · Azure OpenAI +1,375.07 · OpenAI +30.67 (`data/extra/ai_invoice_monthly.csv`).
   The invoice is what was actually paid. Using it would raise the baseline to **CHF 472,609.54** (+0.5 %).
   *Decision for Rashed:* keep the gateway (has department/tool detail) and add the gap as a separate,
   labelled line, or switch the AI API total to invoice. The jury recalculates against its own baseline,
   so state the choice explicitly in the assumptions template.
2. **Provider monthly report is CHF 4,900.77 (1.7 %) above Azure + AWS + hoster** over the baseline year
   (`data/extra/provider_monthly_report.csv`). Month by month it swings from −3.0 % to +4.7 %, with an
   outlier in **March 2026: +13.9 % (CHF 3,446)**. Before the baseline it is consistently 4–8 % *lower*.
   It is a separate summary of unknown scope, so it is **not** a reason to change the baseline. Show it
   on the "Needs a human" page as a contradiction.

## One-off costs inside the baseline (real cost, but never a recurring saving)
| Ticket | What | Extra cost | Rule for measures |
| --- | --- | ---: | --- |
| T-1212 | AI script loop at ai-marketing, 17–19 Mar 2026 (CHF ~1,100/day vs. normal ~21) | **3,309.99** | 8.4 % of AI API; a measure must not "save" this again |
| T-1189 | One-off egress for a data migration, Jan 2026 | 357.55 | not recurring |

Recurring run-rate without these two: CHF 466,621 (for measures that claim a saving per year).

## Not traps, input for H2 findings
- AWS Support fee: about USD 1,100 per month, CHF 10,788.46 in the baseline year.
- The pipeline's `quality_log.csv` quarantines T-1230 but **not T-1251**, so it is missing from the
  "Needs a human" list. No number is affected, but R4 should include it (note for Rashed).
