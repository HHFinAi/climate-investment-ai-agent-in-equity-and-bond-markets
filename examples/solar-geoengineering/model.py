"""Solar geoengineering cost *sensitivity* arithmetic, not deployment advice.

Hypothetical engineering coefficients are kept separate from independently
unverified regional climate response and governance. No proprietary inputs.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
LABEL = "ILLUSTRATIVE_ENGINEERING_COST_SENSITIVITY_NOT_CLIMATE_PROJECTION"


def number(value, field, positive=False):
    if type(value) not in (float, int) or not math.isfinite(value):
        raise ValueError(f"{field}: finite numeric input required")
    if value < 0 or (positive and value <= 0):
        raise ValueError(f"{field}: positive or nonnegative input required")
    return float(value)


def load():
    return json.loads((HERE / "inputs.json").read_text(encoding="utf-8"))


def validate(p):
    if p.get("classification") != LABEL:
        raise ValueError("Illustrative classification required")
    if p.get("governance") != "RESEARCH_ONLY_NO_DEPLOYMENT_AUTHORIZATION":
        raise ValueError("No authorization or deployment evidence is provided")
    if p.get("model_horizon") != "one hypothetical recurring deployment year":
        raise ValueError("Annual deployment horizon must be explicit")
    number(p.get("target_global_cooling_c"), "target", positive=True)
    s = p.get("sai")
    m = p.get("mcb")
    a = p.get("sensitivity")
    if not isinstance(s, dict) or not isinstance(m, dict) or not isinstance(a, dict):
        raise ValueError("SAI, MCB and sensitivity sections required")
    if set(s) != {"required_forcing_w_m2_per_c", "sulfate_effectiveness_w_m2_per_tg_sulfur_per_year",
                  "so2_mass_per_sulfur_mass", "all_in_delivery_usd_per_t_so2"}:
        raise ValueError("SAI units/schema mismatch")
    if set(m) != {"dry_sea_salt_tg_per_year_per_c", "atomization_and_lofting_gwh_per_tg",
                  "marine_generation_all_in_lcoe_usd_per_mwh", "non_energy_annual_cost_usd_bn_per_c"}:
        raise ValueError("MCB units/schema mismatch")
    for k, v in s.items():
        number(v, "sai." + k, positive=True)
    for k, v in m.items():
        number(v, "mcb." + k, positive=k != "non_energy_annual_cost_usd_bn_per_c")
    if not 1.8 <= s["so2_mass_per_sulfur_mass"] <= 2.2:
        raise ValueError("Explicit sulfur/SO2 conversion must remain physically defensible")
    keys = {
        "sai_effectiveness_w_m2_per_tg_sulfur_per_year",
        "sai_delivery_usd_per_t_so2",
        "mcb_salt_tg_per_year_per_c",
        "mcb_power_gwh_per_tg",
    }
    if set(a) != keys:
        raise ValueError("Unexpected sensitivity axes")
    for k, seq in a.items():
        if not isinstance(seq, list) or not seq:
            raise ValueError("Missing sensitivity values")
        for val in seq:
            number(val, k, positive=True)
    if not isinstance(p.get("disclaimers"), list) or len(p["disclaimers"]) < 4:
        raise ValueError("Explicit economic and scientific exclusions required")


def sai(p, *, sulfate_effectiveness=None, unit_cost=None):
    s = p["sai"]
    target = p["target_global_cooling_c"]
    effective = (s["sulfate_effectiveness_w_m2_per_tg_sulfur_per_year"]
                 if sulfate_effectiveness is None else number(sulfate_effectiveness, "sai.efficacy", positive=True))
    price = (s["all_in_delivery_usd_per_t_so2"] if unit_cost is None else
             number(unit_cost, "sai.delivered_cost", positive=True))
    forcing = target * s["required_forcing_w_m2_per_c"]
    tg_s = forcing / effective
    tg_so2 = tg_s * s["so2_mass_per_sulfur_mass"]
    # 1 Tg == 1,000,000 metric tonnes; USD bn = 1,000,000,000 USD.
    annual_cost_bn = tg_so2 * price / 1000
    return {
        "target_global_cooling_c": target,
        "assumed_negative_forcing_magnitude_w_m2": forcing,
        "required_sulfur_tg_per_year": tg_s,
        "required_so2_tg_per_year": tg_so2,
        "annual_direct_deployment_cost_usd_bn": annual_cost_bn,
        "scope": "HYPOTHETICAL_DIRECT_COST_FLOOR_ONLY",
    }


def mcb(p, *, salt_tg_per_c=None, electricity_gwh_per_tg=None):
    m = p["mcb"]
    target = p["target_global_cooling_c"]
    salt_per_c = (m["dry_sea_salt_tg_per_year_per_c"] if salt_tg_per_c is None else
                  number(salt_tg_per_c, "mcb.salt_per_degree", positive=True))
    energy_per_tg = (m["atomization_and_lofting_gwh_per_tg"] if electricity_gwh_per_tg is None else
                     number(electricity_gwh_per_tg, "mcb.energy_per_tg", positive=True))
    salt = target * salt_per_c
    energy_gwh = salt * energy_per_tg
    # 1 GWh == 1,000 MWh; cost in USD bn.
    power_bn = energy_gwh * m["marine_generation_all_in_lcoe_usd_per_mwh"] / 1_000_000
    other_bn = target * m["non_energy_annual_cost_usd_bn_per_c"]
    return {
        "target_global_cooling_c": target,
        "required_dry_sea_salt_tg_per_year": salt,
        "spraying_energy_gwh_per_year": energy_gwh,
        "spraying_energy_twh_per_year": energy_gwh / 1000,
        "annual_all_in_power_cost_usd_bn": power_bn,
        "annual_non_energy_cost_usd_bn": other_bn,
        "annual_direct_deployment_cost_usd_bn": power_bn + other_bn,
        "scope": "HYPOTHETICAL_DIRECT_COST_FLOOR_ONLY",
    }


def build(p):
    validate(p)
    sa = [dict(sai(p, sulfate_effectiveness=e, unit_cost=c),
               efficacy_w_m2_per_tg_s=e, delivered_cost_usd_per_t_so2=c)
          for e in p["sensitivity"]["sai_effectiveness_w_m2_per_tg_sulfur_per_year"]
          for c in p["sensitivity"]["sai_delivery_usd_per_t_so2"]]
    ma = [dict(mcb(p, salt_tg_per_c=sl, electricity_gwh_per_tg=el),
               dry_salt_tg_per_c=sl, energy_gwh_per_tg=el)
          for sl in p["sensitivity"]["mcb_salt_tg_per_year_per_c"]
          for el in p["sensitivity"]["mcb_power_gwh_per_tg"]]
    return {
        "case_id": p["case_id"], "as_of": p["as_of"],
        "classification": LABEL,
        "governance_status": p["governance"],
        "financial_research_decision": "NEEDS_DATA",
        "investable_revenue_by_company_usd_bn": None,
        "atmospheric_co2_removed_tonnes": 0,
        "operational_emissions_tonnes": None,
        "carbon_removal_cost_usd_per_tonne": None,
        "base_sai": sai(p),
        "base_mcb": mcb(p),
        "sai_sensitivities": sa,
        "mcb_sensitivities": ma,
        "disclaimers": p["disclaimers"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true", help="save deterministic results.json")
    args = parser.parse_args()
    result = build(load())
    if args.check:
        assert result["financial_research_decision"] == "NEEDS_DATA"
        assert result["carbon_removal_cost_usd_per_tonne"] is None
        assert len(result["sai_sensitivities"]) == 9
        assert len(result["mcb_sensitivities"]) == 9
        print("CHECK_OK: SAI sulfur units, MCB GWh/TWh, 18 sensitivities, no carbon credit")
    if args.write:
        (HERE / "results.json").write_text(
            json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8")
    elif not args.check:
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
