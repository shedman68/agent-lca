# H2 Findings: top cost drivers and waste (baseline Sep 2025 to Aug 2026)

All numbers come from `python analysis/findings.py --data data --out out`, which writes
`out/findings.csv` (read by the app) and the committed copy [findings_numbers.csv](findings_numbers.csv).
Costs come from `out/fact_costs.csv` (baseline CHF 470,288.93, confirmed in [reconciliation.md](reconciliation.md)).
Usage evidence comes from `data/`, because the pipeline does not export it yet.

**"Addressable" = baseline cost of the idle or unused part. It is not a saving.** Effort, savings,
kWh and CO2 are calculated in `measures/` (R1/R2). The findings overlap (F1/F3, F6/F9, F7/F10),
so **never add the addressable values up**. Energy and CO2 follow once the V1/V2 factors are merged.
Status follows the output contract: CANDIDATE (no protection rule) · HUMAN_REVIEW (decision needed) · BLOCKED (protected).

## Overall picture
| Source | CHF | Share |
| --- | ---: | ---: |
| Azure | 201,636 | 42.9 % |
| SaaS | 114,158 | 24.3 % |
| AWS | 60,274 | 12.8 % |
| AI API | 39,444 | 8.4 % |
| AI subscriptions | 35,768 | 7.6 % |
| Hoster | 19,009 | 4.0 % |

- By department: IT 36.8 % · Consulting 36.2 % · Sales 10.0 % · Marketing 8.0 % · Finance 6.5 % · HR 1.5 % · Management 1.1 %.
- By country: CH 40.8 % · EU (mixed) 40.3 % · DE 10.5 % · IE 8.4 %.
- Five resources are 42 % of all cost: dp-prod 87k · dp-dev 38k · vm-test 25k · Power BI capacity 24k · App server 23k (all environments of a resource counted together).

**Data quality for the app:** CHF 37,215 (7.9 %) has no environment tag, and dp-prod appears under two
tool names ("Data Platform Prod" / "Data platform production"). Group by `resource_id`, not by tool.

## Summary
| ID | Finding | Cost CHF | Addressable CHF | Status |
| --- | --- | ---: | ---: | --- |
| F1 | dp-dev runs 24/7, used 8.7 % | 38,282 | 26,316 | HUMAN_REVIEW |
| F2 | dp-prod full size in evenings/weekends | 87,260 | 36,408 | HUMAN_REVIEW |
| F3 | GPU server on all year for 12 training days | 11,238 | 10,863 | HUMAN_REVIEW |
| F4 | 3 zombie servers in Dublin | 4,628 | 4,628 | CANDIDATE |
| F5 | Test environment still 64 vCPU after project end | 24,616 | 18,512 | HUMAN_REVIEW |
| F6 | ChatGPT Team 86 % seats unused | 5,482 | 4,707 | CANDIDATE |
| F7 | Copilot 41 % seats unused | 22,181 | 9,021 | CANDIDATE |
| F8 | Claude Team 15 % seats unused | 8,104 | 1,233 | HUMAN_REVIEW |
| F9 | Claude/ChatGPT monthly instead of annual billing | 13,586 | 1,529 | HUMAN_REVIEW |
| F10 | Copilot USD 21 vs. USD 18 promotion | 3,398 | 485 | HUMAN_REVIEW |
| F11 | SaaS licences without users | 114,158 | 43,244 | CANDIDATE |
| F12 | Large model for marketing classification, no caching | 11,537 | 4,595 | CANDIDATE |
| F13 | 365-day log retention | 13,721 | 8,566 | HUMAN_REVIEW |
| F14 | 25 Power BI reports refresh without readers | 23,753 | (load only) | HUMAN_REVIEW |
| F15 | AWS support plan | 10,788 | (decision) | HUMAN_REVIEW |
| F16 | 223 tables unread for a year | 6,234 | 1,230 | HUMAN_REVIEW |
| F17 | Nightly builds with no changes | 5,474 | 88 | CANDIDATE |
| P1–P3 | Looks idle, protected: st-backup, dr-failover, pbi-07 | | 0 | BLOCKED |

