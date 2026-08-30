from __future__ import annotations

import unittest

from src.release_readiness.models import CheckResult, ReadinessEvaluation
from src.release_readiness.report import build_report


class ReportTests(unittest.TestCase):
    def test_all_explicit_report_includes_source(self):
        report = build_report(
            ReadinessEvaluation(
                ready=True,
                checks=(
                    CheckResult("unit-tests", "PASS", source="explicit"),
                    CheckResult("documentation", "PASS", source="explicit"),
                ),
            )
        )

        self.assertEqual(
            report,
            {
                "ready": True,
                "checks": [
                    {"name": "unit-tests", "status": "PASS", "source": "explicit"},
                    {"name": "documentation", "status": "PASS", "source": "explicit"},
                ],
            },
        )

    def test_mixed_explicit_and_fallback_report_includes_source(self):
        report = build_report(
            ReadinessEvaluation(
                ready=True,
                checks=(
                    CheckResult("unit-tests", "PASS", source="explicit"),
                    CheckResult("documentation", "PASS", source="fallback"),
                ),
            )
        )

        self.assertEqual(
            report,
            {
                "ready": True,
                "checks": [
                    {"name": "unit-tests", "status": "PASS", "source": "explicit"},
                    {"name": "documentation", "status": "PASS", "source": "fallback"},
                ],
            },
        )


if __name__ == "__main__":
    unittest.main()
