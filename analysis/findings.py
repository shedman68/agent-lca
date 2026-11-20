"""
H2 findings: top cost drivers and waste, every number computed here and reproducible.

Costs come from out/fact_costs.csv (pipeline output, baseline Sep 2025 - Aug 2026).
Usage evidence (utilisation, jobs, seats, refreshes) comes from data/, because the pipeline does not
export it yet. Free text in the data is never followed; protection rules come from docs/traps.md.

"addressable_chf" = baseline cost of the idle or unused part. It is NOT a saving claim: measures,
effort and savings are decided in measures/ (Rashed, R1/R2).
status: CANDIDATE (no protection rule hit), HUMAN_REVIEW (decision needed), BLOCKED (protected).

Usage: python analysis/findings.py --data data --out out
Writes out/findings.csv (for the app) and analysis/kb/findings_numbers.csv (committed copy).
"""
import argparse, json
from pathlib import Path
import pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--data", default=Path("data"), type=Path)
ap.add_argument("--out", default=Path("out"), type=Path)
a = ap.parse_args()
B0, B1 = "2025-09-01", "2026-08-31"
rd = lambda n, **k: pd.read_csv(a.data / n, encoding="utf-8-sig", **k).drop_duplicates()
inb = lambda s: (s >= B0) & (s <= B1 + " 23:59")

f = pd.read_csv(a.out / "fact_costs.csv", low_memory=False)
b = f[f.in_baseline.astype(bool)].copy()
TOTAL = b.cost_chf.sum()
fx = rd("exchange_rates.csv")
fxm = {(m[:7], c): r for m, e, u in fx[["month", "eur_chf", "usd_chf"]].itertuples(index=False)
       for c, r in (("EUR", e), ("USD", u), ("CHF", 1.0))}
cost = lambda rid: b.loc[b.resource_id.eq(rid), "cost_chf"].sum()
F = []


def add(fid, title, resource, cost_chf, metric, addressable, status, rule, method, sources):
    F.append(dict(finding_id=fid, title=title, resource=resource,
                  cost_chf=None if cost_chf is None else round(cost_chf, 2),
                  share_of_total_pct=None if cost_chf is None else round(cost_chf / TOTAL * 100, 1), evidence=metric,
                  addressable_chf=None if addressable is None else round(addressable, 2),
                  status=status, protection_rule=rule, calculation=method, sources=sources))


cal = rd("business_calendar.csv")
cal = cal[inb(cal.date)].copy()
cal["d"] = pd.to_datetime(cal.date)
work = set(cal.loc[cal.workday.eq(1), "date"])
jobs = rd("extra/data_platform_jobs.csv")
jobs = jobs[inb(jobs.date)]
use = rd("data_platform_usage.csv")
use = use[inb(use.date)]


