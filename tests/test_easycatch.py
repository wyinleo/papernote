import copy
import unittest
from test_site_assets import build


class EasycatchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = build.build_payload()
        cls.entries = build.load_json(build.EASYCATCH_PATH)['papers']

    def test_every_paper_has_complete_lazy_explanation(self):
        self.assertEqual(set(self.entries), {p['id'] for p in self.payload['papers']})
        for paper in self.payload['papers']:
            with self.subTest(paper=paper['id']):
                paragraphs = paper['details']['easycatch']
                self.assertEqual(len(paragraphs), 2)
                self.assertTrue(all(p.strip() for p in paragraphs))
                self.assertEqual(paragraphs, self.entries[paper['id']]['paragraphs'])

    def test_missing_or_empty_explanation_fails_build_validation(self):
        paper = self.payload['papers'][0]
        with self.assertRaisesRegex(ValueError, 'missing Easycatch'):
            build.validated_easycatch(paper['id'], paper['details'], {})
        entries = copy.deepcopy(self.entries)
        entries[paper['id']]['paragraphs'][1] = ' '
        with self.assertRaisesRegex(ValueError, 'two nonempty paragraphs'):
            build.validated_easycatch(paper['id'], paper['details'], entries)

    def test_changed_source_requires_review_but_unrelated_metadata_does_not(self):
        paper = self.payload['papers'][0]
        for field in build.EASYCATCH_SOURCE_FIELDS:
            with self.subTest(field=field):
                changed = {**paper['details'], field: paper['details'][field] + ' 新证据'}
                with self.assertRaisesRegex(ValueError, 'stale Easycatch'):
                    build.validated_easycatch(paper['id'], changed, self.entries)
        changed = {**paper['details'], 'public_date': '2027-01-01 正式发表'}
        self.assertEqual(build.validated_easycatch(paper['id'], changed, self.entries),
                         paper['details']['easycatch'])


if __name__ == '__main__':
    unittest.main()
