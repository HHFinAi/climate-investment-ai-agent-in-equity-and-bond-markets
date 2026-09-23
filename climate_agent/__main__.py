"""Run `python -m climate_agent --help` from the repository root."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from .calculations import DataError
from .validation import load_json
from . import workflow as w

def main(argv=None) -> int:
    p=argparse.ArgumentParser(description='Source-grounded climate investment workflow; no automated trading.')
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('list',help='List available workflows')
    s=sub.add_parser('plan',help='Validate input and create an immutable workflow snapshot')
    s.add_argument('--workflow',required=True);s.add_argument('--input',type=Path,required=True);s.add_argument('--out',type=Path,required=True)
    for cmd in ('next','status','report'):
        s=sub.add_parser(cmd);s.add_argument('--run',type=Path,required=True)
    s=sub.add_parser('submit',help='Validate an agent artifact and invalidate descendants on revision')
    s.add_argument('--run',type=Path,required=True);s.add_argument('--agent',required=True)
    s.add_argument('--artifact',type=Path,required=True);s.add_argument('--revision',type=int,required=True)
    s=sub.add_parser('review',help='Record a human research decision, never a trade authorisation')
    s.add_argument('--run',type=Path,required=True);s.add_argument('--reviewer',required=True)
    s.add_argument('--decision',choices=['APPROVE_RESEARCH','REJECT_RESEARCH'],required=True)
    s.add_argument('--rationale',required=True);s.add_argument('--attest-human-review',action='store_true');s.add_argument('--revision',type=int,required=True)
    s=sub.add_parser('demo',help='Run deterministic synthetic fixtures, NOT an LLM or live research')
    s.add_argument('--workflow',default='multi-asset');s.add_argument('--out',type=Path,required=True)
    args=p.parse_args(argv)
    try:
        if args.command=='list': result={'workflows':w.available_workflows()}
        elif args.command=='plan': result=w.status(w.start(args.workflow,load_json(args.input),args.out))
        elif args.command=='next': result=w.request_packets(w.load_state(args.run))
        elif args.command=='status': result=w.status(w.load_state(args.run))
        elif args.command=='submit': result=w.status(w.submit(args.run,args.agent,load_json(args.artifact),expected_revision=args.revision))
        elif args.command=='review': result=w.status(w.human_review(args.run,args.reviewer,args.decision,args.rationale,attest_human=args.attest_human_review,expected_revision=args.revision))
        elif args.command=='report':
            print(w.report(w.load_state(args.run)));return 0
        elif args.command=='demo':
            from .demo import run_demo
            result=w.status(run_demo(args.workflow,args.out))
        print(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False));return 0
    except (DataError,KeyError,TypeError,OverflowError) as exc:
        print(json.dumps({'status':'ERROR','message':str(exc)}),file=sys.stderr);return 2
if __name__=='__main__': raise SystemExit(main())
