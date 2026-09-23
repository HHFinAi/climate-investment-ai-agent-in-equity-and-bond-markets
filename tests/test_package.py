import hashlib, importlib.util, json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from climate_agent.workflow import ROOT

def module(name,file):
    spec=importlib.util.spec_from_file_location(name,ROOT/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
publisher=module('publish_github','scripts/publish_github.py')
checker=module('check_repository','scripts/check_repository.py')

class PackageTests(unittest.TestCase):
    def test_package_invariants(self):self.assertEqual(checker.check()['status'],'PASS')
    def test_source_pdf_not_present(self):self.assertFalse(list(ROOT.rglob('*.pdf')))
    def test_source_hash_documented(self):
        x=json.loads((ROOT/'references/source-map.json').read_text());self.assertEqual(len(x['sha256']),64);self.assertEqual(x['pdf_page_count'],897)
    def test_all_ten_chapters_mapped(self):
        x=json.loads((ROOT/'references/source-map.json').read_text());self.assertEqual(len(x['chapters']),10)
    def test_safe_publishing_paths(self):
        for path in ('README.md','agents/00-mandate.md','.github/workflows/validate.yml','VERSION'):
            self.assertTrue(publisher.safe_path(path),path)
    def test_sensitive_publishing_paths_rejected(self):
        for path in ('../outside.md','/outside.md','x\\y.md','CFA Climate.pdf','.env','keys/x.pem','runs/report.md','.git/config','local_sources/chapter.txt','data/private/holdings.csv','x\x00.md'):
            self.assertFalse(publisher.safe_path(path),path)
    def test_only_confirmed_404_means_absent(self):publisher.ensure_target_absent(1,'HTTP/2.0 404 Not Found\n')
    def test_network_and_authorization_not_absence(self):
        for text in ('HTTP/2.0 403 Forbidden','HTTP/2.0 401 Unauthorized','connection failed'):
            with self.assertRaises(publisher.PublishError):publisher.ensure_target_absent(1,text)
    def test_existing_repo_not_overwritten(self):
        with self.assertRaises(publisher.PublishError):publisher.ensure_target_absent(0,'HTTP/2.0 200 OK')
    def test_publisher_without_credentials_stops(self):
        # All subprocess/network activity is prevented; test does not publish anything.
        with patch.object(publisher,'release_files',return_value=['README.md']),patch.object(publisher.shutil,'which',return_value=None):
            with self.assertRaises(publisher.PublishError):publisher.execute(ROOT)
    def test_release_hashes(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t);(r/'README.md').write_text('test\n');sha=hashlib.sha256((r/'README.md').read_bytes()).hexdigest()
            (r/'FILE_MANIFEST.json').write_text(json.dumps({'files':{'README.md':sha}}))
            self.assertEqual(publisher.release_files(r),['README.md','FILE_MANIFEST.json'])
            (r/'README.md').write_text('changed')
            with self.assertRaises(publisher.PublishError):publisher.release_files(r)
    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t);(r/'actual.md').write_text('test');(r/'README.md').symlink_to(r/'actual.md')
            (r/'FILE_MANIFEST.json').write_text(json.dumps({'files':{'README.md':hashlib.sha256(b'test').hexdigest()}}))
            with self.assertRaises(publisher.PublishError):publisher.release_files(r)
    def test_symlink_parent_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t);(r/'actual').mkdir();(r/'actual/x.md').write_text('test');(r/'alias').symlink_to(r/'actual',target_is_directory=True)
            (r/'FILE_MANIFEST.json').write_text(json.dumps({'files':{'alias/x.md':hashlib.sha256(b'test').hexdigest()}}))
            with self.assertRaises(publisher.PublishError):publisher.release_files(r)
