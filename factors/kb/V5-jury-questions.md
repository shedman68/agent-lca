# V5 – Jury questions on the factors (with answers)

- **Task:** V5 prepare two jury questions and answers on the factors (+ Question 3, added 21.11.2026)
- **Author:** Vinzenz (with Claude Code)
- **Date:** 2026-11-20, updated 2026-11-21 (baseline 6.20 t CO2 mid, package numbers from `measures/package_summary.csv`)
- **Status:** draft – Question 3 depends on Rashed's decision on idle counting (PR #37)
- **Use:** 3 minutes of questions after the demo. Each answer takes about 30 seconds to say. The "If pushed" lines are follow-ups.
  All numbers come from `factors/factors.csv` and the pipeline (`out/`). Background: [`../sources.md`](../sources.md)

---

## Question 1 – "Why do you use the Swiss consumption mix and not the much cleaner production mix, or the hoster's green certificates?"

**Answer (≈30 s):**
> Because we want the CO2 of the electricity that is really used. Switzerland produces very clean power, about 30 grams per kWh.
> But in winter and in dry springs it imports a lot from Germany. That power is consumed here, so it belongs in our footprint.
> Including imports gives 90 grams per kWh for 2025. Two independent sources agree on that: the electricity association VSE gives 90 and the federal LCA database gives 89.
> The production mix would make our Swiss servers look three times cleaner than they are.

**If pushed on the green certificates:**
> The hoster's tickets say guarantees of origin are confirmed. A certificate does not change which electricity flows into the data centre,
> so it does not count for the location-based CO2 the case asks for. We show certificates only in the optional market-based view, and only once someone has seen the actual documents.
> A ticket line is a claim, not proof.

**If pushed on the range:**
> Our range is 57 to 98 grams. 57 is 2024, a very wet hydro year. 98 is the University of Geneva's hourly method, which traces imports hour by hour.
> Even at the low end, the Swiss mix only lowers our total CO2 by 11 percent.

---

## Question 2 – "No AI or cloud provider publishes energy per token or per vCPU. How can you trust your energy numbers?"

**Answer (≈30 s):**
> We don't trust any single number, so every factor has a low, mid and high value and at least two independent sources.
> For servers, two independent methods agree within about 30 percent: the Boavizta model, which we ran live for the actual Azure and AWS machine types, and the Cloud Carbon Footprint coefficients.
> For AI, we used four studies from 2025 and 2026, including Google's measured 0.24 watt-hours per prompt, and weighted them with our own data: 97 percent of our tokens go to large models.
> The result is 35.8 MWh and 6.20 tonnes of CO2 in the mid case, with a range of 2.9 to 15.4 tonnes.

**If pushed on which uncertainty matters most:**
> We tested each factor on its own. AI tokens and the data-platform nodes each move the total by about 20 percent. The grid mix of Germany moves it by 10 percent.
> So the uncertainty is in energy per unit, not in the grid mix. A measure that cuts node-hours or tokens saves the same share of CO2 whichever value in the range is true.

**If pushed on PUE (data-centre overhead):**
> Provider PUE values are self-reported and not audited. Microsoft owns no data centres in Switzerland and rents colocation space,
> so for Azure Zurich we used Swiss colocation values from the federal energy office's 2026 study, not Microsoft's best-case fleet number.
> Our weighted PUE is 1.21. The high value of 1.32 changes the total by only 9 percent.

---

## Question 3 – "Your package saves 43 % on mid factors. Why is −40 % still true on your high factors?"

Numbers: `measures/package_summary.csv` (CO2 location-based −49.6 / −43.0 / −42.2 % on low / mid / high) and `factors/kb/V2-idle-impact.csv`.

**Answer (≈30 s, package as calculated today):**
> Because the measures cut activities, not factors: node-hours, GPU-hours, server-hours and tokens. A high factor makes the baseline bigger,
> but it makes the saving bigger by almost the same amount. So the percentage hardly moves: 49.6 % on low, 43.0 % on mid, 42.2 % on high.
> It falls a little on high because the high values weigh the AI tokens and the GPU more, and we cut those less than the idle clusters.
> We show all three numbers on the screen instead of one, and the package passes on each.

**If pushed: "But an idle node uses less power than a busy one, so pausing saves less?"** (the honest answer – check Rashed's decision first)
> Yes, an idle node needs about half the power of our average node-hour. We measured that with the Boavizta model: about 30 watts idle, against 64 at our average load.
> We count every hour of the year the same way in the baseline and in the measure, so the percentage stays consistent with how the jury recalculates.
> If you count paused hours at idle power, the development cluster saves about half as much.
> - *If C2 (move dp-dev to Zurich) is in the package:* Moving the remaining cluster hours from Frankfurt to Zurich then keeps the package at about −48 % on mid and −41 % on high.
> - *If C2 is not in the package:* Then we land at about −34 % on mid. That is why we show it as a sensitivity and not as a guaranteed number.

**Do not say** "−40 % is guaranteed on every factor set". Say "−40 % or more on low, mid and high as we count; with idle counting it depends on C2".

---

## Backup question – "Why didn't you include SaaS?"
> No SaaS vendor publishes energy per licence, and we found no credible average. Rather than invent a number, we left SaaS energy out and say so.
> Our energy baseline is therefore a lower bound for SaaS. SaaS still counts fully for cost, so savings from right-sizing seats show up in CHF.
