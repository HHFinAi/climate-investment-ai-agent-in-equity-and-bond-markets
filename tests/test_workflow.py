import copy, json, tempfile, unittest
from pathlib import Path
from climate_agent.calculations import DataError
from climate_agent import workflow as w
from climate_agent.demo import example_request, fixture_artifact,run_demo
from climate_agent.__main__ import main

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.out=Path(self.temp.name)/'run'
    def start(self,mode='demo',issuer_evidence=True):
        req=example_request('equity')
        if mode!='demo':
            req['mode']=mode
            for e in req['evidence']:e['kind']='assumption';e['review_status']='UNVERIFIED'
            if issuer_evidence:
                req['evidence'].append({'id':'TEST-ISSUER','kind':'issuer_disclosure','title':'Unit-test record, not a real source','locator':'fixture://test','summary':'A test of review gating, not investment evidence.','entity_scope':'CORP','as_of':'2026-09-20','retrieved_on':'2026-09-22','review_status':'VERIFIED','reviewed_by':'Test human','reviewed_on':'2026-09-22'})
        return w.start('equity',req,self.out)
    def finish(self,state):
        while w.ready_agents(state):
            aid=w.ready_agents(state)[0]
            state=w.submit(self.out,aid,fixture_artifact(state,aid),expected_revision=state['revision'])
        return state
    def test_first_agent_only_mandate(self):self.assertEqual(w.ready_agents(self.start()),['mandate'])
    def test_dependency_guard(self):
        s=self.start()
        with self.assertRaises(DataError):w.submit(self.out,'equity',fixture_artifact(s,'equity'),expected_revision=0)
    def test_wrong_run_artifact_rejected(self):
        s=self.start();a=fixture_artifact(s,'mandate');a['run_id']='0'*32
        with self.assertRaises(DataError):w.submit(self.out,'mandate',a,expected_revision=0)
    def test_wrong_input_digest_rejected(self):
        s=self.start();a=fixture_artifact(s,'mandate');a['input_digest']='0'*64
        with self.assertRaises(DataError):w.submit(self.out,'mandate',a,expected_revision=0)
    def test_first_submit_opens_evidence(self):
        s=self.start();s=w.submit(self.out,'mandate',fixture_artifact(s,'mandate'),expected_revision=0)
        self.assertEqual(w.ready_agents(s),['evidence'])
    def test_stale_revision_guard(self):
        s=self.start();s=w.submit(self.out,'mandate',fixture_artifact(s,'mandate'),expected_revision=0)
        with self.assertRaises(DataError):w.submit(self.out,'evidence',fixture_artifact(s,'evidence'),expected_revision=0)
    def test_needs_data_stops_descendants(self):
        s=self.start();a=fixture_artifact(s,'mandate');a.update(status='NEEDS_DATA',gaps=['Confirm investment objective.'],data={})
        s=w.submit(self.out,'mandate',a,expected_revision=0)
        self.assertEqual(w.ready_agents(s),['mandate']);self.assertEqual(w.status(s)['status'],'NEEDS_DATA')
    def test_resubmit_invalidates_descendants(self):
        s=self.finish(self.start());self.assertEqual(len(s['artifacts']),15)
        s=w.submit(self.out,'evidence',fixture_artifact(s,'evidence'),expected_revision=s['revision'])
        self.assertEqual(set(s['artifacts']),{'mandate','evidence'});self.assertEqual(len(s['history']),14)
    def test_frozen_input_change_detected(self):
        s=self.start();s['frozen']['request']['as_of']='2026-09-24';w.atomic_json(self.out/'state.json',s)
        with self.assertRaises(DataError):w.load_state(self.out)
    def test_existing_directory_not_overwritten(self):
        self.start()
        with self.assertRaises(DataError):w.start('equity',example_request('equity'),self.out)
    def test_workflow_path_injection_rejected(self):
        with self.assertRaises(DataError):w.start('../../secret',example_request('equity'),self.out)
    def test_label_requires_additional_route(self):
        with self.assertRaises(DataError):w.start('corporate-bond',example_request('labelled-bond'),self.out)
    def test_mixed_workflow_prunes_irrelevant_branches(self):
        s=w.start('multi-asset',example_request('equity'),self.out)
        ids={n['id'] for n in s['frozen']['nodes']};self.assertIn('equity',ids);self.assertNotIn('sovereign',ids);self.assertNotIn('labelled-debt',ids)
    def test_labelled_sovereign_uses_sovereign_not_corporate_credit(self):
        req=example_request('sovereign-bond');req['instruments'][0]['label']='green'
        s=w.start('labelled-bond',req,self.out);ids={n['id'] for n in s['frozen']['nodes']}
        self.assertTrue({'sovereign','labelled-debt'}<=ids);self.assertNotIn('corporate-credit',ids)
    def test_incomplete_report_is_not_fabricated(self):
        text=w.report(self.start());self.assertIn('PENDING — no analysis',text);self.assertIn('NOT RECORDED',text)
    def test_explicit_no_execution(self):
        self.assertIs(w.status(self.finish(self.start()))['execution_authorised'],False)
    def test_demo_cannot_be_approved(self):
        s=self.finish(self.start())
        with self.assertRaises(DataError):w.human_review(self.out,'Human','APPROVE_RESEARCH','Reviewed',attest_human=True,expected_revision=s['revision'])
    def test_source_study_cannot_be_approved(self):
        s=self.finish(self.start('source_study'))
        with self.assertRaises(DataError):w.human_review(self.out,'Human','APPROVE_RESEARCH','Reviewed',attest_human=True,expected_revision=s['revision'])
    def test_human_attestation_required(self):
        s=self.finish(self.start('research'))
        with self.assertRaises(DataError):w.human_review(self.out,'Human','APPROVE_RESEARCH','Reviewed',attest_human=False,expected_revision=s['revision'])
    def test_human_approval_recorded_without_trading(self):
        s=self.finish(self.start('research'));s=w.human_review(self.out,'Test reviewer','APPROVE_RESEARCH','Unit-test review only.',attest_human=True,expected_revision=s['revision'])
        self.assertEqual(w.status(s)['status'],'HUMAN_REVIEW_RECORDED');self.assertFalse(s['review']['execution_authorised'])
    def test_no_assumptions_only_research_approval(self):
        s=self.finish(self.start('research',issuer_evidence=False))
        with self.assertRaises(DataError):w.human_review(self.out,'Human','APPROVE_RESEARCH','Reviewed',attest_human=True,expected_revision=s['revision'])
    def test_material_issue_blocks_approval(self):
        s=self.finish(self.start('research'));a=fixture_artifact(s,'red-team');a['data']['issues'][0]['severity']='MATERIAL';a['data']['release_recommendation']='BLOCKED'
        s=w.submit(self.out,'red-team',a,expected_revision=s['revision']);s=self.finish(s)
        self.assertEqual(w.status(s)['status'],'BLOCKED_FOR_REVIEW')
        with self.assertRaises(DataError):w.human_review(self.out,'Human','APPROVE_RESEARCH','Reviewed',attest_human=True,expected_revision=s['revision'])
    def test_revision_invalidates_human_review(self):
        s=self.finish(self.start('research'));s=w.human_review(self.out,'Human','APPROVE_RESEARCH','Unit test',attest_human=True,expected_revision=s['revision'])
        s=w.submit(self.out,'equity',fixture_artifact(s,'equity'),expected_revision=s['revision'])
        self.assertIsNone(s['review']);self.assertNotIn('investment-memo',s['artifacts'])
    def test_work_packets_include_trust_boundary(self):
        packet=w.request_packets(self.start())[0]
        self.assertIn('untrusted_research_inputs',packet);self.assertIn('trusted_operating_contract',packet)
    def test_lock_stops_concurrent_write(self):
        s=self.start();(self.out/'.write.lock').write_text('other writer')
        with self.assertRaises(DataError):w.submit(self.out,'mandate',fixture_artifact(s,'mandate'),expected_revision=0)

# Separate counted integration test for each complete synthetic route.
def make_route_test(name):
    def test(self):
        state=run_demo(name,self.out)
        self.assertEqual(w.status(state)['status'],'DEMO_COMPLETE_NOT_APPROVED')
        self.assertTrue((self.out/'report.md').is_file())
        self.assertTrue(all(v['status']=='COMPLETE' for v in state['artifacts'].values()))
    return test
for name in w.available_workflows():
    setattr(WorkflowTests,'test_full_route_'+name.replace('-','_'),make_route_test(name))
