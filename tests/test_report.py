from __future__ import annotations

import unittest

from src.release_readiness.models import CheckResult, ReadinessEvaluation
from src.release_readiness.report import build_report


class ReportTests(unittest.TestCase):
    def test_preserves_public_shape(self):
        report = build_report(
            ReadinessEvaluation(
                ready=True,
                checks=(CheckResult("unit-tests", "PASS"),),
            )
        )
        self.assertEqual(
            report,
            {
                "ready": True,
                "summary": {
                    "total": 1,
                    "passed": 1,
                    "failed": 0,
                    "failed_names": [],
                },
                "checks": [{"name": "unit-tests", "status": "PASS"}],
            },
        )

    def test_summary_counts_all_passing_checks(self):
        report = build_report(
            ReadinessEvaluation(
                ready=True,
                checks=(
                    CheckResult("unit-tests", "PASS"),
                    CheckResult("security-scan", "PASS"),
                    CheckResult("documentation", "PASS"),
                ),
            )
        )

        self.assertEqual(
            report["summary"],
            {"total": 3, "passed": 3, "failed": 0, "failed_names": []},
        )
        self.assertEqual(
            report["checks"],
            [
                {"name": "unit-tests", "status": "PASS"},
                {"name": "security-scan", "status": "PASS"},
                {"name": "documentation", "status": "PASS"},
            ],
        )

    def test_summary_counts_mixed_results(self):
        report = build_report(
            ReadinessEvaluation(
                ready=False,
                checks=(
                    CheckResult("unit-tests", "PASS"),
                    CheckResult("security-scan", "FAIL"),
                    CheckResult("documentation", "PASS"),
                ),
            )
        )

        self.assertEqual(report["ready"], False)
        self.assertEqual(
            report["summary"],
            {
                "total": 3,
                "passed": 2,
                "failed": 1,
                "failed_names": ["security-scan"],
            },
        )
        self.assertEqual(
            report["checks"],
            [
                {"name": "unit-tests", "status": "PASS"},
                {"name": "security-scan", "status": "FAIL"},
                {"name": "documentation", "status": "PASS"},
            ],
        )

    def test_summary_lists_failed_names_in_declaration_order(self):
        report = build_report(
            ReadinessEvaluation(
                ready=False,
                checks=(
                    CheckResult("unit-tests", "FAIL"),
                    CheckResult("security-scan", "PASS"),
                    CheckResult("documentation", "FAIL"),
                ),
            )
        )

        self.assertEqual(
            report["summary"]["failed_names"],
            ["unit-tests", "documentation"],
        )


if __name__ == "__main__":
    unittest.main()
