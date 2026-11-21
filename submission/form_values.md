# sprintd form – values for the 15:00 draft (review and approve)

Every number below comes from `out/` and `measures/package_summary.csv` on main (MATCH, TRAP GUARD: PASS).
Reply «approve» or a change in Slack. Nobody presses Submit before every teammate has approved and Rashed has written «submit».

**Project title** – GreenOps Basel

**Slogan** – Shows a Basel SME where its cloud, AI and SaaS create CO2 and cost, and a safe package that cuts CO2 by 43 % and cost by 29 % in 14.5 person-days.

**Description**

*The problem.* «Electricity is the new currency, and hardly anyone keeps the books.» A Basel company of about 112 people runs cloud, servers, AI and SaaS in several countries for CHF 470,289 a year. The invoices show francs; nobody sees the energy and CO2 behind them. ALTYCA: «The CO2 impact is at the centre, the savings in francs come on top.»

*Our solution.* A CO2-first app a manager understands in two minutes. Connect: the case files become one baseline that matches the invoices to the franc (CHF 470,288.93, checked three ways). Find: findings with cost, energy and CO2 for each, and their source. Decide: a package of eight measures plus one AI routing change that cuts location-based CO2 by 43.0 % (49.6 % on low factors, 42.2 % on high), cost by 28.6 % (CHF 134,306 a year) within 14.5 person-days (CHF 15,950). Know the limits: planted instructions in the data are refused, protected systems are never switched off, and every decision a human must take names the responsible role.

*How it works, real and mocked.* Python pipeline → findings → measures → Streamlit app, all offline. Real: every cost, energy and CO2 number is computed from the ALTYCA sample data; two automatic checks (baseline match, trap guard) run before every merge. Assumptions: energy and grid factors with low/mid/high ranges and sources, realisation shares and person-days per measure. Limited: the «Ask the data» assistant is an offline keyword router over the same calculations; a Claude mode exists but is off in the demo. Nothing is invented.

*Next four weeks.* Connect live billing exports (AWS, Azure, AI gateway) instead of files; hourly Swiss grid factors for load shifting; pilot the two biggest measures with a real SME and ALTYCA, inside the protection windows; DE/EN, Swiss number formats and a data-stays-local setup for the DACH market; count our own AI energy in full.

**Case** – linked automatically.

**Repository URL** – https://github.com/shedman68/agent-lca (README: run steps, real vs mocked, AI tools note)

**Video pitch URL** – to be set: `submission/media/agent-lca-demo-walkthrough.mp4` (112 s, captions, no voice) uploaded as an unlisted YouTube video. Final video with voice for Sunday.

**Project ZIP** – optional; not needed for the draft (everything is in the repo).

**Thumbnail** – `submission/media/thumbnail-600.png` (Package page, 600×600).

**Checkbox** – own work from the event: tick only after everyone approves.

Data citation: «Sample data ALTYCA, sprintd Basel 2026».
