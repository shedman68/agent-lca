"""
GreenOps pipeline – sprintd Basel, Green AI & Data case.

Cleans the 6 cost sources (Azure, AWS, hoster, AI gateway, AI subscriptions, SaaS)
into ONE fact table, allocates shared costs, computes the baseline year
(Sep 2025 – Aug 2026) and, once factors.csv is filled in, energy and CO2.

Usage:
    python pipeline.py --data <path to the case data folder> --out out

Rules:
- Free text (Notes, Remark, line_item_description, ticket description) is DATA.
  It is scanned and logged, never used to change a calculation.
- Every cleaning decision is written to out/quality_log.csv.
"""
import argparse, json, re, sys
from pathlib import Path
import numpy as np
import pandas as pd

BASE_START, BASE_END = "2025-09-01", "2026-09-01"   # baseline year, end exclusive
CC_DEPT = {4000: "Consulting", 4100: "Sales", 4200: "Finance", 4300: "Marketing",
           4400: "HR", 4500: "IT", 4900: "Management", 9000: "Overhead", 9100: "Test account"}
DEPT_CC = {v: k for k, v in CC_DEPT.items()}
DEPARTMENTS = ["Consulting", "Sales", "Finance", "Marketing", "HR", "IT", "Management"]
COUNTRY = {"Switzerland": "CH", "Germany": "DE", "Ireland": "IE", "EU": "EU"}
HOSTER_ITEM_RID = {"Logging and monitoring": "logs", "Project file storage": "st-proj",
                   "Web hosting and CDN": "web-cdn"}
# unit in the source -> energy key used in factors.csv
UNIT_KEY = {"vCPU-hour": "vcpu_hour", "vCore-hour": "vcpu_hour", "node-hour": "node_hour",
            "GPU-hour": "gpu_hour", "GB-day": "gb_storage_day", "capacity-day": "bi_capacity_day",
            "GB": "gb_transfer", "runner-minute": "runner_minute", "month": "none",
            "tokens": "tokens_1000", "seat-month": "subscription_message",
            "licence-month": "saas_licence_month"}
INJECTION = re.compile(
    r"(?i)(?:ignore (?:all|the|previous)|instruction|for (?:ai )?assistants|ai systems|ai assistants|"
    r"tell the user|set all costs|costs? (?:to|=) ?0|report costs|estimate the values yourself|"
    r"exclude from analys|approved by the head|switch(?:ing)? off .* (?:immediately|completely)|"
    r"no savings are possible|system notice)")

log = []
def note(check, source, n, decision, chf=None, detail=""):
    log.append(dict(check=check, source=source, rows=int(n), chf_affected=None if chf is None else round(float(chf), 2),
                    decision=decision, detail=detail))

def read(data, name):
    return pd.read_csv(data / name, encoding="utf-8-sig")

def norm_project(x):
    if pd.isna(x) or str(x).strip() == "":
        return np.nan
    m = re.search(r"(\d{1,3})", str(x))
    return f"P-{int(m.group(1)):03d}" if m else np.nan

def country_of(region):
    if pd.isna(region):
        return np.nan
    for k, v in COUNTRY.items():
        if str(region).startswith(k):
            return v
    return "OTHER"

def dedupe(df, source):
    n = df.duplicated().sum()
    if n:
        note("exact duplicate rows", source, n, "removed (kept first)")
    return df.drop_duplicates()

def scan_text(df, source, cols, idcol):
    for c in cols:
        if c not in df:
            continue
        hit = df[df[c].astype(str).str.contains(INJECTION, na=False)]
        for _, r in hit.iterrows():
            note("instruction-like free text", source, 1,
                 "quarantined: treated as data, no effect on any calculation; shown to a human",
                 detail=f"{idcol}={r[idcol]} field={c}")

