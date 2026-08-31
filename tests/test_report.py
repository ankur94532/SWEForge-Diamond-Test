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
                "check_count": 1,
            },
        )

    def test_reports_check_count(self):
        report = build_report(
            ReadinessEvaluation(
                ready=False,
                checks=(
                    CheckResult("unit-tests", "PASS"),
                    CheckResult("documentation", "FAIL"),
                ),
            )
        )
        self.assertEqual(report["check_count"], 2)


if __name__ == "__main__":
    unittest.main()
