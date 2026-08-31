from __future__ import annotations

import unittest

from src.release_readiness.models import CheckPolicy, ReleasePolicy
from src.release_readiness.readiness import MissingStatusError, evaluate_readiness


POLICY = ReleasePolicy(
    version=1,
    checks=(
        CheckPolicy("unit-tests", required=True),
        CheckPolicy("documentation", required=False),
    ),
)


class ReadinessTests(unittest.TestCase):
    def test_all_explicit_pass_is_ready(self):
        result = evaluate_readiness(
            POLICY, {"unit-tests": "PASS", "documentation": "PASS"}
        )
        self.assertTrue(result.ready)

    def test_explicit_failure_is_not_ready(self):
        result = evaluate_readiness(
            POLICY, {"unit-tests": "PASS", "documentation": "FAIL"}
        )
        self.assertFalse(result.ready)

    def test_evaluation_tracks_policy_version(self):
        result = evaluate_readiness(
            POLICY, {"unit-tests": "PASS", "documentation": "PASS"}
        )
        self.assertEqual(result.policy_version, 1)

    def test_missing_status_is_an_error(self):
        with self.assertRaisesRegex(MissingStatusError, "documentation"):
            evaluate_readiness(POLICY, {"unit-tests": "PASS"})


if __name__ == "__main__":
    unittest.main()
