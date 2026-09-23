"""Regression checks for documentation claims; no network or external assurance."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('documentation_checker', ROOT / 'scripts/check_documentation.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class DocumentationTests(unittest.TestCase):
    def setUp(self):
        self.register = json.loads((ROOT / 'docs/claims.json').read_text())

    def test_documentation_invariants(self):
        self.assertEqual(checker.check()['status'], 'PASS')

    def test_nine_resolvable_claims(self):
        self.assertEqual(checker.validate_claims(ROOT, self.register), 9)

    def test_no_independent_certification(self):
        self.register['independent_certification'] = True
        with self.assertRaises(ValueError):
            checker.validate_claims(ROOT, self.register)

    def test_missing_implementation_symbol_rejected(self):
        self.register['claims'][0]['implementation']['symbol'] = 'nonexistent_function'
        with self.assertRaises(ValueError):
            checker.validate_claims(ROOT, self.register)

    def test_missing_test_symbol_rejected(self):
        self.register['claims'][0]['tests']['symbols'] = ['test_nonexistent']
        with self.assertRaises(ValueError):
            checker.validate_claims(ROOT, self.register)

    def test_duplicate_claim_rejected(self):
        self.register['claims'].append(copy.deepcopy(self.register['claims'][0]))
        with self.assertRaises(ValueError):
            checker.validate_claims(ROOT, self.register)

    def test_empty_boundary_rejected(self):
        self.register['claims'][0]['boundary'] = ''
        with self.assertRaises(ValueError):
            checker.validate_claims(ROOT, self.register)

    def test_missing_reference_file_rejected(self):
        self.register['claims'][0]['implementation']['path'] = 'absent.py'
        with self.assertRaises(ValueError):
            checker.validate_claims(ROOT, self.register)

    def test_outside_repository_reference_rejected(self):
        with self.assertRaises(ValueError):
            checker.local_path(ROOT, '../outside.py')

    def test_broken_internal_link_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            doc = root / 'README.md'
            doc.write_text('[missing](missing.md)')
            with self.assertRaises(ValueError):
                checker.validate_links(root, [doc])

    def test_broken_heading_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            doc = root / 'README.md'
            doc.write_text('# Real heading\n[wrong](#absent)')
            with self.assertRaises(ValueError):
                checker.validate_links(root, [doc])

    def test_valid_heading_and_offline_external_skip(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            doc = root / 'README.md'
            doc.write_text('# Audit trail\n[local](#audit-trail)\n[external](https://example.org)')
            self.assertEqual(checker.validate_links(root, [doc]), 1)
