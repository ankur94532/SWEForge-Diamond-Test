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
                "checks": [{"name": "unit-tests", "status": "PASS"}],
                "status_counts": {"PASS": 1, "FAIL": 0},
                "total_checks": 1,
            },
        )

    def test_summarizes_status_counts(self):
        report = build_report(
            ReadinessEvaluation(
                ready=False,
                checks=(
                    CheckResult("unit-tests", "PASS"),
                    CheckResult("lint", "FAIL"),
                    CheckResult("integration", "PASS"),
                ),
            )
        )

        self.assertEqual(report["ready"], False)
        self.assertEqual(
            report["checks"],
            [
                {"name": "unit-tests", "status": "PASS"},
                {"name": "lint", "status": "FAIL"},
                {"name": "integration", "status": "PASS"},
            ],
        )
        self.assertEqual(report["status_counts"], {"PASS": 2, "FAIL": 1})
        self.assertEqual(report["total_checks"], 3)


if __name__ == "__main__":
    unittest.main()
