"""Analyst-provided incremental adaptation cashflow arithmetic (no market feed)."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

class DataError(ValueError):
    pass

ROLES = {"supplier", "operator", "insurer"}
CATEGORIES = {"monitoring_early_warning", "cooling_hvac", "insurance_financing",
              "resilient_agriculture", "resilient_power", "resilient_urban",
              "water_infrastructure"}
GATES = ("asset_location_verified", "payer_identified", "funding_approved",
         "issuer_exposure_verified", "issuer_financials_verified",
         "current_security_price_verified", "human_review_completed")

def num(obj, key, *, minimum=0, maximum=None):
    val = obj.get(key)
    if isinstance(val, bool) or not isinstance(val, (float, int)) or not math.isfinite(val):
        raise DataError(f"{key} must be a supplied finite number")
    if val < minimum or (maximum is not None and val > maximum):
        raise DataError(f"{key} outside permitted range")
    return float(val)

def annual_cashflow(role, a):
    """Incremental FCF proxy in millions of declared currency, not issuer FCF."""
    tax_rate = num(a, "cash_tax_rate", maximum=1)
    if role == "supplier":
        rev = num(a, "potential_incremental_revenue_m") * num(a, "revenue_realization", maximum=1)
        ebitda = rev * num(a, "contribution_margin", maximum=1) - num(a, "annual_fixed_opex_m")
        ebit = ebitda - num(a, "annual_depreciation_m")
        return ebitda - max(0, ebit) * tax_rate - num(a, "annual_recurring_capex_m") - num(a, "annual_working_capital_add_m")
    if role == "operator":
        avoided = (num(a, "event_frequency_per_year") * num(a, "loss_per_event_m")
                   * num(a, "loss_reduction_fraction", maximum=1))
        pre_tax = avoided + num(a, "annual_insurance_savings_m") - num(a, "annual_operating_cost_m")
        return pre_tax - max(0, pre_tax) * tax_rate - num(a, "annual_recurring_capex_m")
    if role == "insurer":
        pre_tax = (num(a, "premium_income_m") - num(a, "expected_claims_m")
                   - num(a, "annual_operating_cost_m") - num(a, "reinsurance_cost_m")
                   - num(a, "capital_charge_m"))
        return pre_tax - max(0, pre_tax) * tax_rate
    raise DataError("unsupported role")

def check_treatment_unique(treatments):
    """Reject risk charged in incompatible financial channels."""
    if not isinstance(treatments, list):
        raise DataError("risk_treatments must be a list")
    seen = {}
    for item in treatments:
        rid, channel = item.get("risk_id"), item.get("channel")
        if not isinstance(rid, str) or not rid or channel not in {"cashflow", "discount_rate", "credit_recovery", "disclosure_only"}:
            raise DataError("invalid risk treatment")
        if rid in seen and seen[rid] != channel:
            raise DataError(f"risk {rid} counted in multiple valuation channels")
        seen[rid] = channel
    return seen

def analyze(case):
    if case.get("role") not in ROLES or case.get("category") not in CATEGORIES:
        raise DataError("unsupported role or adaptation category")
    if not isinstance(case.get("case_id"), str) or not case["case_id"]:
        raise DataError("case_id required")
    if case.get("currency") not in {"USD", "EUR", "GBP", "CHF"}:
        raise DataError("explicit supported currency required; no FX conversion")
    a = case.get("assumptions")
    if not isinstance(a, dict):
        raise DataError("assumptions object required")
    years = num(a, "horizon_years", minimum=1, maximum=40)
    if years != int(years):
        raise DataError("horizon_years must be integer")
    discount, upfront = num(a, "discount_rate", maximum=1), num(a, "upfront_capex_m")
    check_treatment_unique(case.get("risk_treatments", []))
    annual = annual_cashflow(case["role"], a)
    pv = sum(annual / (1 + discount) ** year for year in range(1, int(years) + 1))
    gates = case.get("evidence_gates", {})
    if not isinstance(gates, dict) or any(type(gates.get(k)) is not bool for k in GATES):
        raise DataError("all evidence_gates must be explicit booleans")
    missing = [k for k in GATES if not gates[k]]
    return {"case_id": case["case_id"], "role": case["role"], "category": case["category"],
            "currency": case["currency"], "unit": "millions",
            "annual_incremental_fcf_m": round(annual, 4),
            "illustrative_project_npv_m": round(pv - upfront, 4),
            "discount_rate_assumption": discount, "horizon_years": int(years),
            "research_status": "NEEDS_DATA" if missing else "READY_FOR_HUMAN_REVIEW",
            "evidence_gaps": missing, "valuation_status": "NOT_SECURITY_VALUATION",
            "warning": "Hypothetical project cash-flow proxy only; no verified company financials or market prices."}

def run_cases(document):
    cases = document.get("cases")
    if document.get("schema_version") != "1.0" or not isinstance(cases, list):
        raise DataError("schema_version=1.0 and cases[] required")
    ids = [case.get("case_id") for case in cases]
    if len(ids) != len(set(ids)):
        raise DataError("duplicate case_id")
    return {"schema_version": "1.0", "results": [analyze(case) for case in cases]}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path(__file__).with_name("benchmarks.v1.json"))
    parser.add_argument("--out", type=Path)
    opts = parser.parse_args()
    output = json.dumps(run_cases(json.loads(opts.input.read_text(encoding="utf-8"))), indent=2) + "\n"
    if opts.out:
        if opts.out.resolve() == opts.input.resolve() or opts.out.exists():
            parser.error("refusing to overwrite input or prior output")
        opts.out.parent.mkdir(parents=True, exist_ok=True)
        opts.out.write_text(output, encoding="utf-8")
    else:
        print(output, end="")

if __name__ == "__main__":
    main()
