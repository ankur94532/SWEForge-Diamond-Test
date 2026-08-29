from __future__ import annotations

import unittest

from src.release_readiness.models import (
    CheckPolicy,
    CheckResult,
    ReadinessEvaluation,
    ReleasePolicy,
)


class ModelValueObjectTests(unittest.TestCase):
    def test_check_policy_two_argument_form_still_works(self):
        policy = CheckPolicy("unit-tests", required=True)

        self.assertEqual(policy.name, "unit-tests")
        self.assertTrue(policy.required)
        self.assertIsNone(policy.fallback)

    def test_check_policy_supports_optional_fallback(self):
        policy = CheckPolicy("optional-docs", required=False, fallback="PASS")

        self.assertEqual(policy.name, "optional-docs")
        self.assertFalse(policy.required)
        self.assertEqual(policy.fallback, "PASS")

    def test_check_result_two_argument_form_still_works(self):
        result = CheckResult("unit-tests", "PASS")

        self.assertEqual(result.name, "unit-tests")
        self.assertEqual(result.status, "PASS")
        self.assertIsNone(result.source)

    def test_check_result_supports_explicit_source(self):
        result = CheckResult("unit-tests", "PASS", source="explicit")

        self.assertEqual(result.name, "unit-tests")
        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.source, "explicit")

    def test_check_result_supports_fallback_source(self):
        result = CheckResult("optional-docs", "PASS", source="fallback")

        self.assertEqual(result.name, "optional-docs")
        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.source, "fallback")

    def test_release_policy_and_readiness_evaluation_accept_extended_objects(self):
        policy = ReleasePolicy(
            version=1,
            checks=(
                CheckPolicy("unit-tests", required=True),
                CheckPolicy("optional-docs", required=False, fallback="PASS"),
            ),
        )
        evaluation = ReadinessEvaluation(
            ready=True,
            checks=(
                CheckResult("unit-tests", "PASS", source="explicit"),
                CheckResult("optional-docs", "PASS", source="fallback"),
            ),
        )

        self.assertEqual(policy.checks[1].fallback, "PASS")
        self.assertEqual(evaluation.checks[0].source, "explicit")
        self.assertEqual(evaluation.checks[1].source, "fallback")


if __name__ == "__main__":
    unittest.main()
