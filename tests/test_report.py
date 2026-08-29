from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.release_readiness.config_loader import load_policy
from src.release_readiness.models import CheckPolicy, CheckResult, ReadinessEvaluation, ReleasePolicy
from src.release_readiness.readiness import MissingStatusError, evaluate_readiness
from src.release_readiness.report import build_report


class ReportTests(unittest.TestCase):
    def write_policy(self, document: object) -> Path:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as file:
            json.dump(document, file)
            return Path(file.name)

    def test_preserves_public_shape_without_source(self):
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
            },
        )

    def test_includes_source_for_all_explicit_results(self):
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
            report,
            {
                "ready": False,
                "checks": [
                    {"name": "unit-tests", "status": "PASS", "source": "explicit"},
                    {"name": "documentation", "status": "FAIL", "source": "explicit"},
                ],
            },
        )

    def test_includes_source_for_mixed_explicit_and_fallback_results(self):
        policy = ReleasePolicy(
            version=1,
            checks=(
                CheckPolicy("unit-tests", required=True),
                CheckPolicy("documentation", required=False, fallback="PASS"),
            ),
        )

        report = build_report(evaluate_readiness(policy, {"unit-tests": "PASS"}))

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

    def test_missing_required_input_still_fails_before_report_build(self):
        policy = ReleasePolicy(
            version=1,
            checks=(
                CheckPolicy("unit-tests", required=True),
                CheckPolicy("documentation", required=False, fallback="PASS"),
            ),
        )

        with self.assertRaisesRegex(MissingStatusError, "unit-tests"):
            evaluate_readiness(policy, {"documentation": "PASS"})

    def test_invalid_fallback_configuration_still_fails_clearly(self):
        path = self.write_policy(
            {
                "version": 1,
                "checks": [
                    {"name": "documentation", "required": False, "fallback": "UNKNOWN"}
                ],
            }
        )
        try:
            with self.assertRaisesRegex(ValueError, "unsupported fallback"):
                load_policy(path)
        finally:
            path.unlink()


if __name__ == "__main__":
    unittest.main()