def impute_cost(df, source, cost_col, qty_col, group):
    """Fill missing cost with quantity x median unit price of the same resource/unit/currency (same month first)."""
    miss = df[cost_col].isna()
    if not miss.any():
        return df
    ok = df[~miss & (df[qty_col] > 0) & (df[cost_col] > 0)].copy()
    ok["_p"] = ok[cost_col] / ok[qty_col]
    p_month = ok.groupby(group + ["month"])["_p"].median()
    p_all = ok.groupby(group)["_p"].median()
    df["cost_imputed"] = False
    for i in df.index[miss]:
        r = df.loc[i]
        key = tuple(r[g] for g in group)
        p = p_month.get(key + (r["month"],), np.nan)
        if pd.isna(p):
            p = p_all.get(key if len(key) > 1 else key[0], np.nan)
        df.at[i, cost_col] = r[qty_col] * p
        df.at[i, "cost_imputed"] = True
    note("missing cost", source, miss.sum(),
         "imputed = quantity x median unit price (same resource/unit/currency, same month; else whole period)",
         chf=None, detail="flag column cost_imputed=True")
    return df

def to_chf(df, fx, amt_col, cur_col):
    m = df["month"].map(fx.set_index("month")["eur_chf"]), df["month"].map(fx.set_index("month")["usd_chf"])
    cur = df[cur_col].astype(str).str.upper()
    rate = np.where(cur == "EUR", m[0], np.where(cur == "USD", m[1], 1.0))
    return df[amt_col] * rate

# ----------------------------------------------------------------- sources
def load_azure(data, mapping, fx):
    d = dedupe(read(data, "azure_costs.csv"), "azure")
    d["date"] = pd.to_datetime(d["Date"], format="%Y-%m-%d")
    d["month"] = d["date"].dt.strftime("%Y-%m")
    d["resource_id"] = d["ResourceId"].str.split("/").str[-1]
    tags = d["Tags"].fillna("{}").apply(lambda s: json.loads(s) if s.strip().startswith("{") else {})
    d["dept_tag"] = tags.apply(lambda t: t.get("department"))
    d["tool_tag"] = tags.apply(lambda t: t.get("tool"))
    d["project_id"] = tags.apply(lambda t: t.get("project")).map(norm_project)
    d["env_tag"] = tags.apply(lambda t: t.get("environment"))
    note("empty tags", "azure", (tags.apply(len) == 0).sum(), "department/tool/environment filled from mapping by resource_id")
    scan_text(d, "azure", ["Notes"], "ResourceId")
    cred = d["ChargeType"] == "Credit"
    note("credits", "azure", cred.sum(), "kept as negative cost (real money back); excluded from energy (quantity 0)",
         chf=d.loc[cred, "CostInBillingCurrency"].sum())
    d = impute_cost(d, "azure", "CostInBillingCurrency", "Quantity", ["resource_id", "UnitOfMeasure", "BillingCurrency"])
    d["cost_chf"] = to_chf(d, fx, "CostInBillingCurrency", "BillingCurrency")
    return pd.DataFrame(dict(
        source="azure", date=d["date"], month=d["month"], resource_id=d["resource_id"],
        service=d["ServiceName"], region=d["ResourceLocation"], unit=d["UnitOfMeasure"],
        quantity=d["Quantity"], cost_orig=d["CostInBillingCurrency"], currency=d["BillingCurrency"],
        cost_chf=d["cost_chf"], cost_imputed=d.get("cost_imputed", False), charge_type=d["ChargeType"],
        dept_src=d["dept_tag"], tool_src=d["tool_tag"], env_src=d["env_tag"], project_id=d["project_id"],
        cpu_avg_pct=d["AvgCpuPercent"]))

