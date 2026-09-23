import copy, math, unittest
from climate_agent.calculations import *
from climate_agent.demo import numbers
from climate_agent.validation import load_json
from climate_agent.workflow import ROOT

class CalculationTests(unittest.TestCase):
    def setUp(self): self.x=load_json(ROOT/'examples/synthetic-financials.json')
    def test_finite_numbers(self):
        for bad in (None, True, '1', float('inf'), float('nan')):
            with self.subTest(bad=bad),self.assertRaises(DataError): number(bad,'x')
    def test_gross_scopes(self): self.assertEqual(total_emissions(10,20)['tco2e'],30)
    def test_scope3_explicit(self): self.assertEqual(total_emissions(10,20,scope3=50,include_scope3=True)['tco2e'],80)
    def test_missing_scope3_not_zero(self):
        with self.assertRaises(DataError):total_emissions(10,20,include_scope3=True)
    def test_negative_emissions_rejected(self):
        with self.assertRaises(DataError):total_emissions(-1,20)
    def test_intensity_units(self):self.assertEqual(carbon_intensity(1000000,2000),500)
    def test_zero_revenue_rejected(self):
        with self.assertRaises(DataError):carbon_intensity(100,0)
    def test_waci_known_hand_calculation(self):self.assertEqual(waci(self.x['corporate_sleeve'])['full_waci'],380)
    def test_waci_missing_keeps_denominator(self):
        h=self.x['corporate_sleeve'];h[1]['emissions_tco2e']=None;r=waci(h)
        self.assertIsNone(r['full_waci']);self.assertEqual(r['known_weighted_contribution'],300);self.assertEqual(r['covered_only_waci'],500);self.assertEqual(r['coverage_weight'],.6)
    def test_waci_all_missing(self):
        h=self.x['corporate_sleeve']
        for row in h:row['emissions_tco2e']=None
        self.assertIsNone(waci(h)['covered_only_waci'])
    def test_waci_no_silent_rescaling(self):
        self.x['corporate_sleeve'][0]['weight']=.5
        with self.assertRaises(DataError):waci(self.x['corporate_sleeve'])
    def test_waci_short_not_netted(self):
        self.x['corporate_sleeve'][0]['weight']=-.6
        with self.assertRaises(DataError):waci(self.x['corporate_sleeve'])
    def test_waci_sovereign_not_mixed(self):
        self.x['corporate_sleeve'][0]['asset_class']='sovereign_bond'
        with self.assertRaises(DataError):waci(self.x['corporate_sleeve'])
    def test_waci_period_currency_scope_consistency(self):
        for key in ('reporting_year','revenue_currency','scope_basis'):
            h=copy.deepcopy(self.x['corporate_sleeve']);h[0][key]='different'
            with self.subTest(key=key),self.assertRaises(DataError):waci(h)
    def test_waci_duplicate_instrument(self):
        h=self.x['corporate_sleeve'];h[1]['instrument_id']=h[0]['instrument_id']
        with self.assertRaises(DataError):waci(h)
    def test_attributed_emissions(self):self.assertEqual(attributed_emissions(20,200,1000,denominator_basis='equity_market_cap'),100)
    def test_attribution_requires_basis(self):
        with self.assertRaises(DataError):attributed_emissions(20,200,1000,denominator_basis='sovereign_gdp')
    def test_carbon_pass_through(self):
        r=carbon_cost_bridge(**self.x['carbon_inputs']);self.assertEqual(r['gross_carbon_cost'],60000000);self.assertEqual(r['incremental_ebitda_impact'],-24000000)
    def test_carbon_baseline_not_double_counted(self):
        x=self.x['carbon_inputs'];x['baseline_net_carbon_cost']=10000000
        self.assertEqual(carbon_cost_bridge(**x)['incremental_ebitda_impact'],-14000000)
    def test_free_allowance_cannot_make_negative_tax(self):self.assertEqual(carbon_cost_bridge(10,20,50,0,baseline_net_carbon_cost=0)['gross_carbon_cost'],0)
    def test_simplified_fcf_working_capital_release(self):self.assertEqual(simplified_fcf(100,10,20,-5),75)
    def test_duplicate_climate_treatment(self):
        with self.assertRaises(DataError):validate_treatments([{'risk_id':'R','treatment':'cash_flow'},{'risk_id':'R','treatment':'discount_rate'}])
    def test_distinct_treatments(self):validate_treatments([{'risk_id':'R1','treatment':'cash_flow'},{'risk_id':'R2','treatment':'discount_rate'}])
    def test_dcf_hand_calculation(self):self.assertAlmostEqual(dcf([110,121],.1)['enterprise_value'],200)
    def test_dcf_terminal_hand_calculation(self):self.assertAlmostEqual(dcf([100],.1,terminal_growth=0)['enterprise_value'],1000)
    def test_dcf_invalid_terminal_growth(self):
        for g in (.1,.2):
            with self.assertRaises(DataError):dcf([100],.1,terminal_growth=g)
    def test_no_negative_sustainable_terminal(self):
        with self.assertRaises(DataError):dcf([-100],.1,terminal_growth=0)
    def test_equity_claims_bridge(self):self.assertEqual(equity_bridge(1000,100,300,40,other_claims=0)['value_per_share'],20)
    def test_equity_shortfall_requires_distress_model(self):
        with self.assertRaises(DataError):equity_bridge(100,0,200,40)
    def test_no_implied_scenario_probabilities(self):self.assertIsNone(scenario_weighted_value([1,2,3])['weighted_value'])
    def test_scenario_weights_explicit(self):self.assertEqual(scenario_weighted_value([100,200],[.75,.25])['weighted_value'],125)
    def test_scenario_weights_no_renormalisation(self):
        with self.assertRaises(DataError):scenario_weighted_value([100,200],[.3,.3])
    def test_zero_coupon_bond(self):self.assertAlmostEqual(bond_present_value([{'time_years':2,'amount':121}],.05,.05),100)
    def test_bond_at_par(self):self.assertAlmostEqual(bond_present_value(self.x['bond_cash_flows_per_100'],.03,.02),100)
    def test_rate_spread_separated(self):
        x=bond_stress(self.x['bond_cash_flows_per_100'],.03,.015,rate_shock_bps=100,spread_shock_bps=75)
        self.assertLess(x['combined_value'],x['rate_only_value']);self.assertLess(x['combined_value'],x['spread_only_value']);self.assertGreater(x['interaction'],0)
    def test_callable_bond_rejected(self):
        with self.assertRaises(DataError):bond_present_value(self.x['bond_cash_flows_per_100'],.03,.02,instrument_type='callable')
    def test_bond_chronology(self):
        with self.assertRaises(DataError):bond_present_value(list(reversed(self.x['bond_cash_flows_per_100'])),.03,.02)
    def test_ecl_separate_hand_calculation(self):self.assertEqual(expected_credit_loss(100,.03,.5),1.5)
    def test_ecl_probability_range(self):
        with self.assertRaises(DataError):expected_credit_loss(100,1.1,.5)
    def test_worked_example_bridge(self):self.assertEqual(numbers()['illustrative_year1_fcf_million'],104)
