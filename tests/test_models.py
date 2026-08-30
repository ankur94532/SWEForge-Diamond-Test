from __future__ import annotations

import unittest

from src.release_readiness.models import CheckPolicy, CheckResult


class ModelTests(unittest.TestCase):
    def test_check_policy_legacy_construction_defaults_fallback_to_none(self):
        policy = CheckPolicy("unit-tests", required=True)

        self.assertEqual(policy.name, "unit-tests")
        self.assertTrue(policy.required)
        self.assertIsNone(policy.fallback)

    def test_check_policy_stores_explicit_fallback(self):
        policy = CheckPolicy("documentation", required=False, fallback="PASS")

        self.assertEqual(policy.fallback, "PASS")

    def test_check_result_legacy_construction_defaults_source_to_explicit(self):
        result = CheckResult("unit-tests", "PASS")

        self.assertEqual(result.name, "unit-tests")
        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.source, "explicit")

    def test_check_result_stores_explicit_source(self):
        result = CheckResult("documentation", "PASS", source="fallback")

        self.assertEqual(result.source, "fallback")


if __name__ == "__main__":
    unittest.main()
