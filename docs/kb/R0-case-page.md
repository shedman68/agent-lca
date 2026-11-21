# R0 – Case page on app.sprintd.org (copied by Rashed, Sat 21.11. 21:32)

- **Source:** the sprintd case page «Green AI & Data» (ALTYCA with Basel 2037), pasted by Rashed. Verbatim below. Use it for the story, the business case and the requirements.

---

Electricity is the new currency, and hardly anyone keeps the books
The problem today
Digital work causes costs, electricity use and CO₂: in the cloud and data centres, through AI subscriptions, tokens and agents, and in software licences. Hardly any SME in Basel knows exactly where. The figures sit in many systems and formats, with several providers and in three currencies. And not everything that looks unused may be switched off. For a Basel SME these are indirect emissions (Scope 3): the electricity flows into data centres in Zurich, Frankfurt or Dublin, but the decisions are made in Basel.

The expected outcome
A prototype that combines an SME's data into one overall picture, shows the biggest drivers and the waste, and recommends a package of measures that cuts CO₂ and costs and stays within budget. It respects protection windows, flags contradictions and hands over to a human when in doubt. Every figure is an estimate with an open calculation.

Who it serves
IT managers, management and finance managers of SMEs in Basel-Stadt. Basel 2037 supports SMEs on the way to net zero by 2037 and also wants to reduce the indirect emissions of the Basel economy; this case makes digital services measurable for SMEs. ALTYCA, a data and AI consultancy from Basel, brings the case together with Basel 2037 and is on site all weekend.

Data
- Delivery: ZIP with README, data dictionary, two submission templates and three example questions. Handed out at the kick-off, plus the link to the GitHub repository with all files.
- Sample SME: consulting and services company in Basel with around 112 employees. Data from November 2024 to September 2026.
- Locations: the SME is based in Basel. Most services run in Zurich, some in Frankfurt and Dublin. The calculation uses the electricity mix at the location: this shows which decision made in Basel causes how much CO₂, and where.
- Sources: 28 files (CSV and JSON lines): cloud invoices from Azure, AWS and a Swiss hoster, server inventory and metrics, data platform, AI gateway, AI subscriptions, AI agents, SaaS contracts, IT tickets, web, development, logs and backups.
- Core sources: 13 of the 28 files are enough for the must-have functions. They are directly in the main folder. The other 15 are bonus and are in the subfolder «extra».
- Data quality: as in real exports: gaps, drafts next to final versions, CHF, EUR and USD, changing units and column names, sources that contradict each other.
- Real data: exchange rates (ECB via Deutsche Bundesbank), public holidays in Basel-Stadt and list prices of AI models, subscriptions and computing power, each with its source.
- Not included: electricity mix per location, energy per unit and PUE. Teams research these factors themselves, with source, range and calculation. For the Swiss electricity mix, teams explain whether they use the production mix or the consumption mix including imports.

All usage data are synthetic and describe a fictitious company. They are not customer data.

Technology
- Allowed: any language, any framework and any tool. Excel, Power BI and no-code are explicitly allowed. Programming is not required.
- AI while building: AI assistants for code, texts and drafts are welcome. Teams that use AI also estimate its energy use.
- Not required: no hardware and no connection to real systems. Everything runs on the data provided.
- AI access: only needed for the bonus assistant, organised by sprintd.

Core use case
An IT manager loads her SME's exports. The prototype harmonises time, currency and names and allocates costs, energy and CO₂ (location-based) by department and tool. It shows the biggest drivers and the waste, for example a GPU server running around the clock or unused licences. It proposes measures with effort and savings and calculates whether the package meets the target and budget. If a measure falls into a protection window or sources contradict each other, it flags this and puts the decision to a human.

Business value
An overall picture in minutes instead of after weeks of data work. Targeted savings without risk to operations. The CO₂ impact is at the centre, the savings in francs come on top. And an approach that other SMEs can adopt.

Added value for Basel 2037: besides net zero by 2037 on its territory, the canton also wants to reduce the indirect emissions of the Basel economy. Digital services are part of this, but so far they can hardly be measured in SMEs. The case delivers a tested method (location-based, with an open calculation), prototypes from teams in the region and practical experience that Basel 2037 can use when advising and funding SMEs.

Optional stretch goals
- Chat assistant: answers questions about the data and measures and backs every answer with a calculation or source.
- Forecast: costs, energy and CO₂ for the coming years with ranges and justified assumptions (growth, known changes, seasonality), with and without the package of measures.
- Market-based view: CO₂ additionally based on electricity certificates, critically placed next to the location-based view.
- Clustering: find groups of similar usage and explain outliers. Further ideas: shift loads to hours with less CO₂ (carbon-aware computing) and slim down build pipelines (DevOps).
- The 15 bonus sources: integrate web, development, logs, backups, data catalogue and Power BI.

Bonus counts towards the criterion creativity & innovation. It is not required for a valid submission.

Presentation format
Sunday: submission on the platform at 08:30 (prototype and the two tables). Pitches 09:00 to 11:30 in a separate room per case: 5 minutes live demo, 3 minutes questions from ALTYCA. Slides optional. ALTYCA chooses the case winner by 12:00, who pitches in the Grand Finale (13:00 to 14:45).

Friday and Saturday: Friday 18:10 to 18:40 case presentation in the auditorium, 18:40 to 19:10 deep dive with ALTYCA, start of the sprint at 20:30. Saturday: mentors 09:00 to 20:00, draft submission 15:00 to 15:30.

Key presentation elements
- The overall picture: where costs, energy and CO₂ arise in the SME, by department and tool.
- One finding: one piece of waste found, backed up by the data.
- The package: measures with effort and savings in CHF and CO₂, calculated against target and budget.
- One edge case: a measure that the prototype does not recommend, or puts to a human, because of a protection window or a contradiction.

Plus a short statement of how much energy the team's own AI use has caused.

Prototype requirements
1. Connect: at least cloud, servers, AI and SaaS combined into one overall picture by department and tool.
2. Find: the biggest drivers and the waste, backed up by the data.
3. Decide: a package of measures with effort and savings in CHF and CO₂ (location-based). It reduces CO₂ by at least 40% and costs by at least 25% and costs no more than CHF 16,500 to implement (1 person-day = CHF 1,100).
4. Know the limits: protection windows respected, contradictions flagged, hand-over to a human when in doubt.
5. Two tables: baseline and assumptions as well as the package of measures according to the templates, all factors with source, range and calculation.

The prototype runs on the data provided, working or clickable. The form is free; a dashboard is not mandatory. Target and budget apply against the team's own baseline; the jury also recalculates against a uniform reference baseline. Plus a short note on what the path to operation would look like.

How the jury scores
Criterion	Weight	What we reward
Creativity & innovation	20%	Fresh ideas and bonus functions, for example an assistant, a forecast, clustering or visible trade-offs.
Feasibility	15%	Runs on the data provided and is realistic for an SME without a specialist department.
Design & usability	20%	An SME manager understands the overall picture, the package of measures and the reasoning in two minutes.
Impact & relevance	10%	The overall picture is correct, and the package meets target and budget with realistic savings in CO₂ and francs. The jury also recalculates every package against a uniform reference baseline.
Data preparation & pattern recognition	20%	At least cloud, servers, AI and SaaS cleanly connected (time, unit, currency, names), biggest drivers and waste backed up by the data.
Robustness & decision quality	15%	Protection windows respected, contradictions flagged, figures traceable, hand-over to a human when in doubt.
Prize
Present at ALTYCA's internal Project Insights (8 December or 12 January, dinner included), keep building with ALTYCA early next year, and join them on stage later.

