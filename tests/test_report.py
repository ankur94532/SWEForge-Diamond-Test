from __future__ import annotations

import unittest

from src.release_readiness.models import CheckResult, ReadinessEvaluation
from src.release_readiness.report import build_report


class ReportTests(unittest.TestCase):
    def test_preserves_public_shape_with_explicit_source(self):
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
                        "source": "explicit",
                    }
                ],
            },
        )

    def test_reports_fallback_source_in_declaration_order(self):
        report = build_report(
            ReadinessEvaluation(
                ready=False,
                checks=(
                    CheckResult("unit-tests", "PASS", source="explicit"),
                    CheckResult("documentation", "FAIL", source="fallback"),
                ),
            )
        )

        self.assertEqual(
            report,
            {
                "ready": False,
                "checks": [
                    {
                        "name": "unit-tests",
                        "status": "PASS",
                        "source": "explicit",
                    },
                    {
                        "name": "documentation",
                        "status": "FAIL",
                        "source": "fallback",
                    },
                ],
            },
        )


if __name__ == "__main__":
    unittest.main()