def load_aws(data, mapping, fx):
    d = dedupe(read(data, "aws_costs.csv"), "aws")
    d["date"] = pd.to_datetime(d["line_item_usage_start_date"]).dt.normalize()
    d["month"] = d["date"].dt.strftime("%Y-%m")
    d["resource_id"] = d["line_item_resource_id"].str.split(":").str[-1]
    scan_text(d, "aws", ["line_item_description"], "line_item_resource_id")
    tn = d["line_item_description"].astype(str).str.contains("Test account", na=False)
    note("free-text says 'exclude test account'", "aws", tn.sum(),
         "NOT excluded on the basis of free text: these are real paid sandbox costs (cost centre 9100); allocated to IT",
         chf=d.loc[tn, "line_item_unblended_cost"].sum())
    d = impute_cost(d, "aws", "line_item_unblended_cost", "line_item_usage_amount",
                    ["resource_id", "pricing_unit", "line_item_currency_code"])
    d["cost_chf"] = to_chf(d, fx, "line_item_unblended_cost", "line_item_currency_code")
    return pd.DataFrame(dict(
        source="aws", date=d["date"], month=d["month"], resource_id=d["resource_id"],
        service=d["product_servicecode"], region=d["product_region"], unit=d["pricing_unit"],
        quantity=d["line_item_usage_amount"], cost_orig=d["line_item_unblended_cost"],
        currency=d["line_item_currency_code"], cost_chf=d["cost_chf"], cost_imputed=d.get("cost_imputed", False),
        charge_type=d["line_item_line_item_type"], dept_src=d["resource_tags_user_department"],
        tool_src=d["resource_tags_user_tool"], env_src=d["resource_tags_user_environment"],
        project_id=d["resource_tags_user_project"].map(norm_project), cpu_avg_pct=d["avg_cpu_utilization"]))

def load_hoster(data, mapping, fx):
    d = dedupe(read(data, "hoster_invoice.csv"), "hoster")
    d["date"] = pd.to_datetime(d["Date"], format="%d.%m.%Y")
    d["month"] = d["date"].dt.strftime("%Y-%m")
    d["resource_id"] = d["Item"].map(HOSTER_ITEM_RID)
    scan_text(d, "hoster", ["Remark"], "Date")
    note("no resource key", "hoster", len(d), "resource_id derived from Item label via fixed map", detail=str(HOSTER_ITEM_RID))
    note("missing cost centre", "hoster", d["CostCenter"].isna().sum(), "filled from mapping by resource_id")
    d["cur"] = "CHF"
    d = impute_cost(d, "hoster", "Amount_CHF", "Quantity", ["resource_id", "Unit"])
    return pd.DataFrame(dict(
        source="hoster", date=d["date"], month=d["month"], resource_id=d["resource_id"], service=d["Service"],
        region="Switzerland (Zurich)", unit=d["Unit"], quantity=d["Quantity"], cost_orig=d["Amount_CHF"],
        currency="CHF", cost_chf=d["Amount_CHF"], cost_imputed=d.get("cost_imputed", False), charge_type="Usage",
        dept_src=d["CostCenter"].map(CC_DEPT), tool_src=d["Item"], env_src=np.nan,
        project_id=d["ProjectNumber"].map(norm_project), cpu_avg_pct=np.nan))

def load_ai_usage(data, mapping, fx):
    d = dedupe(read(data, "ai_usage.csv"), "ai_usage")
    d["date"] = pd.to_datetime(d["date"])
    d["month"] = d["date"].dt.strftime("%Y-%m")
    miss = d["tokens_out"].isna()
    ratio = (d.loc[~miss, "tokens_out"] / d.loc[~miss, "tokens_in"]).groupby([d["tool"], d["model"]]).median()
    est = d.apply(lambda r: r["tokens_in"] * ratio.get((r["tool"], r["model"]), np.nan), axis=1)
    d["tokens_out_filled"] = d["tokens_out"].fillna(est)
    note("missing tokens_out", "ai_usage", miss.sum(),
         "cost kept as given; tokens_out estimated from median out/in ratio of same tool+model (energy only)")
    return pd.DataFrame(dict(
        source="ai_usage", date=d["date"], month=d["month"], resource_id=d["resource_id"], service=d["task_type"],
        region="EU (mixed)", unit="tokens", quantity=d["tokens_in"] + d["tokens_out_filled"],
        cost_orig=d["cost_chf"], currency="CHF", cost_chf=d["cost_chf"], cost_imputed=False, charge_type="Usage",
        dept_src=d["department"], tool_src=d["tool"], env_src="prod", project_id=d["project_id"].map(norm_project),
        cpu_avg_pct=np.nan, provider=d["provider"], model=d["model"], requests=d["requests"],
        tokens_in=d["tokens_in"], tokens_in_cache=d["tokens_in_cache"], tokens_out=d["tokens_out_filled"]))

