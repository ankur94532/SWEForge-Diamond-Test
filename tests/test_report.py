from __future__ import annotations

import unittest

from src.release_readiness.models import CheckResult, ReadinessEvaluation
from src.release_readiness.report import build_report


class ReportTests(unittest.TestCase):
    def test_preserves_existing_keys_and_defaults_source_to_explicit(self):
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
                "summary": {"total": 1, "passed": 1, "failed": 0},
                "failed_checks": [],
                "checks": [
                    {
                        "name": "unit-tests",
                        "status": "PASS",
                        "source": "explicit",
                    }
                ],
            },
        )

    def test_summarizes_failures_and_preserves_declaration_order(self):
        report = build_report(
            ReadinessEvaluation(
                ready=False,
                checks=(
                    CheckResult("unit-tests", "FAIL", source="explicit"),
                    CheckResult("documentation", "PASS", source="fallback"),
                    CheckResult("security", "FAIL", source="fallback"),
                ),
            )
        )
        self.assertEqual(
            report,
            {
                "ready": False,
                "summary": {"total": 3, "passed": 1, "failed": 2},
                "failed_checks": ["unit-tests", "security"],
                "checks": [
                    {
                        "name": "unit-tests",
                        "status": "FAIL",
                        "source": "explicit",
                    },
                    {
                        "name": "documentation",
                        "status": "PASS",
                        "source": "fallback",
                    },
                    {
                        "name": "security",
                        "status": "FAIL",
                        "source": "fallback",
                    },
                ],
            },
        )


if __name__ == "__main__":
    unittest.main()
