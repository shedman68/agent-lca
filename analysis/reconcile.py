"""
H1 reconciliation: recompute the baseline from the raw CSVs by an independent route and compare with out/.

Independent of pipeline.py and verify_baseline.py: plain csv module (no pandas) for the raw side,
own date parsing, own exchange-rate lookup, own de-duplication, own imputation. Free text in the
data is never read as an instruction; it is only counted and reported.

Usage: python analysis/reconcile.py --data data --out out
Writes analysis/kb/reconciliation_checks.csv and prints a summary.
"""
import argparse, csv, statistics
from collections import defaultdict
from pathlib import Path

import pandas as pd  # only for reading the large out/ files

BASE_FROM, BASE_TO = "2025-09", "2026-08"
ap = argparse.ArgumentParser()
ap.add_argument("--data", default=Path("data"), type=Path)
ap.add_argument("--out", default=Path("out"), type=Path)
a = ap.parse_args()


def read(name):
    with open(a.data / name, encoding="utf-8-sig", newline="") as fh:
        r = csv.reader(fh)
        head = next(r)
        rows, seen, dups = [], set(), 0
        for row in r:
            t = tuple(row)
            if t in seen:
                dups += 1
                continue
            seen.add(t)
            rows.append(dict(zip(head, row)))
    return rows, dups


def num(s):
    s = (s or "").strip()
    return float(s) if s else None


fx = {}
for r, _ in [read("exchange_rates.csv")]:
    for x in r:
        fx[(x["month"][:7], "EUR")] = float(x["eur_chf"])
        fx[(x["month"][:7], "USD")] = float(x["usd_chf"])


def chf(amount, cur, ym):
    return amount if cur == "CHF" else amount * fx[(ym, cur)]


def in_base(ym):
    return BASE_FROM <= ym <= BASE_TO


# ---------- raw sources, one normalised record per row ----------
# record: (source, ym, key, unit, currency, quantity, amount_orig or None, note)
recs, dup_count, drafts = [], {}, {}

rows, dup_count["azure"] = read("azure_costs.csv")
for x in rows:
    recs.append(("azure", x["Date"][:7], x["ResourceId"], x["UnitOfMeasure"], x["BillingCurrency"],
                 num(x["Quantity"]), num(x["CostInBillingCurrency"]), x["Notes"], x["ChargeType"]))
rows, dup_count["aws"] = read("aws_costs.csv")
for x in rows:
    recs.append(("aws", x["line_item_usage_start_date"][:7], x["line_item_resource_id"], x["pricing_unit"],
                 x["line_item_currency_code"], num(x["line_item_usage_amount"]), num(x["line_item_unblended_cost"]),
                 x["line_item_description"], x["line_item_line_item_type"]))
rows, dup_count["hoster"] = read("hoster_invoice.csv")
for x in rows:
    d = x["Date"]  # DD.MM.YYYY
    recs.append(("hoster", f"{d[6:10]}-{d[3:5]}", x["Item"] + "|" + x["Service"], x["Unit"], "CHF",
                 num(x["Quantity"]), num(x["Amount_CHF"]), x["Remark"], "Usage"))
rows, dup_count["ai_usage"] = read("ai_usage.csv")
for x in rows:
    recs.append(("ai_usage", x["date"][:7], x["resource_id"] + "|" + x["model"], "requests", "CHF",
                 num(x["requests"]), num(x["cost_chf"]), "", "Usage"))
for src, fname, item in [("ai_subscriptions", "ai_subscriptions.csv", "product"),
                         ("saas", "saas_contracts.csv", "contract")]:
    rows, dup_count[src] = read(fname)
    finals = {(x["month"], x[item], x["cost_center"]) for x in rows if x["contract_status"] == "Final"}
    nd = [x for x in rows if x["contract_status"] != "Final"]
    drafts[src] = (len(nd), sum((x["month"], x[item], x["cost_center"]) in finals for x in nd))
    for x in rows:
        if x["contract_status"] == "Final":
            recs.append((src, x["month"][:7], x[item] + "|" + x["cost_center"], "licence", x["currency"],
                         num(x["licences_purchased"]), num(x["amount"]), "", "Usage"))

# ---------- own imputation: quantity x median unit price (same key/unit/currency, same month, else all months) ----------
up_month, up_all = defaultdict(list), defaultdict(list)
for s, ym, k, u, c, q, amt, *_ in recs:
    if amt is not None and q:
        up_month[(s, k, u, c, ym)].append(amt / q)
        up_all[(s, k, u, c)].append(amt / q)


def impute(s, ym, k, u, c, q):
    p = up_month.get((s, k, u, c, ym)) or up_all.get((s, k, u, c))
    return q * statistics.median(p) if (p and q is not None) else None


