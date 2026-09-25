import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('build_site', ROOT / 'scripts/build_site.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class SiteAssetsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = build.build_payload()

    def test_lazy_assets_preserve_content_and_search(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'data.js'
            build.write_site_data(self.payload, output)
            catalog = json.loads(output.read_text().split('window.PAPERNOTE_DATA=')[1].rstrip(';\n'))
            self.assertNotIn('institutions', catalog['academic'])
            graph = json.loads((Path(temp) / catalog['assets']['academic']).read_text())
            self.assertEqual(graph['institutions'], self.payload['academic']['institutions'])
            originals = {paper['id']: paper for paper in self.payload['papers']}
            for paper in catalog['papers']:
                details = json.loads((Path(temp) / paper['details_url']).read_text())
                self.assertEqual(details, originals[paper['id']]['details'])
                text = json.loads((Path(temp) / catalog['assets']['search'][paper['week']]).read_text())
                self.assertEqual(json.loads(text[paper['id']]), originals[paper['id']])
            full_size = len(json.dumps(self.payload, ensure_ascii=False, separators=(',', ':')).encode())
            self.assertLess(output.stat().st_size, full_size * .5)

    def test_content_hash_changes_only_for_changed_details(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'data.js'
            build.write_site_data(self.payload, output)
            before = {p.name for p in (Path(temp) / 'data').glob('paper-*.json')}
            updated = copy.deepcopy(self.payload)
            updated['papers'][0]['details']['method'] += ' 新版正文。'
            build.write_site_data(updated, output)
            after = {p.name for p in (Path(temp) / 'data').glob('paper-*.json')}
            self.assertEqual(len(after - before), 1)
            self.assertEqual(updated['papers'][1]['details'], self.payload['papers'][1]['details'])


if __name__ == '__main__':
    unittest.main()
