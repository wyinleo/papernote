import copy
import itertools
import unittest
from test_site_assets import build


class InstitutionGroupingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = build.load_json(build.ENTITY_REGISTRY_PATH)
        cls.payload = build.build_payload()

    def test_aggregation_deduplicates_papers_and_internal_edges(self):
        roots = build.institution_roots(self.registry)
        flat = copy.deepcopy(self.registry)
        for item in flat['institutions'].values():
            item.pop('parent_id', None)
            item.pop('parent_source', None)
        original = build.build_academic_graph(self.payload['papers'], flat)
        grouped = self.payload['academic']
        expected = {}
        for item in original['institutions']:
            expected.setdefault(roots[item['id']]['id'], set()).update(item['papers'])
        for item in grouped['institutions']:
            self.assertEqual(set(item['papers']), expected[item['id']])
            scored = {p['id'] for p in grouped['publications'] if item['id'] in p['institutions'] and p['venue_group']}
            self.assertEqual(item['verified_score'], len(scored))
        expected_edges = {}
        for paper in original['publications']:
            parent_ids = {roots[i]['id'] for i in paper['institutions']}
            for pair in itertools.combinations(sorted(parent_ids), 2):
                expected_edges.setdefault(pair, set()).add(paper['id'])
        actual_edges = {(e['source'], e['target']): {p['id'] for p in e['papers']} for e in grouped['collaborations']}
        self.assertEqual(actual_edges, expected_edges)
        self.assertTrue(all(a != b for a, b in actual_edges))
        self.assertEqual(len(grouped['institutions']), len(expected))
        self.assertLess(len(grouped['institutions']), len(original['institutions']))
        self.assertTrue(any('北京信息科学' in name for i in grouped['institutions'] if i['id'] == 'tsinghua-university' for name in i['affiliation_names']))

    def test_rejects_cycles_and_missing_evidence(self):
        registry = {'institutions': {
            'a': {'id': 'a', 'parent_id': 'b', 'country_code': 'CHN', 'parent_source': 'https://example.edu/'},
            'b': {'id': 'b', 'parent_id': 'a', 'country_code': 'CHN', 'parent_source': 'https://example.edu/'},
        }}
        with self.assertRaises(ValueError):
            build.institution_roots(registry)
        registry['institutions']['b'].pop('parent_id')
        registry['institutions']['a'].pop('parent_source')
        with self.assertRaises(ValueError):
            build.institution_roots(registry)