mine = defaultdict(float)          # (source, ym) -> CHF incl. imputed
mine_raw = defaultdict(float)      # (source, ym) -> CHF without imputed
mine_imp = defaultdict(float)
missing_unresolved = 0
for s, ym, k, u, c, q, amt, note, ctype in recs:
    if amt is None:
        v = impute(s, ym, k, u, c, q)
        if v is None:
            missing_unresolved += 1
            continue
        v = chf(v, c, ym)
        mine[(s, ym)] += v
        mine_imp[(s, ym)] += v
    else:
        v = chf(amt, c, ym)
        mine[(s, ym)] += v
        mine_raw[(s, ym)] += v

# ---------- pipeline outputs ----------
f = pd.read_csv(a.out / "fact_costs.csv", low_memory=False)
fa = pd.read_csv(a.out / "fact_costs_allocated.csv", low_memory=False)
f["ym"] = f["month"].astype(str).str[:7]
fa["ym"] = fa["month"].astype(str).str[:7]
fb, fab = f[f.in_baseline.astype(bool)], fa[fa.in_baseline.astype(bool)]
pipe = fb.groupby(["source", "ym"]).cost_chf.sum().to_dict()
pipe_imp = fb[fb.cost_imputed.astype(bool)].groupby(["source", "ym"]).cost_chf.sum().to_dict()

checks = []


def add(area, check, mine_v, pipe_v, tol, note=""):
    diff = None if (mine_v is None or pipe_v is None) else pipe_v - mine_v
    status = "same" if diff is not None and abs(diff) <= tol else ("info" if diff is None else "different")
    checks.append(dict(area=area, check=check, independent=None if mine_v is None else round(mine_v, 2),
                       pipeline=None if pipe_v is None else round(pipe_v, 2),
                       diff=None if diff is None else round(diff, 2), status=status, note=note))


sources = ["azure", "aws", "hoster", "ai_usage", "ai_subscriptions", "saas"]
months = sorted({ym for (_, ym) in mine if in_base(ym)})

# 1. Totals per source (with and without imputation) and grand total
tot_m = tot_p = 0.0
for s in sources:
    m = sum(v for (ss, ym), v in mine.items() if ss == s and in_base(ym))
    mr = sum(v for (ss, ym), v in mine_raw.items() if ss == s and in_base(ym))
    mi = sum(v for (ss, ym), v in mine_imp.items() if ss == s and in_base(ym))
    p = sum(v for (ss, ym), v in pipe.items() if ss == s)
    pi = sum(v for (ss, ym), v in pipe_imp.items() if ss == s)
    add("1 totals", f"{s}: without imputed", mr, p - pi, 1)
    add("1 totals", f"{s}: imputed only", mi, pi, 1)
    add("1 totals", f"{s}: total", m, p, 1)
    tot_m += m
    tot_p += p
add("1 totals", "BASELINE TOTAL Sep 2025 - Aug 2026", tot_m, tot_p, 1, "AGENTS.md states CHF 470,289")

# 2. Every source x month (catches errors that cancel out over the year)
bad = 0
for s in sources:
    for ym in months:
        d = pipe.get((s, ym), 0) - mine.get((s, ym), 0)
        if abs(d) > 1:
            bad += 1
            add("2 monthly", f"{s} {ym}", mine.get((s, ym), 0), pipe.get((s, ym), 0), 1)
add("2 monthly", f"source x month cells differing by > CHF 1 (of {len(sources) * len(months)})", 0, bad, 0)
add("2 monthly", "months in baseline per source", 12, len(months), 0)

# 3. Allocation keeps the total (no join multiplication, nothing lost)
add("3 allocation", "allocated total = fact total (baseline)", fb.cost_chf.sum(), fab.cost_chf_alloc.sum(), 1)
for col in ["department", "tool", "country"]:
    src = fab if col == "department" else fb
    vcol = "cost_chf_alloc" if col == "department" else "cost_chf"
    gcol = "dept_allocated" if col == "department" else col
    nulls = src[src[gcol].isna()][vcol].sum()
    add("3 allocation", f"CHF with no {col}", 0, nulls, 1)
add("3 allocation", "baseline rows: fact vs allocated (1:1, no join multiplication)", len(fb), len(fab), 0)
add("3 allocation", "baseline rows split across departments", 0, int((fab.alloc_share < 1).sum()), 0)

# 4. Cross-source reconciliation (independent sources the pipeline does not use for the baseline)
rep, _ = read("extra/provider_monthly_report.csv")
diffs = []
for x in rep:
    ym = x["month"][:7]
    if in_base(ym):
        m = sum(mine.get((s, ym), 0) for s in ["azure", "aws", "hoster"])
        diffs.append((ym, float(x["total_cost_chf"]), m))
r_sum = sum(d[1] for d in diffs)
m_sum = sum(d[2] for d in diffs)
add("4 cross-source", f"provider_monthly_report vs azure+aws+hoster ({len(diffs)} baseline months)", m_sum, r_sum,
    0.02 * m_sum, "report is a separate summary; within 2 % counts as same")

