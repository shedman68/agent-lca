# V5 – Jury questions on the factors (with answers)

- **Task:** V5 prepare two jury questions and answers on the factors
- **Author:** Vinzenz (with Claude Code)
- **Date:** 2026-11-20
- **Status:** final for review
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
> The result is 36 MWh and 6.2 tonnes of CO2 in the mid case, with a range of 2.9 to 15 tonnes.

**If pushed on which uncertainty matters most:**
> We tested each factor on its own. AI tokens and the data-platform nodes each move the total by about 20 percent. The grid mix of Germany moves it by 10 percent.
> So the uncertainty is in energy per unit, not in the grid mix. A measure that cuts node-hours or tokens saves the same share of CO2 whichever value in the range is true.

**If pushed on PUE (data-centre overhead):**
> Provider PUE values are self-reported and not audited. Microsoft owns no data centres in Switzerland and rents colocation space,
> so for Azure Zurich we used Swiss colocation values from the federal energy office's 2026 study, not Microsoft's best-case fleet number.
> Our weighted PUE is 1.21. The high value of 1.32 changes the total by only 9 percent.

---

## Backup question – "Why didn't you include SaaS?"
> No SaaS vendor publishes energy per licence, and we found no credible average. Rather than invent a number, we left SaaS energy out and say so.
> Our energy baseline is therefore a lower bound for SaaS. SaaS still counts fully for cost, so savings from right-sizing seats show up in CHF.
