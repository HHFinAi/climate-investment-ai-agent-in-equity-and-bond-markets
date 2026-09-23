#!/usr/bin/env python3
"""Create a deterministic ZIP from the reviewed release manifest only."""
from __future__ import annotations
import argparse, hashlib, json, sys, zipfile
from pathlib import Path
from publish_github import release_files, REPOSITORY, PublishError
ROOT=Path(__file__).resolve().parents[1]
def build(output: Path) -> dict:
    files=release_files(ROOT)
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for path in files:
            info=zipfile.ZipInfo(f'{REPOSITORY}/{path}',date_time=(2026,9,23,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            z.writestr(info,(ROOT/path).read_bytes())
    return {'archive':str(output),'files':len(files),'sha256':hashlib.sha256(output.read_bytes()).hexdigest()}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    try: print(json.dumps(build(a.out),indent=2))
    except (OSError,PublishError) as exc: print(str(exc),file=sys.stderr);raise SystemExit(2)
