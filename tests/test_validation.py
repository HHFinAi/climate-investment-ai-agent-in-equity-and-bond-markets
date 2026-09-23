import copy, json, tempfile, unittest
from pathlib import Path
from climate_agent.calculations import DataError
from climate_agent.validation import *
from climate_agent import workflow as w
from climate_agent.demo import example_request,fixture_artifact

class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.req=example_request('equity');self.state=w.start('equity',self.req,Path(self.temp.name)/'run')
        self.agent=self.state['frozen']['agent_definitions']['mandate']
        self.a=fixture_artifact(self.state,'mandate')
        self.sources={x['id'] for x in self.state['frozen']['source_map']['anchors']}
    def validate(self):validate_artifact(self.a,self.agent,self.req,self.sources)
    def research(self):
        self.req['mode']='research';self.req['evidence']=[{'id':'REAL','kind':'issuer_disclosure','title':'Unit-test source, not a real filing','locator':'fixture://issuer','summary':'Test observation','entity_scope':'test issuer','as_of':'2026-09-20','retrieved_on':'2026-09-22','review_status':'VERIFIED','reviewed_by':'Test reviewer','reviewed_on':'2026-09-22'}]
        self.a['evidence_ids']=['REAL'];self.a['findings']=[{'kind':'fact','statement':'Test-only factual finding','time_basis':'as_of','topic':'financial','evidence_ids':['REAL'],'source_refs':[]}]
    def test_valid_artifact(self):self.validate()
    def test_unknown_evidence(self):
        self.a['evidence_ids']=['NOT-REGISTERED']
        with self.assertRaises(DataError):self.validate()
    def test_empty_method_refs(self):
        self.a['source_refs']=[]
        with self.assertRaises(DataError):self.validate()
    def test_no_confidence_calibration_claim(self):
        self.a['confidence']['calibrated']=True
        with self.assertRaises(DataError):self.validate()
    def test_confidence_out_of_range(self):
        self.a['confidence']['value']=1.1
        with self.assertRaises(DataError):self.validate()
    def test_blocked_requires_gap(self):
        self.a['status']='NEEDS_DATA'
        with self.assertRaises(DataError):self.validate()
    def test_needs_data_with_actionable_gap(self):
        self.a['status']='NEEDS_DATA';self.a['gaps']=['Supply legal issuer name.'];self.a['data']={};self.validate()
    def test_required_data_keys(self):
        self.a['data']={}
        with self.assertRaises(DataError):self.validate()
    def test_no_fact_from_textbook_alone(self):
        self.a['findings'][0]['kind']='fact'
        with self.assertRaises(DataError):self.validate()
    def test_no_fact_from_assumption(self):
        self.research();self.req['evidence'][0]['kind']='assumption'
        with self.assertRaises(DataError):self.validate()
    def test_no_timeless_current_fact_loophole(self):
        self.research();self.a['findings'][0]['time_basis']='timeless'
        with self.assertRaises(DataError):self.validate()
    def test_current_fact_reviewed(self):self.research();self.validate()
    def test_current_fact_unreviewed_rejected(self):
        self.research();self.req['evidence'][0]['review_status']='UNVERIFIED'
        with self.assertRaises(DataError):self.validate()
    def test_stale_market_fact(self):
        self.research();self.req['evidence'][0]['kind']='market_data';self.req['evidence'][0]['as_of']='2026-08-01'
        with self.assertRaises(DataError):self.validate()
    def test_explicit_historical_fact(self):
        self.research();self.req['evidence'][0]['kind']='market_data';self.req['evidence'][0]['as_of']='2020-01-01';self.a['findings'][0]['time_basis']='historical';self.validate()
    def test_current_fact_requires_freshness_policy(self):
        self.research();self.req['freshness_days']={}
        with self.assertRaises(DataError):self.validate()
    def test_policy_requires_primary_record(self):
        self.research();self.a['findings'][0]['topic']='policy'
        with self.assertRaises(DataError):self.validate()
    def test_current_policy_primary_reviewed(self):
        self.research();self.req['evidence'][0]['kind']='policy_primary';self.a['findings'][0]['topic']='policy';self.validate()
    def test_synthetic_cannot_enter_research(self):
        self.req['mode']='research'
        with self.assertRaises(DataError):validate_input(self.req)
    def test_future_evidence_rejected(self):
        self.req['evidence'][0]['as_of']='2027-01-01'
        with self.assertRaises(DataError):validate_input(self.req)
    def test_duplicate_evidence_ids(self):
        self.req['evidence'].append(copy.deepcopy(self.req['evidence'][0]))
        with self.assertRaises(DataError):validate_input(self.req)
    def test_unknown_issuer(self):
        self.req['instruments'][0]['issuer_id']='unknown'
        with self.assertRaises(DataError):validate_input(self.req)
    def test_wrong_issuer_type(self):
        self.req['entities'][0]['type']='sovereign'
        with self.assertRaises(DataError):validate_input(self.req)
    def test_placeholders_not_research(self):
        r=load_json(w.ROOT/'examples/research-request-template.json')
        with self.assertRaises(DataError):validate_input(r)
    def test_no_infinite_data(self):
        self.a['data']['other']=float('nan')
        with self.assertRaises(DataError):self.validate()
    def test_dag_cycle(self):
        with self.assertRaises(DataError):validate_dag([{'id':'a','depends_on':['b']},{'id':'b','depends_on':['a']}],{'a','b'})
    def test_dag_unknown_dependency(self):
        with self.assertRaises(DataError):validate_dag([{'id':'a','depends_on':['b']}],{'a'})
    def test_json_duplicate_keys(self):
        p=Path(self.temp.name)/'x.json';p.write_text('{"x":1,"x":2}')
        with self.assertRaises(DataError):load_json(p)
    def test_scenario_partial_weights_rejected(self):
        self.agent=self.state['frozen']['agent_definitions']['scenarios'];self.a=fixture_artifact(self.state,'scenarios');self.a['data']['scenario_register'][0]['probability']=.3
        with self.assertRaises(DataError):self.validate()
    def test_risk_double_count_rejected(self):
        self.agent=self.state['frozen']['agent_definitions']['financial-transmission'];self.a=fixture_artifact(self.state,'financial-transmission');self.a['data']['risk_treatment_register'].append({'risk_id':'CARBON-COST','treatment':'discount_rate'})
        with self.assertRaises(DataError):self.validate()
    def test_red_team_cannot_ignore_material_issue(self):
        self.agent=self.state['frozen']['agent_definitions']['red-team'];self.a=fixture_artifact(self.state,'red-team');self.a['data']['issues'][0]['severity']='MATERIAL'
        with self.assertRaises(DataError):self.validate()