def load_contracts(data, fx, name, source, item_col, price_col, rid_fn, unit):
    d = dedupe(read(data, name), source)
    drafts = d["contract_status"] == "Draft"
    note("draft rows", source, drafts.sum(), "dropped; every draft has a Final row for the same month/item/cost centre")
    d = d[~drafts].copy()
    d["date"] = pd.to_datetime(d["month"])
    d["month"] = d["date"].dt.strftime("%Y-%m")
    d["cost_chf"] = to_chf(d, fx, "amount", "currency")
    out = pd.DataFrame(dict(
        source=source, date=d["date"], month=d["month"], resource_id=d[item_col].map(rid_fn), service=d[item_col],
        region="EU (mixed)", unit=unit, quantity=d["licences_purchased"], cost_orig=d["amount"],
        currency=d["currency"], cost_chf=d["cost_chf"], cost_imputed=False, charge_type="Usage",
        dept_src=d["cost_center"].map(CC_DEPT), tool_src=d[item_col], env_src="prod", project_id=np.nan,
        cpu_avg_pct=np.nan, seats_active=d["licences_active_30d"], price_per_seat=d[price_col],
        contract_end=d["contract_end"], notice_period_days=d["notice_period_days"], billing=d["billing"]))
    if "messages_30d" in d:
        out["messages"] = d["messages_30d"]
    return out