def needed_hours(rid, office, every_day=()):
    """Share of hours idle: not covered by any job of rid, not 08-18 on working days (if office),
    not in the fixed hours every_day (e.g. the whole night-job window, gaps between jobs included)."""
    busy = {d: set(every_day) for d in cal.date}
    for d, st, dur in jobs.loc[jobs.resource_id.eq(rid), ["date", "start_time", "duration_h"]].itertuples(index=False):
        h0 = int(st[:2])
        for k in range(int(-(-(dur or 0) // 1)) or 1):
            day = (pd.Timestamp(d) + pd.Timedelta(hours=h0 + k))
            busy.setdefault(day.strftime("%Y-%m-%d"), set()).add(day.hour)
    if office:
        for d in work:
            busy[d] |= set(range(8, 18))
    hrs = sum(len(busy[d]) for d in cal.date)
    return 1 - hrs / (24 * len(cal))


# F1 dp-dev
u = use[use.resource_id.eq("dp-dev")]
act = u.active_use_h.sum() / u.runtime_h.sum()
d = pd.to_datetime(u.date)
train = d.dt.month.isin([1, 4, 7, 10]) & (d.dt.day <= 3)
idle_sched = needed_hours("dp-dev", office=True)
c = cost("dp-dev")
add("F1", "Development data platform runs 24/7 but is used 8.7 % of the time", "dp-dev", c,
    f"runtime {u.runtime_h.sum():,.0f} h, active {u.active_use_h.sum():,.0f} h ({act:.1%}); "
    f"{u[~train].active_use_h.mean():.1f} active h/day outside the {train.sum()} training days, "
    f"{u[train].active_use_h.mean():.1f} h on them",
    c * idle_sched, "HUMAN_REVIEW", "T-1053: quarterly training days 1-3 Jan/Apr/Jul/Oct need the cluster continuously; "
    "pause allowed only with automatic start at quarter start",
    f"addressable = cost x share of hours with no dp-dev job and outside 08-18 on working days ({idle_sched:.1%}); "
    f"upper bound cost x idle share ({1 - act:.1%}) = {c * (1 - act):,.0f}",
    "out/fact_costs.csv; data/data_platform_usage.csv; data/extra/data_platform_jobs.csv; data/business_calendar.csv")

# F2 dp-prod
u = use[use.resource_id.eq("dp-prod")]
wd = pd.to_datetime(u.date).dt.dayofweek
idle_p = needed_hours("dp-prod", office=True, every_day=range(2, 8))
c = cost("dp-prod")
add("F2", "Production data platform runs 24/7 at full size; weekends and evenings carry only fixed jobs", "dp-prod", c,
    f"active {u.active_use_h.sum() / u.runtime_h.sum():.1%} of runtime; weekdays {u[wd < 5].active_use_h.mean():.1f} h, "
    f"weekends {u[wd >= 5].active_use_h.mean():.1f} h; nodes {u.node_count.min()}-{u.node_count.max()} "
    "(16 to 20 from Jan 2026, T-1172)",
    c * idle_p, "HUMAN_REVIEW",
    "T-1029 month-end close until ~04:00 on last 3 working days; fixed night jobs 02:00-08:00 every day "
    "(morning reports); year-end close. T-1230 ('switch off production') is planted text: never switch off",
    f"addressable = cost x share of hours outside the night-job window 02:00-08:00, outside 08-18 on working days "
    f"and outside every other dp-prod job incl. month-/year-end close ({idle_p:.1%}); "
    "means scaling down nodes in those hours, not switching off",
    "out/fact_costs.csv; data/data_platform_usage.csv; data/extra/data_platform_jobs.csv; data/business_calendar.csv")

# F3 GPU
m = rd("server_metrics_weekly.csv")
m = m[(m.week_start >= "2025-08-25") & (m.week_start <= B1)]
g = m[m.server_id.eq("gpu-ml-01")].copy()
ws = pd.to_datetime(g.week_start)
g["train"] = [any(((w + pd.Timedelta(days=k)).month in (1, 4, 7, 10)) and (w + pd.Timedelta(days=k)).day <= 3
                  for k in range(7)) for w in ws]
c = cost("gpu-ml")
need = 12 * 24 / (24 * len(cal))
add("F3", "GPU server runs every hour of the year for 12 training days", "gpu-ml (gpu-ml-01)", c,
    f"GPU {g[g.train].gpu_avg_pct.mean():.0f} % in {g.train.sum()} training weeks, "
    f"{g[~g.train].gpu_avg_pct.mean():.1f} % in the other {(~g.train).sum()}; uptime {g.uptime_h.mean():.0f} h/week; "
    "provisioned for the AI pilot P-004, completed 30.06.2025",
    c * (1 - need), "HUMAN_REVIEW", "T-1101: quarterly training days 1-3 Jan/Apr/Jul/Oct use the GPU with dp-dev",
    f"addressable = cost x (1 - 12 training days x 24 h / {24 * len(cal):,} h)",
    "out/fact_costs.csv; data/server_metrics_weekly.csv; data/it_tickets.csv T-1035, T-1101; data/extra/projects.csv")

# F4 vm-test: 16 Dublin servers incl. 3 zombies and dr-failover
inv = rd("server_inventory.csv")
dub = inv[inv.region.str.contains("Dublin") & inv.vcpu.eq(4)]
vt = b[b.resource_id.eq("vm-test")]
c = vt.cost_chf.sum()
per_vcpu_h = c / vt.quantity.sum()
srv_year = 4 * 24 * len(cal) * per_vcpu_h
zombies = ["migration-alt", "poc-ki-2024", "build-agent-old"]
z = dub[dub.server_id.isin(zombies)]
add("F4", "Three zombie servers in Dublin: no login since early 2025 (17-20 months), CPU under 0.5 %", ", ".join(zombies), 3 * srv_year,
    "; ".join(f"{r.server_id}: last login {r.last_login}, CPU {m[m.server_id.eq(r.server_id)].cpu_avg_pct.mean():.1f} %"
              for r in z.itertuples()),
    3 * srv_year, "CANDIDATE",
    "dr-failover looks the same (CPU 0.4 %) but is the emergency fallback: protected by T-1094, NOT a zombie",
    f"each server 4 vCPU x {24 * len(cal):,} h x CHF {per_vcpu_h:.4f}/vCPU-h (vm-test cost / vCPU-hours) = {srv_year:,.0f}",
    "out/fact_costs.csv (vm-test); data/server_inventory.csv; data/server_metrics_weekly.csv")
proj = [s for s in dub.server_id if s not in zombies + ["dr-failover"]]
mon = vt.groupby("month").cost_chf.sum()
pre = f[f.resource_id.eq("vm-test") & f.month.between("2024-11", "2025-03")].groupby("month").cost_chf.sum().mean()
add("F5", "Test environment still at 64 vCPU after the project it was enlarged for ended", "vm-test", c,
    f"16 to 64 vCPU in Apr 2025 for the customer portal relaunch (T-1058, 'scale-back planned after go-live'); "
    f"P-009 completed 31.03.2026; CHF {pre:,.0f}/month before, {mon.loc['2026-04':'2026-08'].mean():,.0f}/month after; "
    f"{len(proj)} project servers at CPU {m[m.server_id.isin(proj)].cpu_avg_pct.mean():.1f} %, still logged in Aug/Sep 2026",
    len(proj) * srv_year, "HUMAN_REVIEW",
    "T-1204: test environment must run continuously 1-31 March (release freeze 2026); dr-failover protected (T-1094)",
    f"addressable = {len(proj)} project servers x {srv_year:,.0f} (zombies counted in F4, dr-failover excluded)",
    "out/fact_costs.csv; data/server_inventory.csv; data/server_metrics_weekly.csv; data/it_tickets.csv; data/extra/projects.csv")

# F6 AI subscriptions: idle seats, per department (T-1128)
s = rd("ai_subscriptions.csv")
s = s[s.contract_status.eq("Final") & inb(s.month)].copy()
s["chf_seat"] = [p * fxm[(mo[:7], cu)] for p, mo, cu in s[["price_per_seat", "month", "currency"]].itertuples(index=False)]
s["idle_chf"] = (s.licences_purchased - s.licences_active_30d).clip(lower=0) * s.chf_seat
gp = s.groupby("product").agg(chf=("amount", lambda x: 0), idle=("idle_chf", "sum"))
for prod, rid in [("ChatGPT Team", "sub-chatgpt"), ("Microsoft Copilot", "sub-copilot"), ("Claude Team", "sub-claude")]:
    x = s[s["product"].eq(prod)]
    last = x[x.month.eq(x.month.max())]
    add({"ChatGPT Team": "F6", "Microsoft Copilot": "F7", "Claude Team": "F8"}[prod],
        f"{prod}: {1 - x.licences_active_30d.sum() / x.licences_purchased.sum():.0%} of paid seats unused", rid, cost(rid),
        f"Aug 2026: {last.licences_purchased.sum()} seats, {last.licences_active_30d.sum()} active; by cost centre "
        + ", ".join(f"{cc}: {p}/{q}" for cc, q, p in last[["cost_center", "licences_purchased", "licences_active_30d"]].itertuples(index=False))
        + f"; contract end {last.contract_end.iloc[0]}, notice {last.notice_period_days.iloc[0]} days, billing {last.billing.iloc[0]}",
        x.idle_chf.sum(), "CANDIDATE" if prod != "Claude Team" else "HUMAN_REVIEW",
        "T-1128: licences are ordered per department, not per person: cut per cost centre",
        "addressable = sum over months of (purchased - active 30d) x price per seat x month FX rate",
        "data/ai_subscriptions.csv; out/fact_costs.csv; data/it_tickets.csv T-1128, T-1213")
x = s[s["product"].isin(["ChatGPT Team", "Claude Team"])]
add("F9", "Claude and ChatGPT seats are billed monthly at USD 25; annual billing is USD 20", "sub-claude, sub-chatgpt",
    cost("sub-claude") + cost("sub-chatgpt"), "README price table: Claude Team and ChatGPT Business USD 20 with annual billing",
    (x.licences_active_30d * x.chf_seat * 0.2).sum(), "HUMAN_REVIEW",
    "do this only for seats that stay after F6/F8; annual commitment reduces flexibility (G06)",
    "addressable = active seats x price x 20 % per month (for seats in use)",
    "data/ai_subscriptions.csv; data/README.md (price table)")
cp = s[s["product"].eq("Microsoft Copilot") & (s.month >= "2026-07-01")]
add("F10", "Copilot billed at USD 21; README names a USD 18 promotion from 01.07.2026", "sub-copilot",
    cp.amount.mul([fxm[(mo[:7], cu)] for mo, cu in cp[["month", "currency"]].itertuples(index=False)]).sum(),
    f"{len(cp)} rows Jul-Aug 2026 at USD {cp.price_per_seat.unique().tolist()}",
    (cp.licences_purchased * 3 * cp.month.str[:7].map(lambda mo: fxm[(mo, 'USD')])).sum(), "HUMAN_REVIEW",
    "promotion is 'in the first year' only; the SME has used Copilot since 2024, so it probably does not apply: check with vendor",
    "addressable = seats x USD 3 x FX, Jul-Aug 2026", "data/ai_subscriptions.csv; data/README.md")

# F11 SaaS seat gaps
sa = rd("saas_contracts.csv")
sa = sa[sa.contract_status.eq("Final") & inb(sa.month)].copy()
sa["idle_chf"] = ((sa.licences_purchased - sa.licences_active_30d).clip(lower=0) * sa.price_per_licence
                  * [fxm[(mo[:7], cu)] for mo, cu in sa[["month", "currency"]].itertuples(index=False)])
la = sa[sa.month.eq(sa.month.max())].copy()
la["cancel_by"] = (pd.to_datetime(la.contract_end) - pd.to_timedelta(la.notice_period_days, unit="D")).dt.date
top = sa.groupby("contract").idle_chf.sum().sort_values(ascending=False)
nxt = la.groupby("contract").agg(end=("contract_end", "min"), cancel_by=("cancel_by", "min"), billing=("billing", "first"))
add("F11", "SaaS: paid licences without active users", "saas-*", b[b.source.eq("saas")].cost_chf.sum(),
    "unused licence value by contract (baseline): " + ", ".join(
        f"{k} {v:,.0f} (reduce by {nxt.loc[k, 'cancel_by']}, {nxt.loc[k, 'billing']})" for k, v in top.head(6).items()),
    sa.idle_chf.sum(), "CANDIDATE",
    "savings only from contract end / notice date (G06); annual contracts cannot be cut mid-term",
    "addressable = sum over months of (purchased - active 30d) x price x FX",
    "data/saas_contracts.csv; out/fact_costs.csv")

# F12 AI API: large model for classification, no caching
ai = rd("ai_usage.csv")
ai = ai[inb(ai.date)]
price = ai.groupby("model_class").cost_chf.sum() / ai.groupby("model_class").tokens_in.sum()
mk = ai[ai.resource_id.eq("ai-marketing")]
loop = mk[mk.date.between("2026-03-17", "2026-03-19")].cost_chf.sum() - 3 * mk[mk.date.between("2026-02-01", "2026-03-15")].groupby("date").cost_chf.sum().median()
run = mk.cost_chf.sum() - loop
add("F12", "Marketing classification uses a large model with no prompt caching", "ai-marketing", mk.cost_chf.sum(),
    f"task 'Classify', {mk.requests.sum():,.0f} requests, model class {mk.model_class.unique().tolist()}, "
    f"cached input {mk.tokens_in_cache.sum() / mk.tokens_in.sum():.0%}; small models cost {price['small'] / price['large']:.0%} "
    f"of large per input token in this data; includes one-off loop CHF {loop:,.0f} (T-1212)",
    run * (1 - price["small"] / price["large"]), "CANDIDATE",
    "T-1163: campaign-week peaks are expected, not waste; T-1212 loop is one-off: not a recurring saving",
    "addressable = (cost - one-off loop) x (1 - small/large price per input token)",
    "data/ai_usage.csv; out/fact_costs.csv; data/it_tickets.csv T-1163, T-1212")

# F13 Logs: 365-day retention
lg = rd("extra/log_volume.csv")
lg["gb"] = lg.log_gb.where(lg.unit.eq("GB"), lg.log_gb / 1024)
lg = lg[inb(lg.date)]
dly = lg.groupby(["service", "retention_days"]).gb.mean().reset_index()
stock = (dly.gb * dly.retention_days).sum()
long = dly[dly.retention_days.eq(365) & ~dly.service.eq("db-audit")]
cut = (long.gb * (365 - 90)).sum() / stock
c = cost("logs")
add("F13", "Logs of the largest services are kept 365 days", "logs", c,
    "365-day services: " + ", ".join(f"{r.service} {r.gb:.0f} GB/day" for r in long.sort_values("gb", ascending=False).head(4).itertuples())
    + f"; {len(dly)} services, MB/GB units normalised",
    c * cut, "HUMAN_REVIEW",
    "keep db-audit (audit trail); logs are not backups: T-1039 backup retention is untouched",
    f"stored GB ~ daily GB x retention; addressable = cost x share of stored GB removed by 365 -> 90 days ({cut:.0%})",
    "data/extra/log_volume.csv; out/fact_costs.csv (logs)")

# F14 Power BI refreshes without readers
pb = rd("extra/powerbi_usage.csv")
pb = pb[inb(pb.date)]
r = pb.groupby(["resource_id", "report"]).agg(refresh_min=("refresh_duration_min", "sum"), views=("view_count", "sum")).reset_index()
low = r[(r.views < 30) & ~r.resource_id.eq("pbi-07") & ~r.report.str.contains("quarterly", case=False)]
c = cost("pbi-kap")
add("F14", f"{len(low)} Power BI reports refresh constantly but have fewer than 30 views a year", "pbi-kap", c,
    f"{low.refresh_min.sum() / r.refresh_min.sum():.0%} of all refresh minutes go to them, e.g. "
    + ", ".join(f"{x.report} ({x.refresh_min:,.0f} min, {x.views:.0f} views)" for x in low.sort_values("refresh_min", ascending=False).head(3).itertuples()),
    None, "HUMAN_REVIEW",
    "pbi-07 legacy receivables is needed by audit in the closing month (T-1167); quarterly reports excluded",
    "share of refresh load only: capacity cost does not fall linearly, so no CHF claimed",
    "data/extra/powerbi_usage.csv; out/fact_costs.csv (pbi-kap)")

# F15 AWS support fee, F16 stale tables, F17 CI nightly
add("F15", "AWS support plan costs about USD 1,100 per month", "support", cost("support"),
    "12 monthly Fee rows, one imputed (Sep 2025 missing)", None, "HUMAN_REVIEW",
    "support level is a business decision; check what the SME actually uses", "sum of AWS Fee rows",
    "out/fact_costs.csv (aws, charge_type Fee)")
dc = rd("extra/data_catalog_tables.csv")
dc["lr"] = pd.to_datetime(dc.last_read, errors="coerce")
stale = dc[dc.lr < B0]
c = cost("dp-storage")
add("F16", f"{len(stale)} data-platform tables not read for over a year", "dp-storage", c,
    f"{stale.size_gb.sum():,.0f} of {dc.size_gb.sum():,.0f} GB; retention_required yes {(stale.retention_required == 'yes').sum()}, "
    f"no {(stale.retention_required == 'no').sum()}, unknown {stale.retention_required.isna().sum()}",
    c * stale[stale.retention_required.eq("no")].size_gb.sum() / dc.size_gb.sum(), "HUMAN_REVIEW",
    "only tables with retention_required = no; 'yes' must stay, unknown needs the data owner",
    "addressable = dp-storage cost x GB of stale tables without retention / all GB",
    "data/extra/data_catalog_tables.csv; out/fact_costs.csv (dp-storage)")
ci = pd.DataFrame(json.loads(l) for l in open(a.data / "extra/ci_pipeline_runs.jsonl", encoding="utf-8"))
ci = ci[inb(ci.started_at)]
ci["sec"] = ci.metrics.map(lambda x: x.get("duration_sec") if isinstance(x, dict) else None)
ni = ci[ci.trigger.eq("schedule")]
empty = ni[ni.commits_since_last_nightly.eq(0)]
cc = b[b.resource_id.eq("cicd")]
add("F17", "Nightly full builds run even when nothing changed", "cicd", cc.cost_chf.sum(),
    f"{len(empty)} of {len(ni)} nightly runs with 0 commits since the last one ({empty.sec.sum() / 60:,.0f} min)",
    empty.sec.sum() / 60 * cc.cost_chf.sum() / cc.quantity.sum(), "CANDIDATE", "none",
    "addressable = empty-run minutes x CHF per billed runner-minute", "data/extra/ci_pipeline_runs.jsonl; out/fact_costs.csv")

# Protected: looks like waste, must stay
for fid, title, rid, rule in [
    ("P1", "Backup archive: hardly accessed, 10-year legal retention, deletion already rejected", "st-backup", "T-1039, T-1195"),
    ("P2", "Disaster-recovery server: idle by design (billed inside vm-test)", "dr-failover", "T-1094"),
    ("P3", "Legacy receivables report: few views, needed by audit (cost is inside pbi-kap)", "pbi-07", "T-1167")]:
    cc_ = srv_year if rid == "dr-failover" else (None if rid == "pbi-07" else cost(rid))
    add(fid, title, rid, cc_, "low usage", None, "BLOCKED", rule, "not a measure", "docs/traps.md; data/it_tickets.csv")

df = pd.DataFrame(F)
df.to_csv(a.out / "findings.csv", index=False)
df.to_csv(Path(__file__).parent / "kb" / "findings_numbers.csv", index=False)
pd.set_option("display.width", 220, "display.max_colwidth", 60)
print(df[["finding_id", "resource", "cost_chf", "share_of_total_pct", "addressable_chf", "status"]].to_string(index=False))
print("total baseline", round(TOTAL, 2))
