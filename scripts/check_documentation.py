#!/usr/bin/env python3
"""Offline documentation checks, not source verification or audit assurance."""
from __future__ import annotations
import ast
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_URL = 'https://github.com/HHFinAi/climate-investment-ai-agent-in-equity-and-bond-markets'


def local_path(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f'reference outside repository: {relative}')
    if not path.is_file():
        raise ValueError(f'missing reference: {relative}')
    return path


def symbols(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding='utf-8'))
    return {node.name for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}


def validate_claims(root: Path, register: dict) -> int:
    if register.get('independent_certification') is not False:
        raise ValueError('claims must not imply independent certification')
    rows = register.get('claims')
    if not isinstance(rows, list) or not rows:
        raise ValueError('nonempty claims list required')
    ids: set[str] = set()
    for row in rows:
        cid = row.get('id')
        if not isinstance(cid, str) or not re.fullmatch(r'IQ-[0-9]{2}', cid) or cid in ids:
            raise ValueError('invalid/duplicate claim ID')
        ids.add(cid)
        for key in ('claim', 'boundary'):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError(f'{cid}: {key} is required')
        code = row['implementation']
        if code['symbol'] not in symbols(local_path(root, code['path'])):
            raise ValueError(f'{cid}: implementation symbol missing')
        tests = row['tests']
        names = tests['symbols']
        available = symbols(local_path(root, tests['path']))
        if (not isinstance(names, list) or not names or len(names) != len(set(names))
                or any(not n.startswith('test_') or n not in available for n in names)):
            raise ValueError(f'{cid}: named test missing/invalid')
    return len(ids)


def heading_ids(text: str) -> set[str]:
    ids: set[str] = set()
    for heading in re.findall(r'^#{1,6}\s+(.+?)\s*#*$', text, re.M):
        slug = re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')
        suffix, value = 0, slug
        while value in ids:
            suffix += 1
            value = f'{slug}-{suffix}'
        ids.add(value)
    return ids


def validate_links(root: Path, documents: list[Path]) -> int:
    checked = 0
    for doc in documents:
        text = re.sub(r'```.*?```', '', doc.read_text(encoding='utf-8'), flags=re.S)
        for target in re.findall(r'\[[^\]]*\]\(([^)\s]+)\)', text):
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc:
                continue  # No network or claims that remote links were verified.
            dest = (doc.parent / unquote(parsed.path)).resolve() if parsed.path else doc.resolve()
            if not dest.is_relative_to(root.resolve()) or not dest.exists():
                raise ValueError(f'{doc.name}: unresolved link {target}')
            if parsed.fragment and dest.is_file() and dest.suffix == '.md':
                if unquote(parsed.fragment) not in heading_ids(dest.read_text(encoding='utf-8')):
                    raise ValueError(f'{doc.name}: unresolved heading {target}')
            checked += 1
    return checked


def check(root: Path = ROOT) -> dict:
    register = json.loads((root / 'docs/claims.json').read_text(encoding='utf-8'))
    if register['engine_version'] != (root / 'VERSION').read_text().strip():
        raise ValueError('claim-register version mismatch')
    count = validate_claims(root, register)
    matrix = (root / 'docs/INSTITUTIONAL_QUALITY.md').read_text(encoding='utf-8')
    for row in register['claims']:
        if f"| {row['id']} |" not in matrix:
            raise ValueError('claim missing from visible matrix')
    docs = [root / 'README.md', root / 'SKILL.md', *sorted((root / 'docs').glob('*.md'))]
    links = validate_links(root, docs)
    cff = (root / 'CITATION.cff').read_text(encoding='utf-8')
    for value in ('cff-version: 1.2.0', 'license: MIT', f'version: "{register["engine_version"]}"', REPOSITORY_URL):
        if value not in cff:
            raise ValueError(f'citation metadata mismatch: {value}')
    if 'MIT License' not in (root / 'LICENSE').read_text(encoding='utf-8'):
        raise ValueError('citation license does not match repository')
    if REPOSITORY_URL not in (root / 'llms.txt').read_text(encoding='utf-8'):
        raise ValueError('LLM index repository identity mismatch')
    return {'status': 'PASS', 'claims': count, 'internal_links': links,
            'scope': 'reference and metadata consistency, not assurance or ranking performance'}


if __name__ == '__main__':
    try:
        print(json.dumps(check(), indent=2))
    except (ValueError, KeyError, TypeError, OSError, SyntaxError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        raise SystemExit(1)
