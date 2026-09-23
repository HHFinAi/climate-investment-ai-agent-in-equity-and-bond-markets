"""Structural and provenance gates. These cannot establish source entailment."""
from __future__ import annotations
import json, re, math
from datetime import date
from pathlib import Path
from typing import Any
from .calculations import DataError, number, validate_treatments, scenario_weighted_value

ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.:-]{0,95}$')
ASSETS = {'equity', 'corporate_bond', 'sovereign_bond', 'municipal_bond', 'structured_credit'}
KINDS = {'issuer_disclosure','market_data','scenario_data','policy_primary','assumption','synthetic','methodology'}
MODES = {'demo','source_study','research'}

def text(value: Any, name: str) -> str:
    if not isinstance(value,str) or not value.strip(): raise DataError(f'{name} must be nonempty text')
    return value

def identifier(value: Any, name: str) -> str:
    if not isinstance(value,str) or not ID.fullmatch(value): raise DataError(f'invalid {name}')
    return value

def iso_date(value: Any, name: str) -> date:
    if not isinstance(value,str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',value): raise DataError(f'{name} must be YYYY-MM-DD')
    try: return date.fromisoformat(value)
    except ValueError as exc: raise DataError(f'invalid {name}') from exc

def strings(value: Any, name: str) -> list[str]:
    if not isinstance(value,list) or any(not isinstance(x,str) or not x.strip() for x in value):
        raise DataError(f'{name} must be a list of nonempty strings')
    if len(value) != len(set(value)): raise DataError(f'duplicate {name}')
    return value

def object_value(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value,dict): raise DataError(f'{name} must be an object')
    return value

def load_json(path: Path) -> Any:
    def pairs(items):
        out={}
        for k,v in items:
            if k in out: raise DataError(f'duplicate JSON key: {k}')
            out[k]=v
        return out
    def constant(x): raise DataError(f'non-finite JSON number: {x}')
    try:
        return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=pairs, parse_constant=constant)
    except (OSError, ValueError) as exc:
        raise DataError(f'{path.name}: {exc}') from exc

def validate_evidence(record: dict[str, Any], request: dict[str, Any]) -> None:
    object_value(record,'evidence')
    identifier(record.get('id'),'evidence ID')
    if record.get('kind') not in KINDS: raise DataError('unsupported evidence kind')
    for k in ('title','locator','summary','entity_scope'): text(record.get(k),k)
    observed = iso_date(record.get('as_of'),'evidence.as_of')
    retrieved = iso_date(record.get('retrieved_on'),'evidence.retrieved_on')
    asof = iso_date(request.get('as_of'),'request.as_of')
    if observed > asof or retrieved > asof: raise DataError('look-ahead evidence: date exceeds analysis as-of date')
    if observed > retrieved: raise DataError('evidence observation cannot be after retrieval')
    if record.get('review_status') not in ('UNVERIFIED','VERIFIED','SYNTHETIC'): raise DataError('explicit evidence review status required')
    if record.get('review_status') == 'SYNTHETIC' or record.get('kind') == 'synthetic':
        if request['mode'] != 'demo': raise DataError('synthetic evidence is only permitted in demo mode')
    if record.get('review_status') == 'VERIFIED':
        text(record.get('reviewed_by'),'reviewed_by')
        rd = iso_date(record.get('reviewed_on'),'reviewed_on')
        if rd > asof or rd < retrieved: raise DataError('invalid evidence review date')

def ensure_json(value: Any) -> None:
    try: json.dumps(value,allow_nan=False)
    except (ValueError,TypeError) as exc: raise DataError('non-finite or non-JSON value in input/output') from exc

