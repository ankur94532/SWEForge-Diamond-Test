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
                "checks": [
                    {
                        "name": "unit-tests",
                        "status": "PASS",
                        "severity": "blocker",
                    }
                ],
                "severity_counts": {"blocker": 1, "advisory": 0},
            },
        )

    def test_counts_each_check_by_severity(self):
        report = build_report(
            ReadinessEvaluation(
                ready=False,
                checks=(
                    CheckResult("unit-tests", "FAIL"),
                    CheckResult("documentation", "FAIL", severity="advisory"),
                    CheckResult("security", "PASS", severity="advisory"),
                ),
            )
        )
        self.assertEqual(report["severity_counts"], {"blocker": 1, "advisory": 2})
        self.assertEqual(list(report), ["ready", "checks", "severity_counts"])


if __name__ == "__main__":
    unittest.main()
