"""App checks. Run from the repo root: python -m unittest app.test_app

Pages must load without an exception. Package totals must match measures/package_summary.csv
when the chosen rows are ticked. No number is typed in as an expected result: the test reads
the same files the app reads.
"""
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _open(at, url_path: str):
    """Open a st.navigation page registered as a callable (no separate script file)."""
    for page_hash, info in at._registered_pages.items():
        if info.get("url_pathname") == url_path:
            at._page_hash = page_hash
            return at.run()
    known = [info.get("url_pathname") for info in at._registered_pages.values()]
    raise AssertionError(f"no page {url_path!r}; known: {known}")


class DataTests(unittest.TestCase):
    def test_aligned_baseline_keeps_cost_and_splits_co2(self):
        from app import data

        frame = data.aligned_baseline()
        totals = data.energy_totals()
        self.assertAlmostEqual(frame["cost_chf_alloc"].sum(), totals["cost_chf"], places=1)
        self.assertAlmostEqual(frame["co2_alloc_mid"].sum(), totals["co2_mid"], places=1)
        # Test-account cost moves to IT; it must not remain its own department.
        self.assertNotIn("Test account", set(frame["dept_allocated"]))

    def test_chosen_package_matches_summary_file(self):
        from app import data

        rows = data.package_rows()
        self.assertIsNotNone(rows)
        self.assertTrue(bool(rows["files_agree"].iloc[0]))
        chosen = rows[rows["chosen"]]
        summary = data.package_summary()
        for level, key in (("low", "co2_pct_low"), ("mid", "co2_pct_mid"), ("high", "co2_pct_high")):
            result = data.package_result(chosen, level)
            self.assertAlmostEqual(result["co2_pct"], float(summary[key]), places=1)
        mid = data.package_result(chosen, "mid")
        self.assertAlmostEqual(mid["cost_pct"], float(summary["chf_pct"]), places=1)
        self.assertAlmostEqual(mid["pd"], float(summary["effort_pd"]), places=1)
        self.assertAlmostEqual(mid["co2_kg"], float(summary["co2_mid"]), places=0)

    def test_turning_candidates_on_changes_the_co2_total(self):
        from app import data

        rows = data.package_rows()
        chosen = rows[rows["chosen"]]
        with_candidates = rows
        base = data.package_result(chosen, "mid")["co2_kg"]
        both = data.package_result(with_candidates, "mid")["co2_kg"]
        self.assertGreater(both, base)
        self.assertIn("C1", set(rows["measure_id"]))
        self.assertIn("C2", set(rows["measure_id"]))

    def test_headline_uses_the_country_sum(self):
        from app import data

        facts = data.overview_facts("mid")
        country = data.impact_by("country", "co2", "mid")
        top = country.iloc[0]
        self.assertEqual(facts["top_country"], top["label"])
        self.assertAlmostEqual(facts["top_country_share"], float(top["share"]), places=4)
        self.assertAlmostEqual(facts["co2_mid"], country["amount"].sum(), places=1)


class PageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from streamlit.testing.v1 import AppTest

        cls.at = AppTest.from_file(str(ROOT / "app" / "app.py"), default_timeout=120).run()

    def test_overview_loads(self):
        page = _open(self.at, "")
        self.assertFalse(page.exception, page.exception)
        self.assertIn("Overall picture", [t.value for t in page.title])

    def test_package_loads(self):
        page = _open(self.at, "package")
        self.assertFalse(page.exception, page.exception)
        self.assertIn("Measures package", [t.value for t in page.title])

    def test_findings_and_human_still_load(self):
        findings = _open(self.at, "findings")
        self.assertFalse(findings.exception, findings.exception)
        human = _open(findings, "needs-a-human")
        self.assertFalse(human.exception, human.exception)


if __name__ == "__main__":
    unittest.main()