def validate_input(request: dict[str, Any]) -> None:
    ensure_json(request)
    object_value(request,'request')
    if request.get('schema_version') != '1.0': raise DataError('schema_version must be 1.0')
    if request.get('mode') not in MODES: raise DataError('mode must be demo, source_study or research')
    iso_date(request.get('as_of'),'as_of')
    mandate=object_value(request.get('mandate'),'mandate')
    for k in ('financial_objective','climate_objective','base_currency','investment_horizon','benchmark','constraints'):
        text(mandate.get(k),f'mandate.{k}')
    entities=request.get('entities')
    instruments=request.get('instruments')
    if not isinstance(entities,list) or not entities: raise DataError('entities required')
    if not isinstance(instruments,list) or not instruments: raise DataError('instruments required')
    ids=[]
    for e in entities:
        object_value(e,'entity');ids.append(identifier(e.get('id'),'entity ID'));text(e.get('name'),'entity name')
        if e.get('type') not in ('corporate','sovereign','municipal','spv'): raise DataError('invalid entity type')
    if len(ids)!=len(set(ids)): raise DataError('duplicate entity ID')
    types={e['id']:e['type'] for e in entities}
    if request['mode']=='research' and any('REPLACE_WITH' in str(v) or str(v).startswith('REPLACE_') for v in list(mandate.values())+[e['name'] for e in entities]):
        raise DataError('replace template identity/mandate placeholders before research')
    iids=[]
    for i in instruments:
        object_value(i,'instrument');iids.append(identifier(i.get('id'),'instrument ID'))
        if i.get('issuer_id') not in ids: raise DataError('instrument issuer is not mapped')
        if i.get('asset_class') not in ASSETS: raise DataError('unsupported asset class')
        compatible={'equity':{'corporate'},'corporate_bond':{'corporate','spv'},'sovereign_bond':{'sovereign'},'municipal_bond':{'municipal'},'structured_credit':{'spv','corporate'}}
        if types[i['issuer_id']] not in compatible[i['asset_class']]: raise DataError('issuer type inconsistent with instrument asset class')
        if i.get('label') not in ('none','green','sustainability','sustainability_linked','transition','blue'): raise DataError('explicit supported label required')
        if i['asset_class']=='equity' and i['label']!='none': raise DataError('bond label cannot be applied to equity')
        text(i.get('currency'),'instrument currency')
    if len(iids)!=len(set(iids)): raise DataError('duplicate instrument ID')
    policies=object_value(request.get('freshness_days'),'freshness_days')
    for k,v in policies.items():
        if k not in KINDS: raise DataError(f'unknown freshness kind: {k}')
        if isinstance(v,bool) or not isinstance(v,int) or v<0: raise DataError('freshness thresholds must be nonnegative whole days')
    evidence=request.get('evidence')
    if not isinstance(evidence,list): raise DataError('evidence must be a list, possibly empty')
    eids=[]
    for e in evidence:
        validate_evidence(e,request);eids.append(e['id'])
    if len(eids)!=len(set(eids)): raise DataError('duplicate evidence ID')

def validate_dag(nodes: list[dict[str, Any]], agent_ids: set[str]) -> None:
    if not nodes: raise DataError('empty DAG')
    ids=[n['id'] for n in nodes]
    if len(ids)!=len(set(ids)): raise DataError('duplicate node')
    for n in nodes:
        if n['id'] not in agent_ids: raise DataError(f'unknown agent {n["id"]}')
        deps=strings(n.get('depends_on'),'depends_on')
        if any(d not in ids for d in deps): raise DataError('unknown dependency')
    done=set()
    while len(done)<len(ids):
        ready={n['id'] for n in nodes if n['id'] not in done and set(n['depends_on'])<=done}
        if not ready: raise DataError('dependency cycle')
        done.update(ready)

