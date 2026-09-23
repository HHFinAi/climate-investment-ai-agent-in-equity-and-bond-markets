"""Deterministic synthetic replay for integration tests. This is NOT model research."""
from __future__ import annotations
import copy
from pathlib import Path
from typing import Any
from . import workflow as w
from .validation import load_json
from .calculations import (carbon_cost_bridge, simplified_fcf, dcf, equity_bridge,
                           bond_stress, expected_credit_loss, waci)


def example_request(name: str) -> dict[str,Any]:
    return load_json(w.ROOT/f'examples/requests/{name}.json')

def numbers() -> dict[str,Any]:
    x=load_json(w.ROOT/'examples/synthetic-financials.json')
    carbon=carbon_cost_bridge(**x['carbon_inputs'])
    valuation={}
    for scenario, cfs in x['cash_flow_scenarios_million'].items():
        ev=dcf(cfs,x['discount_rate'],terminal_growth=x['terminal_growth'])
        valuation[scenario]={**ev,**equity_bridge(ev['enterprise_value'],x['cash_million'],x['debt_million'],x['diluted_shares_million'])}
    return {'carbon_bridge':carbon,'equity_valuation_million':valuation,
            'baseline_fcf_million':simplified_fcf(240,35,60,5),
            'illustrative_year1_fcf_million':simplified_fcf(218,33,75,6),
            'bond_stress_per_100':bond_stress(x['bond_cash_flows_per_100'],.03,.015,rate_shock_bps=100,spread_shock_bps=75),
            'expected_loss_separate_sensitivity':expected_credit_loss(100,.03,.5),
            'corporate_sleeve_waci':waci(x['corporate_sleeve'])}

