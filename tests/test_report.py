from __future__ import annotations

import unittest

from src.release_readiness.models import CheckPolicy, CheckResult, ReadinessEvaluation, ReleasePolicy
from src.release_readiness.readiness import evaluate_readiness
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
                "source_path": "",
            },
        )

    def test_includes_policy_source_path_after_existing_fields(self):
        policy = ReleasePolicy(
            version=1,
            checks=(CheckPolicy("unit-tests", required=True),),
            source_path="config/release-policy.json",
        )
        report = build_report(evaluate_readiness(policy, {"unit-tests": "PASS"}))

        self.assertEqual(report["source_path"], "config/release-policy.json")
        self.assertEqual(list(report), ["ready", "checks", "source_path"])


if __name__ == "__main__":
    unittest.main()