def validate_artifact(artifact: dict[str, Any], agent: dict[str, Any], request: dict[str, Any], source_ids: set[str]) -> None:
    ensure_json(artifact)
    object_value(artifact,'artifact')
    if artifact.get('schema_version')!='1.0': raise DataError('artifact schema_version must be 1.0')
    if not re.fullmatch(r'[a-f0-9]{32}',str(artifact.get('run_id',''))): raise DataError('run_id must be copied from the work packet')
    if not re.fullmatch(r'[a-f0-9]{64}',str(artifact.get('input_digest',''))): raise DataError('input_digest must be copied from the work packet')
    if artifact.get('agent_id')!=agent['id']: raise DataError('agent ID mismatch')
    status=artifact.get('status')
    if status not in ('COMPLETE','NEEDS_DATA','BLOCKED'): raise DataError('invalid artifact status')
    text(artifact.get('summary'),'summary')
    refs=strings(artifact.get('source_refs'),'source_refs')
    if not refs or not set(refs)<=source_ids: raise DataError('unknown or empty methodology source_refs')
    gaps=strings(artifact.get('gaps'),'gaps')
    strings(artifact.get('assumptions'),'assumptions');strings(artifact.get('uncertainties'),'uncertainties')
    if status!='COMPLETE' and not gaps: raise DataError('blocking status requires an actionable gap')
    conf=object_value(artifact.get('confidence'),'confidence')
    number(conf.get('value'),'confidence.value',minimum=0,maximum=1)
    text(conf.get('basis'),'confidence.basis')
    if conf.get('calibrated') is not False: raise DataError('self-reported confidence must not be labelled calibrated')
    evidence={e['id']:e for e in request['evidence']}
    supplied=set(strings(artifact.get('evidence_ids'),'evidence_ids'))
    if not supplied<=evidence.keys(): raise DataError('artifact refers to unregistered evidence')
    findings=artifact.get('findings')
    if not isinstance(findings,list) or (status=='COMPLETE' and not findings): raise DataError('completed output requires findings')
    for f in findings:
        object_value(f,'finding');text(f.get('statement'),'finding.statement')
        kind=f.get('kind')
        if kind not in ('source_method','fact','inference','assumption','calculation'): raise DataError('invalid finding kind')
        time=f.get('time_basis')
        if time not in ('historical','as_of','scenario','timeless'): raise DataError('invalid time_basis')
        if kind=='fact' and time not in ('historical','as_of'): raise DataError('empirical facts require historical or as_of timing; scenarios are not facts')
        if f.get('topic') not in ('financial','climate','policy','methodology','governance'): raise DataError('invalid finding topic')
        eids=set(strings(f.get('evidence_ids'),'finding.evidence_ids'))
        methods=set(strings(f.get('source_refs'),'finding.source_refs'))
        if not eids<=supplied or not methods<=set(refs): raise DataError('finding references must be listed in envelope')
        if kind=='source_method' and not methods: raise DataError('method finding needs methodology refs')
        if kind in ('fact','calculation') and not eids: raise DataError('facts/calculations require evidence, not just textbook citations')
        if kind=='fact' and any(evidence[e]['kind'] in ('assumption','methodology') for e in eids):
            raise DataError('assumptions/methodology cannot be presented as issuer facts')
        if kind=='calculation': text(f.get('calculation_basis'),'calculation_basis')
        if kind=='fact' and request['mode']=='research':
            for eid in eids:
                e=evidence[eid]
                if e['review_status']!='VERIFIED': raise DataError(f'{eid}: fact evidence not reviewed')
                if time=='as_of':
                    limit=request['freshness_days'].get(e['kind'])
                    if limit is None: raise DataError(f'{eid}: explicit freshness threshold required')
                    age=(iso_date(request['as_of'],'as_of')-iso_date(e['as_of'],'evidence.as_of')).days
                    if age>limit: raise DataError(f'{eid}: stale current fact; refresh or label historical')
                    if f['topic']=='policy' and e['kind']!='policy_primary': raise DataError('current policy fact requires a reviewed primary policy record')
        if time=='as_of' and kind=='source_method': raise DataError('textbook method is not current empirical evidence')
    data=object_value(artifact.get('data'),'data')
    if status=='COMPLETE':
        for key in agent['required_data_keys']:
            if key not in data or data[key] is None or data[key]=='': raise DataError(f'missing output data: {key}')
        if agent['id']=='financial-transmission':
            if not isinstance(data['risk_treatment_register'],list): raise DataError('risk_treatment_register must be a list')
            validate_treatments(data['risk_treatment_register'])
        if agent['id']=='scenarios':
            rows=data['scenario_register']
            if not isinstance(rows,list) or not rows: raise DataError('scenario_register must be a nonempty list')
            for row in rows:
                text(row.get('id'),'scenario.id');text(row.get('name'),'scenario.name')
            if len({r['id'] for r in rows})!=len(rows): raise DataError('duplicate scenario ID')
            ps=[r.get('probability') for r in rows]
            if any(p is not None for p in ps): scenario_weighted_value([0]*len(rows),ps)
        if agent['id']=='red-team':
            if not isinstance(data['issues'],list): raise DataError('issues must be a list')
            for issue in data['issues']:
                if issue.get('severity') not in ('CRITICAL','MATERIAL','MINOR'): raise DataError('invalid issue severity')
                text(issue.get('description'),'issue.description')
                if not isinstance(issue.get('resolved'),bool): raise DataError('issue.resolved must be boolean')
                if issue['resolved']: text(issue.get('resolution'),'issue.resolution')
            if data['release_recommendation'] not in ('REVIEWABLE','BLOCKED'): raise DataError('invalid release recommendation')
            if any(not i['resolved'] and i['severity'] in ('CRITICAL','MATERIAL') for i in data['issues']) and data['release_recommendation']!='BLOCKED':
                raise DataError('unresolved material/critical issue requires BLOCKED recommendation')
