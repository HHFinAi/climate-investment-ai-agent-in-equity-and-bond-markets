#!/usr/bin/env python3
"""Offline package invariants. Does not certify analytical accuracy or law."""
from __future__ import annotations
import json, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from climate_agent import __version__
from climate_agent.validation import load_json, validate_dag, validate_input
from climate_agent.workflow import registry, available_workflows, select_nodes

def check() -> dict:
    assert (ROOT/'VERSION').read_text().strip()==__version__, 'version mismatch'
    agents=registry()
    assert len(agents)==20, 'expected 20 role contracts'
    source=load_json(ROOT/'references/source-map.json')
    assert source['pdf_page_count']==897
    ids={a['id'] for a in source['anchors']}
    assert len(ids)==len(source['anchors']), 'duplicate source anchor'
    assert [c['chapter'] for c in source['chapters']]==list(range(1,11))
    for a in source['anchors']:
        assert all(isinstance(p,int) and 1<=p<=897 for p in a['pdf_pages'])
    for a in agents.values():
        assert set(a['source_refs'])<=ids, f'unknown source reference {a["id"]}'
        path=ROOT/a['path']
        assert path.is_file() and len(path.read_text())>800, f'missing role content {path}'
        assert all(s in path.read_text() for s in a['source_refs'])
    workflows=available_workflows()
    assert len(workflows)==7
    counts={}
    for name in workflows:
        wf=load_json(ROOT/f'workflows/{name}.json')
        assert wf['human_review_required'] is True and wf['automatic_execution'] is False
        validate_dag(wf['nodes'],set(agents))
        req=load_json(ROOT/f'examples/requests/{name}.json')
        validate_input(req)
        counts[name]=len(select_nodes(name,req))
    entry=(ROOT/'SKILL.md').read_text()
    assert entry.startswith('---\n') and '\n---\n' in entry[4:]
    front=entry.split('---',2)[1]
    name=re.search(r'^name: (.+)$',front,re.M).group(1)
    assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',name) and len(name)<=64
    assert 'description: >-' in front and 'metadata:' in front
    metadata=front.split('metadata:\n',1)[1].splitlines()
    for line in metadata:
        assert re.fullmatch(r'  [a-z_]+: .+',line), 'this package uses scalar metadata only'
    assert 'version: "'+__version__+'"' in front
    for p in ['README.md','WORKFLOW.md','AGENTS.md','NOTICE.md','references/data-contract.md','references/calculation-conventions.md','references/limitations.md','PUBLISHING.md']:
        assert (ROOT/p).is_file(), f'missing {p}'
    for p in (ROOT/'schemas').glob('*.json'): assert isinstance(load_json(p),dict)
    workflow=(ROOT/'.github/workflows/validate.yml').read_text()
    assert 'contents: read' in workflow and 'contents: write' not in workflow
    return {'status':'PASS','version':__version__,'roles':len(agents),'workflows':counts,'source_anchors':len(ids),'source_pdf_distributed':False}
if __name__=='__main__':
    try: print(json.dumps(check(),indent=2))
    except (AssertionError,ValueError,KeyError) as exc: print(f'FAIL: {exc}',file=sys.stderr);raise SystemExit(1)