# ----------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, type=Path)
    ap.add_argument("--out", default=Path("out"), type=Path)
    ap.add_argument("--factors", default=Path(__file__).resolve().parent.parent / "factors" / "factors.csv", type=Path)
    a = ap.parse_args()
    data, out = a.data, a.out
    out.mkdir(parents=True, exist_ok=True)

    fx = read(data, "exchange_rates.csv")
    fx["month"] = pd.to_datetime(fx["month"]).dt.strftime("%Y-%m")
    mapping = read(data, "mapping_departments_tools.csv").set_index("resource_id")

    sub_rid = {"Microsoft Copilot": "sub-copilot", "Claude Team": "sub-claude", "ChatGPT Team": "sub-chatgpt"}
    parts = [
        load_azure(data, mapping, fx), load_aws(data, mapping, fx), load_hoster(data, mapping, fx),
        load_ai_usage(data, mapping, fx),
        load_contracts(data, fx, "ai_subscriptions.csv", "ai_subscriptions", "product", "price_per_seat",
                       lambda p: sub_rid.get(p, "sub-other"), "seat-month"),
        load_contracts(data, fx, "saas_contracts.csv", "saas", "contract", "price_per_licence",
                       lambda c: "saas-m365" if c == "Microsoft 365" else "saas-other", "licence-month"),
    ]
    f = pd.concat(parts, ignore_index=True, sort=False)

    # master data: department, tool, environment, criticality, owner role
    m = mapping.reindex(f["resource_id"])
    f["department"] = f["dept_src"].where(f["dept_src"].notna(), m["department"].values)
    f["tool"] = f["tool_src"].where(f["tool_src"].notna(), m["tool"].values)
    f["environment"] = f["env_src"].where(f["env_src"].notna(), m["environment"].values)
    f["criticality"] = m["criticality"].values
    f["responsible_role"] = m["responsible_role"].values
    f.loc[f["department"].isna() & (f["resource_id"] == "sandbox"), "department"] = "Test account"
    f["cost_center"] = f["department"].map(DEPT_CC)
    f["country"] = f["region"].map(country_of)
    f["energy_key"] = f["unit"].map(UNIT_KEY)
    f.loc[f["unit"].eq("month"), "energy_key"] = "none"
    f["in_baseline"] = (f["date"] >= BASE_START) & (f["date"] < BASE_END)
    un = f["department"].isna().sum()
    if un:
        note("no department after mapping", "all", un, "left as 'Unallocated'; check mapping")
        f["department"] = f["department"].fillna("Unallocated")
    note("project id spellings", "all", f["project_id"].notna().sum(), "normalised to P-### (P001, p-001 -> P-001)")
    f = f.drop(columns=["dept_src", "tool_src", "env_src"])
    for src, g in f[f["cost_imputed"].astype(bool) & f["in_baseline"]].groupby("source"):
        note("imputed cost in baseline year", src, len(g), "sum of imputed values (CHF)", chf=g["cost_chf"].sum())
    tk = read(data, "it_tickets.csv")
    scan_text(tk, "it_tickets", ["title", "description"], "ticket_id")

    # ---------------------------------------------------- allocation of shared costs
    hc = read(data, "extra/headcount.csv") if (data / "extra/headcount.csv").exists() else None
    alloc_rows = []
    if hc is not None:
        hc["month"] = pd.to_datetime(hc["month"]).dt.strftime("%Y-%m")
        share = hc.pivot_table(index="month", columns="department", values="fte", aggfunc="sum")
        share = share.div(share.sum(axis=1), axis=0)
    for dept_label, rule in [("Overhead", "FTE share of the month (headcount.csv)"),
                             ("Test account", "100% IT (sandboxes are developer environments)")]:
        sel = f["department"] == dept_label
        note("shared costs", "all", sel.sum(), f"{dept_label} allocated by {rule}",
             chf=f.loc[sel & f["in_baseline"], "cost_chf"].sum(), detail="baseline-year CHF shown")
    fa = f.copy()
    fa["dept_allocated"] = fa["department"]
    fa["alloc_share"] = 1.0
    over = fa[fa["department"] == "Overhead"]
    rest = fa[fa["department"] != "Overhead"].copy()
    rest.loc[rest["department"] == "Test account", "dept_allocated"] = "IT"
    pieces = [rest]
    if hc is not None and len(over):
        for dept in DEPARTMENTS:
            p = over.copy()
            p["dept_allocated"] = dept
            p["alloc_share"] = p["month"].map(share[dept]).fillna(1 / len(DEPARTMENTS))
            pieces.append(p)
    fa = pd.concat(pieces, ignore_index=True)
    for c in ["cost_chf", "quantity"]:
        fa[c + "_alloc"] = fa[c] * fa["alloc_share"]

    # ---------------------------------------------------- energy and CO2 (only if factors filled)
    fac = pd.read_csv(a.factors) if a.factors.exists() else pd.DataFrame()
    have = fac.dropna(subset=["value_mid"]) if len(fac) else fac
    missing_f = sorted(set(f.loc[f["in_baseline"], "energy_key"].dropna()) - {"none"} - set(have.get("key", [])))
    grid_keys = {f"grid_{c}" for c in f["country"].dropna().unique()}
    missing_g = sorted(grid_keys - set(have.get("key", [])))
    pue_row = have[have["key"] == "pue_default"] if len(have) else have
    if len(have):
        for lvl in ["low", "mid", "high"]:
            ef = have.set_index("key")[f"value_{lvl}"]
            pue = float(pue_row[f"value_{lvl}"].iloc[0]) if len(pue_row) else 1.0
            applies = have.set_index("key")["applies_pue"].astype(str).str.lower().eq("yes")
            qty = f["quantity"].where(f["energy_key"] != "tokens_1000", f["quantity"] / 1000)
            qty = qty.where(f["energy_key"] != "subscription_message", f.get("messages"))
            qty = qty.where(f["charge_type"] != "Credit", 0)
            e = qty * f["energy_key"].map(ef)
            e = e * np.where(f["energy_key"].map(applies).fillna(False), pue, 1.0)
            f[f"kwh_{lvl}"] = e
            f[f"co2_kg_{lvl}"] = e * ("grid_" + f["country"]).map(ef)
    if missing_f or missing_g:
        note("factors missing", "factors.csv", len(missing_f) + len(missing_g),
             "energy/CO2 not computed for these keys yet", detail=", ".join(missing_f + missing_g))

    # ---------------------------------------------------- contradiction checks
    checks = []
    base = f[f["in_baseline"]]
    pr = data / "extra/provider_monthly_report.csv"
    if pr.exists():
        rep = read(data, "extra/provider_monthly_report.csv")
        rep["month"] = pd.to_datetime(rep["month"]).dt.strftime("%Y-%m")
        ours = f.groupby(["month", "source"])["cost_chf"].sum().unstack()
        for combo in [["azure"], ["aws"], ["azure", "aws"], ["azure", "aws", "hoster"]]:
            diff = (rep.set_index("month")["total_cost_chf"] - ours[combo].sum(axis=1)).dropna()
            checks.append(dict(check="provider_monthly_report vs " + "+".join(combo),
                               mean_abs_diff_chf=round(diff.abs().mean(), 0),
                               mean_diff_pct=round((diff / rep.set_index("month")["total_cost_chf"]).mean() * 100, 1)))
    inv = data / "extra/ai_invoice_monthly.csv"
    if inv.exists():
        iv = read(data, "extra/ai_invoice_monthly.csv")
        iv["month"] = pd.to_datetime(iv["month"]).dt.strftime("%Y-%m")
        iv["cost_chf"] = to_chf(iv, fx, "amount", "currency")
        g = f[f["source"] == "ai_usage"].groupby(["month", "provider"])["cost_chf"].sum()
        i2 = iv.groupby(["month", "provider"])["cost_chf"].sum()
        both = pd.concat([g.rename("gateway"), i2.rename("invoice")], axis=1).dropna()
        b2 = both[both.index.get_level_values(0) >= BASE_START[:7]]
        b2 = b2[b2.index.get_level_values(0) < BASE_END[:7]]
        for prov, grp in b2.groupby(level=1):
            checks.append(dict(check=f"AI gateway vs invoice ({prov}), baseline year",
                               mean_abs_diff_chf=round((grp.gateway - grp.invoice).abs().mean(), 0),
                               mean_diff_pct=round(((grp.invoice - grp.gateway) / grp.invoice).mean() * 100, 1)))
    dpu = read(data, "data_platform_usage.csv")
    dpu["month"] = pd.to_datetime(dpu["date"]).dt.strftime("%Y-%m")
    nh = (dpu["node_count"] * dpu["runtime_h"]).groupby([dpu["month"], dpu["resource_id"]]).sum()
    az_nh = f[(f["unit"] == "node-hour") & (f["charge_type"] == "Usage")].groupby(["month", "resource_id"])["quantity"].sum()
    j = pd.concat([nh.rename("monitoring"), az_nh.rename("invoice")], axis=1).dropna()
    for rid, grp in j.groupby(level=1):
        checks.append(dict(check=f"node-hours: monitoring vs Azure invoice ({rid})",
                           mean_abs_diff_chf=None,
                           mean_diff_pct=round(((grp.invoice - grp.monitoring) / grp.monitoring).mean() * 100, 1)))
    cop = f[(f["source"] == "ai_subscriptions") & (f["tool"] == "Microsoft Copilot") & (f["month"] >= "2026-07")]
    if len(cop):
        note("price vs README", "ai_subscriptions", len(cop),
             "flag for a human: README states a Copilot promotion (USD 18) from 01.07.2026; data bill "
             f"USD {sorted(cop['price_per_seat'].unique())}", detail="not corrected")
    pd.DataFrame(checks).to_csv(out / "contradiction_checks.csv", index=False)
    print(pd.DataFrame(checks).to_string(index=False))

    # ---------------------------------------------------- outputs
    f.to_csv(out / "fact_costs.csv", index=False)
    fa.to_csv(out / "fact_costs_allocated.csv", index=False)
    b = f[f["in_baseline"]]
    ba = fa[fa["in_baseline"]]
    total = b["cost_chf"].sum()
    with pd.ExcelWriter(out / "baseline_summary.xlsx") as xw:
        b.groupby("source")["cost_chf"].sum().sort_values(ascending=False).to_frame().to_excel(xw, "by_source")
        ba.groupby("dept_allocated")["cost_chf_alloc"].sum().sort_values(ascending=False).to_frame().to_excel(xw, "by_department_allocated")
        b.groupby(["source", "tool"])["cost_chf"].sum().sort_values(ascending=False).to_frame().to_excel(xw, "by_tool")
        b.groupby(["country", "energy_key", "unit"]).agg(quantity=("quantity", "sum"), cost_chf=("cost_chf", "sum")).to_excel(xw, "by_country_unit")
        b.groupby("month")["cost_chf"].sum().to_frame().to_excel(xw, "by_month")
        if "kwh_mid" in b:
            b.groupby(["country", "source"])[["kwh_mid", "co2_kg_mid"]].sum().to_excel(xw, "energy_co2")
    pd.DataFrame(log).to_csv(out / "quality_log.csv", index=False)

    # template prefill
    tpl = read(data, "template_baseline_and_assumptions.csv").astype(object)
    idx = tpl["parameter"] == "total_cost_baseline_year_chf"
    tpl.loc[idx, "value_mid"] = round(total, 0)
    tpl.loc[idx, "source"] = "Sample data ALTYCA, sprintd Basel 2026: azure, aws, hoster, ai_usage, ai_subscriptions, saas"
    tpl.loc[idx, "calculation_or_assumption"] = (
        "Sum of all cost rows Sep 2025-Aug 2026 after removing exact duplicates and Draft rows; "
        "missing costs imputed from median unit price; EUR/USD converted with monthly ECB-based rates in exchange_rates.csv; "
        "Azure SLA credits kept as negative cost; bonus invoices (ai_invoice_monthly, provider report) used only as cross-checks to avoid double counting.")
    ar = tpl["parameter"] == "allocation_rule_shared_costs"
    tpl.loc[ar, "value_mid"] = ("1) Department named in the row (cloud tags; consuming department in the AI gateway); "
                                "2) else cost centre of the row (licences, hoster); 3) else mapping_departments_tools.csv by resource_id; "
                                "4) anything still on Overhead (9000) by monthly FTE share from headcount.csv; "
                                "test account (9100, sandboxes) 100% to IT.")
    if "kwh_mid" in b and b["kwh_mid"].notna().any():
        for p, col in [("total_energy_baseline_year_kwh", "kwh"), ("total_co2_location_based_baseline_year_kg", "co2_kg")]:
            k = tpl["parameter"] == p
            for lvl in ["low", "mid", "high"]:
                tpl.loc[k, f"value_{lvl}"] = round(b[f"{col}_{lvl}"].sum(), 0)
            tpl.loc[k, "calculation_or_assumption"] = "Quantity per row x energy factor (x PUE where applicable) x grid factor of the row's country; see factors.csv"
    tpl.to_csv(out / "template_baseline_and_assumptions_prefilled.csv", index=False, encoding="utf-8-sig")

    print(f"Baseline year {BASE_START}..{BASE_END[:7]} (excl.): total cost CHF {total:,.0f}")
    print(b.groupby("source")["cost_chf"].sum().round(0).to_string())
    if missing_f or missing_g:
        print("\nFactors still missing in factors.csv:", ", ".join(missing_f + missing_g))
    print(f"\nWrote {out}/: fact_costs.csv, fact_costs_allocated.csv, baseline_summary.xlsx, "
          "quality_log.csv, contradiction_checks.csv, template_baseline_and_assumptions_prefilled.csv")
    return f, fa, total

if __name__ == "__main__":
    main()
