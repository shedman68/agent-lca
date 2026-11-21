"""Rebuild the submission measures table from measures/measures.csv.

The column order and header text are the official template. The file is written
with a UTF-8 BOM, matching data/template_measures_package.csv. Market-based CO2
stays blank: measures/measures.csv has no market-based kilogram.

Also fills empty cells in submission/template_baseline_and_assumptions.csv.
Numbers in that fill come from out/fact_costs.csv and factors/factors.csv.
A cell with no such number is written as n/a, with the reason in
calculation_or_assumption. The header and the BOM are kept.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEASURES = ROOT / "measures" / "measures.csv"
MEASURES_TEMPLATE = ROOT / "submission" / "template_measures_package.csv"
BASELINE_TEMPLATE = ROOT / "submission" / "template_baseline_and_assumptions.csv"
FACT_COSTS = ROOT / "out" / "fact_costs.csv"
FACTORS = ROOT / "factors" / "factors.csv"

MEASURE_COLUMNS = [
    "measure_id",
    "description",
    "resource_or_source",
    "change",
    "effort_person_days",
    "savings_cost_chf_per_year",
    "savings_energy_kwh_per_year",
    "savings_co2_kg_location_based",
    "savings_co2_kg_market_based",
    "risks_and_exceptions",
    "assumptions_and_sources",
]

MARKET_NOTE = (
    " Market-based CO2 stays blank: measures/measures.csv has no market-based kilogram, "
    "and the pipeline baseline is location-based."
)

NA = "n/a"


def _read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    text = path.read_text(encoding="utf-8-sig")
    reader = csv.DictReader(text.splitlines())
    if reader.fieldnames is None:
        raise SystemExit(f"{path} has no header")
    return list(reader.fieldnames), list(reader)


def _write_rows(path: Path, header: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=header, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def build_measures() -> list[str]:
    header, _ = _read_rows(MEASURES_TEMPLATE)
    if header != MEASURE_COLUMNS:
        raise SystemExit("measures template header does not match the official column order")
    _, source_rows = _read_rows(MEASURES)
    required = [name for name in MEASURE_COLUMNS if name != "savings_co2_kg_market_based"]
    if source_rows:
        missing = [name for name in required if name not in source_rows[0]]
        if missing:
            raise SystemExit(f"measures/measures.csv is missing columns: {missing}")
    out_rows = []
    ids = []
    for row in source_rows:
        assumptions = (row.get("assumptions_and_sources") or "").rstrip()
        if "Market-based CO2 stays blank" not in assumptions:
            assumptions = f"{assumptions}{MARKET_NOTE}"
        item = {name: row.get(name, "") for name in MEASURE_COLUMNS}
        item["savings_co2_kg_market_based"] = ""
        item["assumptions_and_sources"] = assumptions
        out_rows.append(item)
        ids.append(item["measure_id"])
    _write_rows(MEASURES_TEMPLATE, header, out_rows)
    if not MEASURES_TEMPLATE.read_bytes().startswith(b"\xef\xbb\xbf"):
        raise SystemExit("measures template was written without the UTF-8 BOM")
    return ids


def _baseline_cost() -> float:
    if not FACT_COSTS.exists():
        raise SystemExit("out/fact_costs.csv is missing. Run pipeline/pipeline.py before this script.")
    total = 0.0
    with FACT_COSTS.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if str(row.get("in_baseline", "")).strip() != "True":
                continue
            raw = str(row.get("cost_chf", "")).strip()
            if raw:
                total += float(raw)
    return total


def _baseline_kwh() -> dict[str, float]:
    if not FACT_COSTS.exists():
        raise SystemExit("out/fact_costs.csv is missing. Run pipeline/pipeline.py before this script.")
    totals = {"low": 0.0, "mid": 0.0, "high": 0.0}
    with FACT_COSTS.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if str(row.get("in_baseline", "")).strip() != "True":
                continue
            for level in totals:
                raw = str(row.get(f"kwh_{level}", "")).strip()
                if raw:
                    totals[level] += float(raw)
    return totals


def _market_factor() -> dict[str, float]:
    with FACTORS.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("key") == "grid_market_based":
                return {level: float(row[f"value_{level}"]) for level in ("low", "mid", "high")}
    raise SystemExit("factors/factors.csv has no grid_market_based row")


def _by_parameter(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["parameter"]: row for row in rows}


def fill_baseline() -> None:
    raw = BASELINE_TEMPLATE.read_bytes()
    if not raw.startswith(b"\xef\xbb\xbf"):
        raise SystemExit("baseline template is missing its UTF-8 BOM")
    header, rows = _read_rows(BASELINE_TEMPLATE)
    expected = [
        "parameter",
        "must_or_bonus",
        "value_low",
        "value_mid",
        "value_high",
        "unit",
        "source",
        "calculation_or_assumption",
    ]
    if header != expected:
        raise SystemExit("baseline template header changed")
    by_name = _by_parameter(rows)

    cost = by_name["total_cost_baseline_year_chf"]
    cost_total = f"{_baseline_cost():.2f}"
    cost["value_low"] = cost_total
    cost["value_mid"] = cost_total
    cost["value_high"] = cost_total
    old_cost_note = (
        " value_low and value_high are n/a: the baseline cost is one reconciled total in value_mid, "
        "not a low/mid/high range."
    )
    cost_text = cost["calculation_or_assumption"].replace(old_cost_note, "").rstrip()
    cost_note = (
        " Cost has no factor range, so low = mid = high: value_low, value_mid and value_high "
        f"are the same reconciled total from out/fact_costs.csv ({cost_total})."
    )
    if "low = mid = high" not in cost_text:
        cost_text += cost_note
    cost["calculation_or_assumption"] = cost_text

    kwh = _baseline_kwh()
    factor = _market_factor()
    market = by_name["total_co2_market_based_baseline_year_kg"]
    products = {level: kwh[level] * factor[level] for level in ("low", "mid", "high")}
    for level in products:
        market[f"value_{level}"] = f"{products[level]:.1f}"
    market["source"] = "out/fact_costs.csv (baseline rows, kwh_low/mid/high); factors/factors.csv key grid_market_based"
    shown = " / ".join(f"{kwh[level]:,.1f} x {factor[level]:.3f} = {products[level]:,.1f}" for level in ("low", "mid", "high"))
    market["calculation_or_assumption"] = (
        "Bonus, derived, not a pipeline total. Baseline kWh on in_baseline rows of out/fact_costs.csv "
        f"times grid_market_based from factors/factors.csv ({shown}). "
        "The factor row is already the energy-weighted mix (low = certificate claims accepted, "
        "mid = providers' assured market-based figures, high = residual mixes paired with high energy). "
        "Location-based CO2 stays the official number. Hoster guarantees of origin "
        "(T-1030, T-1181, T-1203, T-1227) count in the low case only after a human has seen the certificates. "
        "PR #45 describes this product and was still open, so the figures were calculated here from out/ and factors/factors.csv."
    )

    growth = by_name["growth_per_year"]
    for level in ("low", "mid", "high"):
        growth[f"value_{level}"] = NA
    growth["source"] = "docs/traps.md (T-1261)"
    growth["calculation_or_assumption"] = (
        "n/a in the value cells: out/ has no company-wide growth rate, and this note is not in the baseline. "
        "T-1261: dp-prod 20 → 24 nodes from 1 Oct 2026, up to +20 % for dp-prod only (24/20 − 1). "
        "Do not put 24 nodes in the baseline."
    )

    rule = by_name["allocation_rule_shared_costs"]
    rule["value_low"] = "n/a (text rule)"
    rule["value_mid"] = "n/a (text rule)"
    rule["value_high"] = "n/a (text rule)"
    rule["source"] = (
        "pipeline/pipeline.py (allocation of shared costs); "
        "data/mapping_departments_tools.csv; data/extra/headcount.csv"
    )
    rule["calculation_or_assumption"] = (
        "n/a (text rule) in value_low, value_mid and value_high. The rule, as pipeline/pipeline.py writes it: "
        "1) Department named in the row (cloud tags; consuming department in the AI gateway); "
        "2) else cost centre of the row (licences, hoster); "
        "3) else mapping_departments_tools.csv by resource_id; "
        "4) anything still on Overhead (9000) by monthly FTE share from headcount.csv; "
        "test account (9100, sandboxes) 100% to IT."
    )

    for row in rows:
        for column in header:
            if str(row.get(column, "")).strip() == "":
                raise SystemExit(f"blank cell left on {row.get('parameter')} / {column}")
    _write_rows(BASELINE_TEMPLATE, header, rows)
    if not BASELINE_TEMPLATE.read_bytes().startswith(b"\xef\xbb\xbf"):
        raise SystemExit("baseline template lost its UTF-8 BOM")


def main() -> None:
    ids = build_measures()
    fill_baseline()
    print("measures:", " ".join(ids))
    print("wrote", MEASURES_TEMPLATE.name, "and", BASELINE_TEMPLATE.name)


if __name__ == "__main__":
    main()
