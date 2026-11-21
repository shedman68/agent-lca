# Questions for Andy (energy / LCA expert) – ready to send

- **Task:** R4 / R9 · **Author:** Rashed (with Claude) · **Date:** 21.11.2026 02:45 · **Status:** ready to send – add Andy's answers below with date
- Andy has no context on the case, so the message starts with a short brief, then our current recommendation for him to confirm or correct.

## Message to send
Hi Andy, quick expert check for a hackathon this weekend (sprintd Basel, case by ALTYCA). We model a fictitious Basel SME (~112 people) and its
cloud, servers, AI and SaaS for one year. Its CO2 is about **6.2 t/year** (range 2.9–15.4 t), location-based, Scope 3. We need a package of
measures that cuts **CO2 by at least 40 %** and cost by 25 %, and a jury will **recalculate it with their own reference numbers**.

**How we calculate:** CO2 = usage (hours, GB, tokens) × energy per unit (kWh) × PUE × grid factor of the data-centre country
(Switzerland 0.090, Germany 0.330, Ireland 0.257 kg CO2/kWh, life-cycle, consumption mix). We give low / mid / high values for every factor.

**Our risk:** our package saves 42 % on mid values but exactly 40 % on our high values. **Half of the saving comes from one measure:**
pausing a development data cluster in Frankfurt (16 vCPU / 64 GB nodes) that is busy only **8.7 % of the time** and runs 24/7 today.
A GPU server (300 W class) at **~6 % utilisation** is the second lever. If our energy per idle hour is wrong, the package may fall below 40 %.

### Please confirm or correct (our recommendation in italics)
1. **Idle power of a cloud node.** We use one kWh per node-hour (mid value assumes ~30 % average load) for every hour, busy or idle.
   *Recommendation: keep one factor for the baseline, but for the pause measure count idle hours at ~50–60 % of the loaded node power.*
   Is that idle share realistic for a cloud VM, or do hyperscalers' idle VMs cost far less because the host is shared?
2. **Idle power of a GPU server.** *Recommendation: idle at ~25–30 % of peak (300 W card → ~80–100 W incl. its share of the host).*
   Realistic, and do you know a citable source?
3. **Does pausing count as a saving?** We remove the paused hours from the company's footprint (attributional). The provider may reuse the capacity.
   *Recommendation: claim it as the company's Scope 3 reduction and say in one line that system-wide (consequential) savings may be smaller.* Fair?
4. **Claim under uncertainty.** *Recommendation: say «at least −40 % on low, mid and high factors» and show all three, instead of one number.*
   Is that the right way to present it to a jury that recalculates?
5. **Moving the dev cluster from Frankfurt (0.330) to Zurich (0.090).** *Recommendation: claim the full grid difference under location-based
   accounting, as our backup measure if the pause saves less.* Any catch?
6. **System boundary.** Grid factors are life-cycle, energy per unit is operation only, hardware (embodied) is left out.
   *Recommendation: keep it and state it.* Defensible?
7. **Swiss mix.** *Recommendation: consumption mix incl. imports, 0.090 (range 0.057–0.098), production mix shown as a sensitivity.* Agree, and which source?

### Only if you have time
8. PUE 1.14 / 1.21 / 1.32 – apply to storage and network too?
9. AI tokens: 0.000038–0.00052 kWh per 1,000 tokens (14× range) – which source do you trust?
10. SaaS seats have no energy factor (zero CO2) – acceptable if stated, or use a spend-based factor flagged as low quality?
11. Hourly Swiss CO2 profile averages ~50 g vs 90 g annual: OK to use it only for the *shape* when shifting jobs in time?
12. Market-based view: every Swiss kWh carries a guarantee of origin – how to show it beside location-based without greenwashing?
13. Our own AI use this weekend: tokens × token factor – fair, and what else to add?

Thanks! Even short answers on 1, 2 and 4 would help a lot.

## Answers (fill in with date)