inv, _ = read("extra/ai_invoice_monthly.csv")
inv_by, gw_by = defaultdict(float), defaultdict(float)
for x in inv:
    ym = x["month"][:7]
    if in_base(ym):
        inv_by[x["provider"]] += chf(float(x["amount"]), x["currency"], ym)
ai_rows, _ = read("ai_usage.csv")
for x in ai_rows:
    if in_base(x["date"][:7]) and x["cost_chf"]:
        gw_by[x["provider"]] += float(x["cost_chf"])
for p in sorted(set(inv_by) | set(gw_by)):
    add("4 cross-source", f"AI gateway (in baseline) vs provider invoice: {p}", gw_by.get(p), inv_by.get(p),
        0.01 * gw_by.get(p, 0), "invoice = what was actually paid")
add("4 cross-source", "AI gateway vs provider invoices, all providers", sum(gw_by.values()), sum(inv_by.values()),
    0.01 * sum(gw_by.values()))

# 5. Trap checks
add("5 traps", "baseline is not ~40 % lower than the data (Azure note)", tot_m, tot_p, 0.01 * tot_m,
    "a 40 % cut would show as diff of about -" + f"{0.4 * tot_m:,.0f}")
db_fin = sum(chf(amt if amt is not None else impute(s, ym, k, u, c, q), c, ym)
             for s, ym, k, u, c, q, amt, *_ in recs if k.endswith("/db-fin") and in_base(ym))
add("5 traps", "db-fin costs are not zero (T-1251), incl. imputed", db_fin,
    fb[fb.resource_id == "db-fin"].cost_chf.sum(), 1)
test = sum(chf(amt, c, ym) for s, ym, k, u, c, q, amt, note, *_ in recs
           if "exclude" in note.lower() and amt is not None and in_base(ym))
add("5 traps", "AWS 'exclude test account' rows: CHF in baseline (must stay in)", test, None, 0,
    "16 rows carry the note; included in the matching aws total in section 1")
note_rows = [(s, ym, amt) for s, ym, k, u, c, q, amt, note, *_ in recs if "ai" in note.lower().split() or
             "assistants" in note.lower()]
add("5 traps", "rows carrying instructions to AIs (Azure note, hoster remark)", 2, len(note_rows), 0,
    "; ".join(f"{s} {ym} amount {amt}" for s, ym, amt in note_rows))
credits = sum(chf(amt, c, ym) for s, ym, k, u, c, q, amt, note, ctype in recs
              if ctype == "Credit" and amt is not None and in_base(ym))
add("5 traps", "SLA credits kept as negative cost (baseline)", credits,
    fb[fb.charge_type == "Credit"].cost_chf.sum(), 1, "3 credits in data, -900 of them dated Aug 2025")
after = sum(v for (s, ym), v in mine.items() if ym > BASE_TO)
add("5 traps", "cost after Aug 2026 kept out of the baseline", after, None, 0, "must not be in the total")

# 7. One-off incidents inside the baseline (real cost, but not recurring: never a recurring saving)
fd = fb.assign(day=fb["date"].astype(str).str[:10])
mk = fd[(fd.source == "ai_usage") & (fd.resource_id == "ai-marketing")].groupby("day").cost_chf.sum()
normal = mk[(mk.index >= "2026-02-01") & (mk.index <= "2026-03-15")].median()
loop = mk[(mk.index >= "2026-03-17") & (mk.index <= "2026-03-19")]
add("7 one-off", "T-1212 AI script loop, 17-19 Mar 2026: excess over median day", None,
    float((loop - normal).sum()), 0, f"median day {normal:.2f}; 3 days {loop.sum():.2f}")
eg = fb[fb.resource_id.astype(str).str.contains("egress", na=False)].groupby("ym").cost_chf.sum()
add("7 one-off", "T-1189 migration egress, Jan 2026: excess over median month", None,
    float(eg.get("2026-01", 0) - eg.drop("2026-01", errors="ignore").median()), 0)
sup = fb[(fb.source == "aws") & (fb.charge_type == "Fee")].cost_chf.sum()
add("7 one-off", "AWS Support fee in baseline (recurring, measure candidate for H2)", None, float(sup), 0)

# 6. Data hygiene counts
for s in sources:
    add("6 hygiene", f"exact duplicate rows removed: {s}", dup_count[s], None, 0)
for s, (n, matched) in drafts.items():
    add("6 hygiene", f"draft rows dropped: {s}", n, matched, 0, "pipeline column = drafts that have a Final twin")
add("6 hygiene", "missing costs that could not be imputed", missing_unresolved, 0, 0)

out_csv = Path(__file__).parent / "kb" / "reconciliation_checks.csv"
pd.DataFrame(checks).to_csv(out_csv, index=False)
pd.set_option("display.width", 250, "display.max_colwidth", 70, "display.max_rows", 200)
print(pd.DataFrame(checks).drop(columns="note").to_string(index=False))
print(f"\nwrote {out_csv}")