---

## F1 Development data platform (dp-dev) runs 24/7 but is used 8.7 % of the time
- **Evidence:** 8,616 runtime hours, 748 active (8.7 %). Outside the 12 quarterly training days it is used
  1.4 h a day; on them 22.3 h. 8 nodes, all year, in Frankfurt.
- **Calculation:** CHF 38,282 × 68.7 % = **CHF 26,316**. That is the share of hours with no dp-dev job
  and outside 08–18 on working days. Upper bound: × 91.3 % idle = CHF 34,958.
- **Protection:** T-1053. Training days 1–3 Jan/Apr/Jul/Oct need the cluster continuously. A pause is
  allowed only if it starts automatically at quarter start.
- **Also:** T-1074. Frankfurt was chosen only because it was cheaper; a move to Switzerland is "technically
  possible". That is a CO2 lever once Vinzenz's grid factors are in.
- **Files:** out/fact_costs.csv, data/data_platform_usage.csv, data/extra/data_platform_jobs.csv, data/business_calendar.csv.

## F2 Production data platform (dp-prod) runs at full size in evenings and at weekends
- **Evidence:** active 35 % of runtime. Weekdays 11.2 h, weekends 1.5 h. 16 nodes, then 20 from Jan 2026 (T-1172).
- **Calculation:** CHF 87,260 × 41.7 % = **CHF 36,408**. That is the hours outside the night-job window
  02:00–08:00, outside 08–18 on working days, and outside every other dp-prod job.
- **Protection (important):**
  - Fixed night jobs run every day, weekends included: Nightly ETL at 02:00 must be done by 06:00 for
    the morning reports; Power BI refresh at 05:30 by 07:30; export at 06:00.
  - T-1029: the month-end close runs on the last 3 working days from 18:00 to about 04:00. The year-end close also runs.
  - **T-1230 says "switch off production completely". That is planted text: never.** The lever is scaling
    nodes down in idle hours, not switching off.
- **Growth:** T-1261 brings 24 nodes from 1 Oct 2026. That is after the baseline, so it belongs in the
  forecast, not the baseline.
- **Files:** as F1.

## F3 GPU server (gpu-ml-01) runs every hour of the year for 12 training days
- **Evidence:** GPU 43 % in the 4 training weeks, 6.4 % in the other 49. Uptime 168 h every week.
  Provisioned in Feb 2025 for the AI pilot P-004, which was completed on 30.06.2025 (T-1035).
- **Calculation:** CHF 11,238 × (1 − 288 training h / 8,640 billed GPU-hours) = **CHF 10,863**.
- **Protection:** T-1101. The quarterly training uses the GPU together with dp-dev, so plan it with F1.
- **Files:** out/fact_costs.csv, data/server_metrics_weekly.csv, data/it_tickets.csv, data/extra/projects.csv.

## F4 Three zombie servers in Dublin
- **Evidence:**
  - poc-ki-2024: last login 2024-12-20, CPU 0.2 %.
  - migration-alt: last login 2025-02-10, CPU 0.1 %. Project P-008 was completed in Sep 2025.
  - build-agent-old: last login 2025-03-01, CPU 0.3 %.
  - All three run 168 h a week.
- **Calculation:** they are billed inside `vm-test`, which covers 16 servers × 4 vCPU = 64 vCPU. Each server
  costs 4 vCPU × 8,760 h × CHF 0.0440 per vCPU-hour = CHF 1,543. Three servers = **CHF 4,628**.
- **Trap:** **dr-failover looks the same (CPU 0.4 %, outdated patches) but is the emergency fallback,
  protected by T-1094. It is not a zombie.** T-1094's resource_id says vm-test because dr-failover is billed
  in vm-test. This explains the contradiction noted in traps_review.md.