def fixture_artifact(state: dict[str,Any], aid: str) -> dict[str,Any]:
    agent=state['frozen']['agent_definitions'][aid]
    n=numbers()
    scenario_names=['baseline','managed_transition','delayed_transition','physical_stress']
    data_by_agent={
      'mandate':{'mandate_contract':state['frozen']['request']['mandate'],'instrument_scope':state['frozen']['request']['instruments']},
      'evidence':{'evidence_inventory':{'status':'SYNTHETIC_ONLY','records':['SYN-DATA','SYN-SCENARIOS'],'live_sources':[]},'entity_map':state['frozen']['request']['entities']},
      'science-materiality':{'materiality_map':[{'mechanism':'transition carbon cost','exposure':'illustrative corporate industrial production','vulnerability':'assumed partial pass-through'},{'mechanism':'physical disruption','exposure':'fictional coastal facility','vulnerability':'site loss function not supplied'}],'horizon_map':{'holding':'5 years','scenario':'5 explicit years plus illustrative terminal','long_term':'qualitative; no climate forecast'}},
      'disclosure-policy':{'policy_register':[{'jurisdiction':'not specified','status':'NOT_LEGALLY_VERIFIED','scenario_carbon_price':'assumption only; not a tax applicability conclusion'}],'disclosure_gaps':['No real issuer or current primary policy evidence used.']},
      'emissions':{'emissions_inventory':n['corporate_sleeve_waci'],'target_assessment':{'status':'ILLUSTRATIVE_ONLY','assumed_scope':'1+2','scope3':'not supplied; not treated as zero','net_zero_certification':False}},
      'physical-risk':{'physical_exposures':[{'asset':'fictional coastal facility','hazard':'flood','financial_effect':'scenario-only cost/capex sensitivity; no estimated event likelihood'}],'adaptation_options':[{'option':'resilience capital expenditure','illustrative_incremental_capex_million':15,'loss_reduction_estimated':False}]},
      'transition':{'transition_exposures':n['carbon_bridge'],'opportunity_map':{'illustrative_incremental_solution_revenue_million':40,'assumed_incremental_margin':.25,'source':'SYN-SCENARIOS','no_guaranteed_returns':True}},
      'scenarios':{'scenario_register':[{'id':s.upper(),'name':s,'provider':'HHFinAi synthetic demonstration','version':'0.1.0','probability':None} for s in scenario_names],'model_limitations':['No IAM/GCM dataset loaded. Cash flows are analyst-authored synthetic sensitivities, not forecasts.']},
      'financial-transmission':{'financial_bridge':{'baseline_fcf_million':n['baseline_fcf_million'],'scenario_year1_fcf_million':n['illustrative_year1_fcf_million'],'year1_ebitda_bridge':'240 - 24 carbon - 8 physical cost + 10 solutions contribution = 218; taxes, capex, WC supplied separately','source':'SYN-DATA; SYN-SCENARIOS'},'risk_treatment_register':[{'risk_id':'CARBON-COST','treatment':'cash_flow'},{'risk_id':'PHYSICAL-COST','treatment':'cash_flow'},{'risk_id':'ADAPTATION-CAPEX','treatment':'cash_flow'},{'risk_id':'SOLUTION-MARGIN','treatment':'cash_flow'}]},
      'equity':{'equity_valuation':n['equity_valuation_million'],'variant_and_sensitivity':{'market_price':'NOT_SUPPLIED','current_upside':None,'key_sensitivities':['cost pass-through','cash-flow path','terminal growth'],'weights':None,'discount_rate_held_constant':True}},
      'corporate-credit':{'credit_assessment':{'recourse':'illustrative senior corporate obligation; legal documents not supplied','default_and_recovery':'analyst assumptions only','separate_undiscounted_ecl_per_100':n['expected_loss_separate_sensitivity'],'ecl_not_subtracted_from_bond_price':True},'bond_valuation':n['bond_stress_per_100']},
      'sovereign':{'sovereign_transmission':{'issuer':'Asteria (fictional)','channels':['tax revenue sensitivity','reconstruction spending','external financing'],'political_rating':None,'quantification':'not estimated'},'rates_and_credit':{'currency_basis':'hypothetical USD debt; not a local monetary-policy model','rates_vs_spreads':'separate sensitivity axes','country_waci_merged_with_corporate':False}},
      'municipal':{'local_exposure':{'issuer':'Bayhaven (fictional)','geography':'not geocoded','hazard':'illustrative flood sensitivity'},'repayment_analysis':{'tax_base':'not supplied','sovereign_guarantee':'not assumed','valuation':'not estimated; local revenue/recourse documents required for real research'}},
      'labelled-debt':{'label_assessment':{'label':'green','status':'UNVERIFIED_SYNTHETIC','required_documents':['framework','allocation report','impact report','external review'],'certification':False},'contract_and_impact':{'issuer_credit':'separate corporate-credit artifact','avoided_emissions':'not netted against gross emissions','additionality':'not established','ringfenced_credit':'not assumed'}},
      'structured-credit':{'collateral_analysis':{'pool':'fictional resilience loan pool','locations':'not supplied','risk_transmission':['asset cash flow','insurance','recovery','waterfall']},'structural_limits':{'tranche_price':None,'required_model':'specialist loan/waterfall model','simple_bond_helper_used_for_tranche':False}},
      'portfolio':{'portfolio_assessment':{'corporate_metric_example':n['corporate_sleeve_waci'],'sovereign_and_corporate_metrics_combined':False,'allocation_recommendation':None,'live_portfolio_analysed':False},'constraint_checks':{'status':'SYNTHETIC_ONLY','financial_and_climate_objectives':'reported separately','real_world_emission_reduction_claim':False}},
      'stewardship':{'engagement_plan':[{'question':'What facility-level exposure and insurance evidence support resilience assumptions?','milestone':'obtain source-backed asset data before real review'},{'question':'Which costs can be passed through and on what contractual basis?','milestone':'reconcile pass-through to customer contracts'}],'approval_requirements':['Human authorisation before any contact, vote or other external action.']},
      'monitoring':{'monitoring_plan':[{'item':'issuer disclosure','owner':'analyst','trigger':'new filing'},{'item':'bond terms and label documents','owner':'credit analyst','trigger':'new issue or revised KPI terms'},{'item':'scenario and data vintage','owner':'risk analyst','trigger':'new model version or material evidence change'}],'reopen_triggers':['Revise upstream artifact and rerun its descendants. No background monitor is running.']},
      'red-team':{'issues':[{'severity':'MINOR','description':'Synthetic replay verifies mechanics only, not a live investment thesis.','resolved':False}],'release_recommendation':'REVIEWABLE'},
      'investment-memo':{'investment_case':{'decision':'NO_TRADE_DECISION','purpose':'illustrate equity/bond branch separation and auditable arithmetic','equity_values':n['equity_valuation_million'],'corporate_bond_stress':n['bond_stress_per_100'],'missing_real_evidence':'issuer, market, policy, physical loss functions and contract verification'},'client_disclosure':'Synthetic demonstration; no live research, climate forecast, legal certification or investment approval.'}}
    result={'schema_version':'1.0','run_id':state['run_id'],'input_digest':state['frozen_digest'],'agent_id':aid,'status':'COMPLETE',
            'summary':f'Synthetic replay of {agent["title"]}; illustrates the workflow contract, not a real investment assessment.',
            'source_refs':agent['source_refs'],'evidence_ids':['SYN-DATA','SYN-SCENARIOS'],
            'findings':[{'kind':'source_method','statement':agent['purpose'],'time_basis':'timeless','topic':'methodology','evidence_ids':[],'source_refs':agent['source_refs']}],
            'data':data_by_agent[aid],'assumptions':['All companies, securities and numerical paths are fictional demo inputs.'],
            'gaps':[],'uncertainties':['No semantic model-output evaluation or live-source validation has been performed.'],
            'confidence':{'value':.5,'basis':'Fixed demonstration value; not a model-derived confidence or empirical calibration.','calibrated':False},
            'provenance':{'provider':'deterministic_synthetic_replay','llm_called':False}}
    if aid in ('equity','corporate-credit','financial-transmission','emissions'):
        result['findings'].append({'kind':'calculation','statement':'Reported numerical illustrations were computed from the bundled synthetic inputs.','time_basis':'scenario','topic':'financial','evidence_ids':['SYN-DATA','SYN-SCENARIOS'],'source_refs':agent['source_refs'],'calculation_basis':'climate_agent.demo.numbers() using documented helpers and examples/synthetic-financials.json; see calculation-conventions.md.'})
    return result

def run_demo(name: str, directory: Path) -> dict[str,Any]:
    state=w.start(name,example_request(name),directory)
    while w.ready_agents(state):
        aid=w.ready_agents(state)[0]
        state=w.submit(directory,aid,fixture_artifact(state,aid),expected_revision=state['revision'])
    (directory/'report.md').write_text(w.report(state),encoding='utf-8')
    return state
