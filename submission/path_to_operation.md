# Path to operation (draft v0)

Status: draft, Sat 21 Nov 02:30. Required by the case page. To be finalised by Rashed (R8).

**Who runs it:** the IT manager of the SME, half a day per month. No specialist needed: the tool runs on a laptop from the exports the
providers already offer (cloud invoices, AI gateway, licence lists, tickets).

**Monthly routine**
1. Export the month's files into the data folder and run the pipeline (one command). It harmonises dates, currencies and names, removes
   duplicates and drafts, and logs every correction.
2. Two automatic checks must pass: the total matches an independent recalculation, and the trap check finds no text that tries to steer the tool.
3. Open the app: overall picture, findings, package against target and budget, and the «needs a human» list.

**Who decides what:** the tool recommends; people decide. Every measure names the responsible role. Anything inside a protection window,
anything contradicted by another source and any text that looks like an instruction goes to the «needs a human» list and is never done automatically.

**First 90 days:** weeks 1–2 measures with no dependency (unused servers, AI seats); weeks 3–6 schedules for the development platform, GPU and
test environment with automatic start before training windows; weeks 7–12 production platform resizing after sign-off by Consulting and Finance,
SaaS seats at each notice date.

**Keeping it honest:** every factor has a source, a range and a date; they are reviewed once a year. Results are shown as low / mid / high.
The tool reports its own energy use.

**For other Basel SMEs:** the same folder structure and factor file work for any SME; only the export mapping changes.