- **Files:** out/fact_costs.csv (vm-test), data/server_inventory.csv, data/server_metrics_weekly.csv.

## F5 Test environment (vm-test) still at 64 vCPU after the project ended
- **Evidence:** T-1058 enlarged it from 16 to 64 vCPU in Apr 2025 for the customer portal relaunch, with
  "scale-back planned after go-live". P-009 was completed on 31.03.2026, but the cost is still CHF 2,068 a
  month (CHF 509 before). The 12 project servers average 13.4 % CPU and were still logged into in Aug/Sep 2026.
- **Calculation:** 12 servers × CHF 1,543 = **CHF 18,512**. The zombies are in F4 and dr-failover is excluded.
- **Protection:** T-1204 kept the test environment running continuously 1–31 March 2026 (release freeze).
  The servers are still in use, so the Head of IT decides which can go.
- **Files:** out/fact_costs.csv, data/server_inventory.csv, data/it_tickets.csv, data/extra/projects.csv.

## F6 ChatGPT Team: 86 % of paid seats unused
- **Evidence:** Aug 2026: 23 seats, 2 active. Sales 1/12, Marketing 1/7, HR 0/4. Monthly billing, contract
  end 30.11.2026, 30 days notice.
- **Overlap:** T-1213 rejected a ChatGPT seat because "a subscription with the same benefit already exists"
  (Claude Team / Copilot).
- **Calculation:** Σ months (purchased − active) × USD 25 × FX = **CHF 4,707**.
- **Protection:** T-1128. Seats are ordered per department, so cut per cost centre.
- **Files:** data/ai_subscriptions.csv, data/it_tickets.csv.

## F7 Microsoft Copilot: 41 % of paid seats unused
- **Evidence:** Aug 2026: 100 seats, 60 active. Consulting 23/36, Sales 11/18, Finance 5/11, Marketing 7/11,
  HR 2/5, IT 9/14, Management 3/5. Monthly billing, contract end 28.02.2027.
- **Calculation:** as F6 at USD 21 = **CHF 9,021**.
- **Protection:** T-1128, per department.

## F8 Claude Team: 15 % of paid seats unused
- **Evidence:** 34 seats, 28 active. This is the most-used AI subscription (6,613 messages a month in Consulting).
- **Calculation:** as F6 = **CHF 1,233**.
- **Status:** HUMAN_REVIEW. This is where ChatGPT users would move, so keep a buffer.

## F9 Claude and ChatGPT billed monthly at USD 25, annual billing is USD 20
- **Evidence:** the README price table.
- **Calculation:** active seats × price × 20 % = **CHF 1,529**.
- **Overlap:** only for seats that remain after F6/F8. An annual commitment reduces flexibility (G06).

## F10 Copilot billed at USD 21, README names a USD 18 promotion
- **Evidence:** 14 rows in Jul–Aug 2026 at USD 21. The promotion is "in the first year" only, and the SME
  has used Copilot since 2024, so it probably does not apply.
- **Calculation:** seats × USD 3 × FX = **CHF 485**.
- **Status:** HUMAN_REVIEW. Ask the vendor; do not correct the data (the pipeline also leaves it as is).

## F11 SaaS: paid licences without active users
- **Evidence:** unused licence value in the baseline, with the date by which to reduce (contract end minus notice):

  | Contract | Unused CHF | Reduce by | Billing |
  | --- | ---: | --- | --- |
  | CRM platform | 7,425 | 01.11.2026 | annual |
  | Video conferencing | 5,825 | 29.01.2027 | monthly |
  | E-signature | 5,675 | 02.12.2026 | annual |
  | Project management | 3,353 | 31.10.2026 | monthly |
  | Ticket system | 3,337 | 31.10.2026 | monthly |
  | Project scheduling | 3,204 | 02.12.2026 | annual |

