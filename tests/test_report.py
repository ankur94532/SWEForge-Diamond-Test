from __future__ import annotations

import unittest

from src.release_readiness.models import (
    CheckPolicy,
    CheckResult,
    ReadinessEvaluation,
    ReleasePolicy,
)
from src.release_readiness.readiness import MissingStatusError, evaluate_readiness
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
                    {"name": "unit-tests", "status": "PASS", "source": "explicit"}
                ],
            },
        )

    def test_all_explicit_input_marks_every_check_explicit(self):
        report = build_report(
            ReadinessEvaluation(
                ready=False,
                checks=(
                    CheckResult("unit-tests", "PASS", source="explicit"),
                    CheckResult("documentation", "FAIL", source="explicit"),
                ),
            )
        )
        self.assertEqual(
            report["checks"],
            [
                {"name": "unit-tests", "status": "PASS", "source": "explicit"},
                {"name": "documentation", "status": "FAIL", "source": "explicit"},
            ],
        )

    def test_mixed_explicit_and_fallback_input_distinguishes_source(self):
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
            report["checks"],
            [
                {"name": "unit-tests", "status": "PASS", "source": "explicit"},
                {"name": "documentation", "status": "PASS", "source": "fallback"},
            ],
        )

    def test_missing_required_input_never_produces_a_report(self):
        policy = ReleasePolicy(
            version=1,
            checks=(
                CheckPolicy("unit-tests", required=True),
                CheckPolicy("documentation", required=False, fallback="PASS"),
            ),
        )
        with self.assertRaisesRegex(MissingStatusError, "unit-tests"):
            build_report(evaluate_readiness(policy, {"documentation": "PASS"}))

    def test_invalid_fallback_configuration_never_produces_a_report(self):
        policy = ReleasePolicy(
            version=1,
            checks=(
                CheckPolicy("unit-tests", required=True),
                CheckPolicy("documentation", required=False, fallback="MAYBE"),
            ),
        )
        with self.assertRaisesRegex(
            ValueError, "unsupported status for documentation"
        ):
            build_report(evaluate_readiness(policy, {"unit-tests": "PASS"}))


if __name__ == "__main__":
    unittest.main()
