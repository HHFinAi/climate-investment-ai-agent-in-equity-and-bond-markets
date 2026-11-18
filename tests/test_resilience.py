import copy
import json
import unittest
from pathlib import Path
from resilience.engine import analyze, DataError, check_treatment_unique, run_cases

ROOT = Path(__file__).resolve().parents[1]
class TestResilience(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads((ROOT/"resilience/benchmarks.v1.json").read_text())
    def test_three_illustrative_blocked_cases(self):
        rows = run_cases(self.doc)["results"]
        self.assertEqual(len(rows), 3)
        self.assertTrue(all(x["research_status"]=="NEEDS_DATA" for x in rows))
        self.assertTrue(all(x["valuation_status"]=="NOT_SECURITY_VALUATION" for x in rows))
    def test_seven_categories(self):
        t=json.loads((ROOT/"resilience/taxonomy.v1.json").read_text())
        self.assertEqual(len(set(x["id"] for x in t["categories"])),7)
    def test_duplicate_risk_channels_rejected(self):
        with self.assertRaises(DataError):
            check_treatment_unique([{"risk_id":"heat","channel":"cashflow"},{"risk_id":"heat","channel":"discount_rate"}])
    def test_unverified_missing_field_blocks(self):
        x=copy.deepcopy(self.doc["cases"][0])
        del x["evidence_gates"]["funding_approved"]
        with self.assertRaises(DataError): analyze(x)
    def test_no_invented_financial(self):
        x=copy.deepcopy(self.doc["cases"][0])
        del x["assumptions"]["contribution_margin"]
        with self.assertRaises(DataError): analyze(x)
    def test_out_of_range_conversion(self):
        x=copy.deepcopy(self.doc["cases"][0])
        x["assumptions"]["revenue_realization"]=1.5
        with self.assertRaises(DataError): analyze(x)
    def test_operator_loss_proxy(self):
        x=copy.deepcopy(self.doc["cases"][0])
        x["role"]="operator"
        x["assumptions"]=dict(horizon_years=1,discount_rate=0,cash_tax_rate=0,upfront_capex_m=0,
           event_frequency_per_year=.2,loss_per_event_m=10,loss_reduction_fraction=.5,
           annual_insurance_savings_m=0,annual_operating_cost_m=0,annual_recurring_capex_m=0)
        self.assertEqual(analyze(x)["illustrative_project_npv_m"],1.0)
    def test_insurer_can_lose(self):
        x=copy.deepcopy(self.doc["cases"][0])
        x["role"]="insurer"
        x["category"]="insurance_financing"
        x["assumptions"]=dict(horizon_years=1,discount_rate=0,cash_tax_rate=0,upfront_capex_m=0,
            premium_income_m=4,expected_claims_m=5,annual_operating_cost_m=1,
            reinsurance_cost_m=1,capital_charge_m=1)
        self.assertEqual(analyze(x)["illustrative_project_npv_m"],-4)
    def test_enso_remains_pending(self):
        x=json.loads((ROOT/"resilience/enso-freeze-2026-11-18.json").read_text())
        self.assertTrue(all(p["outcome"]=="PENDING" for p in x["hypotheses"]))
        self.assertIsNone(x["security_return_prediction"])

if __name__=="__main__":
    unittest.main()
