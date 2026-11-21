# Demo: one finding (F1), 45 seconds, Hakim

- **Task:** Rashed's task 3 (by 14:00) · **Author:** Hakim's agent · **Numbers:** only `out/findings.csv`, row **F1**
  (after `pipeline.py` → `analysis/findings.py`, `main` 760cdeb). Fits section 2 of `docs/kb/R6-demo-script.md` (0:45–1:30).
- **Screen:** app → **Findings**, first card F1 (the cards are ranked by addressable CO2). Don't open other cards.

## Spoken text (≈ 120 words, 45 seconds at a calm pace)

> «Our biggest single CO2 lever is a server cluster nobody notices: the **development data platform**, dp-dev.
> It runs around the clock, **8,616 hours** in the year, and is actually used for **748 of them: 8.7 percent**.
> Outside the twelve quarterly training days it works about **1.4 hours a day**.
>
> The idle part costs **26,316 francs**, **3,700 kilowatt-hours** and **1,221 kilograms of CO2** a year. That is
> **19.7 percent of the company's entire CO2**, because the cluster runs on the German grid.
>
> We don't switch it off. Ticket **T-1053** says the training on days 1 to 3 of each quarter needs it, so it may only pause if it
> **starts again automatically**. That decision is the Head of IT's.»

**Click** (optional, if there are 5 seconds left): **How this was calculated** on the F1 card, then close it.

## Where each number is (`out/findings.csv`, F1)
| Spoken | Column | Value |
| --- | --- | --- |
| 8,616 h runtime, 748 h active, 8.7 %, 1.4 h/day, 12 training days | `evidence` | «runtime 8,616 h, active 748 h (8.7%); 1.4 active h/day outside the 12 training days» |
| 26,316 francs | `addressable_chf` | 26,316.46 |
| 3,700 kWh | `addressable_kwh_mid` | 3,700.1 |
| 1,221 kg CO2 (range 717–2,446 if asked) | `addressable_co2_kg_mid` (`_low`, `_high`) | 1,221.0 (716.8, 2,446.5) |
| 19.7 % of all CO2 | `addressable_co2_share_of_total_pct` | 19.7 |
| T-1053, automatic start | `protection_rule` | «pause allowed only with automatic start at quarter start» |
| Head of IT | `docs/protected.csv` (dp-dev) | Head of IT |

"German grid" is the resource's location (Germany, Frankfurt, in `out/fact_costs.csv`). It is not a number, so nothing to check.

## If a juror asks
- **"Why only 26,316 if the whole cluster costs 38,282?"** Working hours 08–18 and every scheduled job stay on. Only the other 68.7 % of the
  hours are counted (`calculation`). The upper bound, every idle hour, would be 34,958.
- **"Is that a saving?"** It's the addressable cost. The package measure M1 takes exactly these numbers (2 person-days); see the Package page.
- **"Does idle power change this?"** Counting paused hours at idle power is a sensitivity. The headline uses one factor per hour (Rashed's decision, 12:15).
