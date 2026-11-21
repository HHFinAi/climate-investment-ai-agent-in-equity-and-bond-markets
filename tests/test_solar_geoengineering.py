"""Deterministic geoengineering cost assumptions; no scientific calibration claim."""
import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "examples" / "solar-geoengineering"
SPEC = importlib.util.spec_from_file_location("srmg_model", CASE / "model.py")
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class GeoengineeringCostMath(unittest.TestCase):
    def setUp(self):
        self.p = M.load()

    def test_sai_mass_units_and_cost(self):
        s = M.sai(self.p)
        self.assertAlmostEqual(s["assumed_negative_forcing_magnitude_w_m2"], .75)
        self.assertAlmostEqual(s["required_sulfur_tg_per_year"], 2.5)
        self.assertAlmostEqual(s["required_so2_tg_per_year"], 5.0)
        self.assertAlmostEqual(s["annual_direct_deployment_cost_usd_bn"], 27.5)

    def test_mcb_tg_gwh_twh_lcoe(self):
        x = M.mcb(self.p)
        self.assertAlmostEqual(x["required_dry_sea_salt_tg_per_year"], 30)
        self.assertAlmostEqual(x["spraying_energy_gwh_per_year"], 150000)
        self.assertAlmostEqual(x["spraying_energy_twh_per_year"], 150)
        self.assertAlmostEqual(x["annual_all_in_power_cost_usd_bn"], 24)
        self.assertAlmostEqual(x["annual_non_energy_cost_usd_bn"], 3)
        self.assertAlmostEqual(x["annual_direct_deployment_cost_usd_bn"], 27)

    def test_delivery_cost_and_efficacy_sensitivities(self):
        low = M.sai(self.p, sulfate_effectiveness=.5, unit_cost=4000)
        high = M.sai(self.p, sulfate_effectiveness=.15, unit_cost=7500)
        self.assertLess(low["annual_direct_deployment_cost_usd_bn"],
                        high["annual_direct_deployment_cost_usd_bn"])
        lo = M.mcb(self.p, salt_tg_per_c=30, electricity_gwh_per_tg=3000)
        hi = M.mcb(self.p, salt_tg_per_c=120, electricity_gwh_per_tg=7000)
        self.assertLess(lo["annual_direct_deployment_cost_usd_bn"],
                        hi["annual_direct_deployment_cost_usd_bn"])

    def test_no_removal_credit_no_company_revenue_no_authority(self):
        r = M.build(self.p)
        self.assertEqual(r["atmospheric_co2_removed_tonnes"], 0)
        self.assertIsNone(r["carbon_removal_cost_usd_per_tonne"])
        self.assertIsNone(r["investable_revenue_by_company_usd_bn"])
        self.assertIsNone(r["operational_emissions_tonnes"])
        self.assertEqual(r["financial_research_decision"], "NEEDS_DATA")
        self.assertEqual(len(r["sai_sensitivities"]), 9)
        self.assertEqual(len(r["mcb_sensitivities"]), 9)

    def test_invalid_number_or_governance_rejected(self):
        for key, value in (("target_global_cooling_c", 0),
                           ("target_global_cooling_c", True),
                           ("target_global_cooling_c", float("nan"))):
            p = copy.deepcopy(self.p)
            p[key] = value
            with self.assertRaises(ValueError):
                M.build(p)
        p = copy.deepcopy(self.p)
        p["sai"]["so2_mass_per_sulfur_mass"] = 1
        with self.assertRaises(ValueError):
            M.build(p)
        p = copy.deepcopy(self.p)
        p["governance"] = "FULL_DEPLOYMENT_AUTHORIZED"
        with self.assertRaises(ValueError):
            M.build(p)


if __name__ == "__main__":
    unittest.main()