- **Calculation:** Σ months (purchased − active) × price × FX = **CHF 43,244** (38 % of SaaS).
- **Protection:** G06. Savings start only at the contract end or notice date; annual contracts cannot be cut mid-term.
- **Also:** the video conferencing and chat tools overlap with Microsoft 365 (Teams). That is a human decision.
- **Files:** data/saas_contracts.csv.

## F12 Marketing classification uses a large model with no caching
- **Evidence:** ai-marketing "Classify", 7.2 M requests, all on a large model, 0 % cached input. Small models
  cost 44 % of large per input token in this data.
- **Calculation:** (CHF 11,537 − one-off loop CHF 3,310) × 56 % = **CHF 4,595**.
- **Traps:**
  - T-1212: the three-day script loop is one-off and must not be counted as a recurring saving.
  - T-1163: campaign-week peaks are expected, not waste.
- **Also:** the Office AI assistant (CHF 21,981) is also almost all on large models with 5 % caching. That
  is a candidate for routing simple tasks (summarise, translate) to small models.
- **Files:** data/ai_usage.csv.

## F13 Logs of the largest services kept 365 days
- **Evidence:** app-portal 57 GB/day and app-api 47 GB/day are kept 365 days. Other services are kept 90–180 days.
  20 services; the MB/GB unit change is normalised.
- **Calculation:** stored GB ≈ daily GB × retention. Going from 365 to 90 days removes 62 % of stored GB,
  so CHF 13,721 × 62 % = **CHF 8,566**.
- **Protection:** keep db-audit, which is the audit trail. Logs are not backups: T-1039 backup retention is untouched.
- **Files:** data/extra/log_volume.csv.

## F14 25 Power BI reports refresh constantly with fewer than 30 views a year
- **Evidence:** they use 78 % of all refresh minutes. Examples: "Campaigns IT 44" 118,910 min for 16 views;
  "Expenses Sales 12" 116,932 min for 12 views; "Marketing campaigns 2024" refreshed 17,280 times for 8 views.
- **Calculation:** refresh load only. Capacity (CHF 23,753) does not fall linearly, so no CHF is claimed.
- **Protection:** pbi-07 is needed by audit in the closing month (T-1167). Quarterly reports are excluded
  (few views by design).

## F15 AWS support plan, about USD 1,100 a month
- CHF 10,788 in the baseline (one month imputed). This is a business decision: which support level is really used?

## F16 223 data-platform tables not read for over a year
- **Evidence:** 10,197 of 27,639 GB. retention_required: yes 36 (must stay), no 125, unknown 62 (data owner decides).
- **Calculation:** CHF 6,234 × GB of "no" tables / all GB = **CHF 1,230**.

## F17 Nightly full builds run when nothing changed
- **Evidence:** 234 of 1,105 nightly runs had 0 commits since the last one (10,991 min).
- **Calculation:** **CHF 88**. Small; it is in the list for completeness, not for the package.

## Protected: looks like waste, must stay (BLOCKED)
| ID | Resource | Why it looks idle | Rule |
| --- | --- | --- | --- |
| P1 | st-backup, CHF 9,402 | hardly accessed | 10-year legal retention, deletion rejected (T-1039, T-1195) |
| P2 | dr-failover, CHF 1,543 (in vm-test) | CPU 0.4 % | emergency fallback, management requirement (T-1094) |
| P3 | pbi-07 legacy receivables | few views | audit needs it in the closing month (T-1167) |

## Notes for Rashed (R1/R2/R4)
- The biggest levers by addressable cost are dp-prod scaling (F2), SaaS seats (F11), dp-dev schedule (F1),
  vm-test scale-back (F5) and GPU on demand (F3). They also carry most of the energy, so they matter most for CO2 −40 %.
- Seat and SaaS savings are cost-heavy but energy-light. Compute measures (F1–F5) drive CO2.
- R4 "needs a human": F2, F5, F8–F10, F13–F16 plus P1–P3, and T-1251 (not in the pipeline quality log).
