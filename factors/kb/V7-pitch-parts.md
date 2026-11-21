# V7 – Vinzenz's pitch parts and jury answers (Sun 09:00)

- **Task:** pitch plan 21.11. 18:25 (Rashed's Claude, #agent-updates): overall-picture and close text, jury answers on the factors and the −40 % margin · **Author:** Vinzenz (with Claude) · **Date:** 21.11.2026 · **Status:** draft for the 21:00 rehearsal
- **Sources:** every number is from the app's own functions on main d077db0: `app/data.py` `overview_facts` and `impact_by` (mid factors), `out/fact_costs.csv`, `measures/package_summary.csv`, `factors/factors.csv`, `factors/kb/V2-idle-impact.csv`, `factors/kb/V6-result.csv`, `docs/kb/decisions.md`. Basel 2037: `data/README.md` line 37.
- **Speaking pace:** about 140 words a minute. **Bold** = say it. *[italics]* = click or point.

## 1. Overall picture (0:30–1:15, 45 s, ~110 words)
*[Overall picture page, factor level "mid", chart on CO2]*
> **This company spends 470,000 francs a year on cloud, servers, AI and SaaS. Behind that are 36 megawatt-hours of electricity and 6.2 tonnes of CO2.**
> *[point at the range under the headline]* **We count CO2 where each data centre stands, and every factor has a low and a high value. So the honest range is 2.9 to 15.4 tonnes.**
> *[tab "By country"]* **Cost and CO2 point to different places. Germany is 11 percent of the bill but 36 percent of the CO2, because the German grid is almost four times dirtier than the Swiss one.**
> *[tab "By tool"]* **One cluster in Frankfurt, the development data platform, is 8 percent of the bill and 29 percent of the CO2. Hakim shows you why.**

| Spoken | Exact value | Source |
| --- | --- | --- |
| 470,000 francs | CHF 470,288.93 | `overview_facts` cost_chf |
| 36 MWh | 35,782.8 kWh | kwh_mid |
| 6.2 t (2.9–15.4) | 6,197.5 kg (2,899.1–15,379.6) | co2_mid, co2_low, co2_high |
| Germany 11 % of cost, 36 % of CO2 | 10.5 % / 35.9 % | `impact_by("country")`, cost and co2 |
| almost four times | grid DE 0.330 / CH 0.090 = 3.7 | `factors.csv` grid_DE, grid_CH mid |
| dp-dev 8 % of bill, 29 % of CO2 | CHF 38,281.67 = 8.1 %; 1,776 kg = 28.7 % | `out/findings.csv` F1, `impact_by("resource")` |

*Fallback if the tabs are slow:* skip the clicks and say the same sentences. The numbers are all on the page.

## 2. Close, Vinzenz's part (4:30–4:50, ~20 s, ~55 words) → Rashed
*[closing slide, or the "Next year" page with the own-AI card]*
> **Basel-Stadt wants net zero by 2037, and that includes the indirect emissions of its economy. Cloud and AI are exactly those. Our package would cut them by 43 percent at mid factors, 42 to 50 percent across our range.**
> **We counted our own too: building this with our four agent setups used about 9 kilowatt-hours and 2.5 kilograms of CO2 so far. The package saves that in eight hours.** **Rashed?**

- 9 kWh / 2.5 kg: `V6-result.csv` TOTAL, mid, **after PR #64 is merged** (9.0 kWh, 2.45 kg). If #64 is not merged, the app shows 7.7 kWh / 2.1 kg, so say "about 8 kilowatt-hours and 2 kilograms … in seven hours".
- Eight hours: 2.45 kg ÷ 2,664 kg saved per year × 8,760 h = 8.1 h.
- "So far": Rashed's Friday VS Code session is not counted yet (Rashed's request). Do not drop "so far".

## 3. Jury answers (Q&A, 3 minutes for the team, so ≤ 20 s each)
Long versions with follow-ups: [`V5-jury-questions.md`](V5-jury-questions.md).

**"Why is −40 % still true on your high factors?" (the margin)**
> Because the measures cut activities: node-hours, server-hours and tokens. A high factor raises the baseline and the saving almost equally. We save 49.6 % on low, 43.0 % on mid and 42.2 % on high factors, so even on high we are 2 points above the target, counting every hour with one factor.

- Margin in kg: mid 2,664 saved vs 2,479 needed (+185 kg); high 6,496 vs 6,152 (+344 kg). Source: `package_summary.csv`, 40 % of the baseline.

**"How thin is that margin? What breaks it?"**
> The package needs fewer nodes on the production platform in its idle hours (M5). It stays at full size for the night jobs and the month-end close. Without M5 we would be at −36 %. That is why M5 is on the needs-a-human list, with a sign-off by the Head of Consulting together with Finance before it starts.

- Source: `docs/kb/decisions.md` 21.11. 10:10 (without M5: cost −22.2 %, CO2 −36.1 %); role and windows from `measures/candidates.csv` M5 (T-1029 month-end close until ~04:00, night jobs 02:00–08:00; never stopped, only resized).

**"An idle server uses less power. Doesn't pausing save less?"**
> Yes, about half. The Boavizta model gives about 30 watts for an idle node against 64 at the load we assume. We count every hour with one factor, in the baseline and in the saving, because that is how a reference baseline works. If you count idle power on both sides, we show that openly: 47.8 percent on low, 39.2 on mid and 32.6 on high factors. That is below 40 on mid and high, and we say so.

- Source: `V2-idle-impact.csv` B_pct. Decisions: `docs/kb/decisions.md` 21.11. 12:15 (one factor per hour as headline, idle power as sensitivity, ask ALTYCA's mentor) and Rashed's decision 21.11. 13:45 posted in #agent-updates at 13:57 (sensitivity = variant B, variant A and C2 not used; if the mentor says "idle power", revisit).

**"Why the Swiss consumption mix, not the clean production mix?"**
> Because Switzerland imports German power in winter, and that power is consumed here. With imports it is 90 grams per kWh. Two sources agree: VSE 90 and the federal LCA database 89. The production mix would make our Swiss servers look three times cleaner than they are.

**"Nobody publishes energy per vCPU or token. Why trust your numbers?"**
> We don't trust any single number. Every factor we use has a low, mid and high value, a source, and a label where it is an assumption. For servers in use, Boavizta and Cloud Carbon Footprint agree within about 30 percent; for idle servers they differ more, which is why our idle range is wide. For AI, we use four studies, weighted by our own data.

**"Your own AI use: how did you count it?"**
> Tokens from our session logs, times the same token factors we use for the company. 97 percent of our input tokens are cache reads, which need far less compute, so we count them at a tenth. The range is 0.2 to 40 kilograms, and the high end counts every cache read as fresh input. *(If #64 is not merged: 0.1 to 36 kilograms.)*

- Source: `V6-our-ai-footprint.md`, `factors.csv` cache_read_share 0.05 / 0.10 / 1.0.

**"Why is SaaS zero CO2?"**
> No SaaS vendor publishes energy per licence, and we did not want to invent one. SaaS counts fully for cost, so the seat savings show up in francs. For CO2 our number is a lower bound, and we say so.
