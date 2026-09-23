#!/usr/bin/env python3
"""Guarded initial publication; previews without --execute.

Never reads/prints tokens, never overwrites a remote, never publishes the PDF.
A fresh sibling staging checkout keeps existing local repositories untouched.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path, PurePosixPath
ROOT=Path(__file__).resolve().parents[1]
OWNER='HHFinAi'
REPOSITORY='climate-investment-ai-agent-in-equity-and-bond-markets'

class PublishError(RuntimeError): pass

def safe_path(path: str) -> bool:
    p=PurePosixPath(path)
    if not path or '\x00' in path or p.is_absolute() or '\\' in path or '..' in p.parts or ':' in path: return False
    if any(x in p.parts for x in ('.git','__pycache__','runs','local_sources','.venv','private')): return False
    if p.name.startswith('.env') or p.name=='.DS_Store': return False
    if p.suffix.lower() in ('.pdf','.pem','.key','.p12','.pfx','.zip','.gz','.png','.jpg'): return False
    return p.suffix.lower() in ('.md','.json','.py','.csv','.txt','.yml','.yaml') or p.name in ('.gitignore','.gitattributes','VERSION','LICENSE','CITATION.cff')

def release_files(root: Path) -> list[str]:
    manifest_path=root/'FILE_MANIFEST.json'
    try: manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    except (OSError,ValueError) as exc: raise PublishError('release manifest missing or invalid') from exc
    files=manifest.get('files')
    if not isinstance(files,dict) or not files or len(files)>1000: raise PublishError('invalid release file list')
    resolved=root.resolve()
    for path,sha in files.items():
        if not isinstance(path,str) or not safe_path(path): raise PublishError(f'unsafe release path: {path}')
        p=root/path
        if any((root.joinpath(*PurePosixPath(path).parts[:i])).is_symlink() for i in range(1,len(PurePosixPath(path).parts)+1)):
            raise PublishError(f'symlink in release: {path}')
        if not p.resolve().is_relative_to(resolved) or not p.is_file(): raise PublishError(f'missing/outside-root file: {path}')
        if p.stat().st_size>2_000_000: raise PublishError('unexpected oversized file')
        if hashlib.sha256(p.read_bytes()).hexdigest()!=sha: raise PublishError(f'release hash mismatch: {path}')
    return sorted(files)+['FILE_MANIFEST.json']

def run(args: list[str], *, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    env=dict(os.environ,GH_PROMPT_DISABLED='1',GH_HOST='github.com',GIT_TERMINAL_PROMPT='0')
    try: result=subprocess.run(args,cwd=cwd,text=True,capture_output=True,env=env,timeout=240)
    except (OSError,subprocess.TimeoutExpired) as exc: raise PublishError(f'command could not complete: {args[0]}') from exc
    if check and result.returncode:
        # Never dump credentials or token-bearing environment variables.
        raise PublishError(f'{args[0]} {args[1] if len(args)>1 else ""} failed (exit {result.returncode}); inspect local authentication/permissions. No force or overwrite attempted.')
    return result

def ensure_target_absent(returncode: int, response: str) -> None:
    if returncode==0: raise PublishError('target repository already exists; initial publisher will not overwrite it')
    if not re.search(r'^HTTP/\S+\s+404\b',response,re.M):
        raise PublishError('absence not established by an HTTP 404; authorization/network errors are not treated as absence')

def execute(root: Path) -> dict:
    files=release_files(root)
    if not shutil.which('gh') or not shutil.which('git'): raise PublishError('install GitHub CLI (gh) and Git before publishing')
    user=json.loads(run(['gh','api','--hostname','github.com','user']).stdout)
    if str(user.get('login','')).casefold()!=OWNER.casefold(): raise PublishError('authenticated GitHub user must be HHFinAi')
    probe=run(['gh','api','--hostname','github.com','--include',f'repos/{OWNER}/{REPOSITORY}'],check=False)
    ensure_target_absent(probe.returncode,probe.stdout)
    author_name=run(['git','config','--get','user.name'],cwd=root,check=False).stdout.strip()
    author_email=run(['git','config','--get','user.email'],cwd=root,check=False).stdout.strip()
    if not author_name or not author_email: raise PublishError('configure Git user.name and user.email before creating the remote')
    run([sys.executable,'-m','unittest','discover','-s','tests','-v'],cwd=root)
    run([sys.executable,'scripts/check_repository.py'],cwd=root)
    stage=Path(tempfile.mkdtemp(prefix=REPOSITORY+'-publish-',dir=root.parent))
    print(f'Staging directory retained for review/recovery: {stage}')
    # Recheck every copied byte to narrow the change-between-validation-and-copy window.
    for rel in files:
        dest=stage/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/rel,dest)
    release_files(stage)
    run(['git','init','-b','main'],cwd=stage)
    run(['git','config','user.name',author_name],cwd=stage)
    run(['git','config','user.email',author_email],cwd=stage)
    run(['git','add','--',*files],cwd=stage)
    run(['git','-c','commit.gpgsign=false','commit','-m','Initial climate investment agent workflow with source mapping and tests'],cwd=stage)
    target=f'{OWNER}/{REPOSITORY}'
    run(['gh','repo','create',target,'--private','--description','Source-grounded, human-reviewed climate investment research for equity and bond markets.'],cwd=stage)
    # Check privacy before publishing any content. Do not auto-change existing settings.
    remote=json.loads(run(['gh','api','--hostname','github.com',f'repos/{target}']).stdout)
    if remote.get('private') is not True: raise PublishError('new remote is not confirmed private; no source content pushed')
    run(['git','remote','add','origin',f'https://github.com/{target}.git'],cwd=stage)
    run(['git','-c','credential.helper=','-c','credential.helper=!gh auth git-credential','push','-u','origin','main'],cwd=stage)
    local_sha=run(['git','rev-parse','HEAD'],cwd=stage).stdout.strip()
    ref=json.loads(run(['gh','api','--hostname','github.com',f'repos/{target}/git/ref/heads/main']).stdout)
    if ref.get('object',{}).get('sha')!=local_sha: raise PublishError('remote commit verification failed; inspect the retained staging directory')
    return {'status':'CREATED_AND_PUSHED','repository':target,'private':True,'commit':local_sha,
            'url':remote['html_url'],'staging_directory':str(stage),'remote_ci_status':'NOT_CHECKED'}

def main(argv=None) -> int:
    p=argparse.ArgumentParser(description='Create the new HHFinAi private repository; never overwrite an existing target.')
    p.add_argument('--execute',action='store_true',help='Explicitly authorise remote creation and initial push')
    args=p.parse_args(argv)
    try:
        if args.execute: result=execute(ROOT)
        else:
            files=release_files(ROOT)
            result={'status':'LOCAL_PREVIEW_ONLY','repository':f'{OWNER}/{REPOSITORY}','private':True,
                    'files_to_publish':len(files),'source_pdf_included':False,'remote_created':False,
                    'next_step':'Authenticate HHFinAi using gh, configure Git identity, then rerun with --execute.'}
        print(json.dumps(result,indent=2));return 0
    except (PublishError,ValueError) as exc:
        print(json.dumps({'status':'NOT_COMPLETED','reason':str(exc),'partial_failure_note':'If creation already occurred, inspect the retained staging directory and private remote. No automatic deletion or force-push will occur.'}),file=sys.stderr);return 2
if __name__=='__main__': raise SystemExit(main())
