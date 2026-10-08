import unittest

from test_site_assets import build


class VenueSeriesTest(unittest.TestCase):
    def test_ccf_a_series_aliases_and_tracks_are_collapsed(self):
        cases = {
            "ACM CCS 2025": "CCS",
            "CCS 2025": "CCS",
            "NeurIPS 2025": "NeurIPS",
            "NeurIPS 2025 Datasets and Benchmarks": "NeurIPS",
            "Second Workshop on Agents in the Wild: Safety, Security, and Beyond (NeurIPS 2026)": "NeurIPS",
            "IEEE Symposium on Security and Privacy 2026": "IEEE S&P",
            "USENIX Security 2026": "USENIX Security",
        }
        for venue, expected in cases.items():
            with self.subTest(venue=venue):
                self.assertEqual(build.venue_series_name([venue]), expected)

    def test_non_grouped_sources_keep_their_name_without_year(self):
        self.assertEqual(build.venue_series_name(["IEEE HOST 2026"]), "IEEE HOST")
        self.assertEqual(build.venue_series_name(["arXiv"]), "arXiv")
        self.assertEqual(build.venue_series_name([]), "其他 / 未标注")

    def test_payload_uses_one_neurips_and_ccs_label(self):
        payload = build.build_payload()
        labels = {
            paper["id"]: paper["venue_series"]
            for paper in payload["papers"]
        }
        self.assertEqual(labels["neurips25-zou-agent-red-team-competition"], "NeurIPS")
        self.assertEqual(labels["neurips25-nie-secodeplt"], "NeurIPS")
        self.assertEqual(labels["neurips25-aichberger-mip-agent"], "NeurIPS")
        self.assertEqual(labels["arxiv-2607-18063-adaptive-adversaries"], "NeurIPS")
        self.assertEqual(labels["ccs25-hao-syzspec"], "CCS")


if __name__ == "__main__":
    unittest.main()
