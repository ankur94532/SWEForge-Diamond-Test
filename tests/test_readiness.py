from __future__ import annotations

import unittest

from src.release_readiness.models import CheckPolicy, ReleasePolicy
from src.release_readiness.readiness import MissingStatusError, evaluate_readiness


POLICY = ReleasePolicy(
    version=1,
    checks=(
        CheckPolicy("unit-tests", required=True),
        CheckPolicy("documentation", required=False, fallback="PASS"),
    ),
)

NO_FALLBACK_POLICY = ReleasePolicy(
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
        self.assertEqual(
            [(item.name, item.status, item.source) for item in result.checks],
            [
                ("unit-tests", "PASS", "explicit"),
                ("documentation", "PASS", "explicit"),
            ],
        )

    def test_explicit_failure_is_not_ready(self):
        result = evaluate_readiness(
            POLICY, {"unit-tests": "PASS", "documentation": "FAIL"}
        )

        self.assertFalse(result.ready)
        self.assertEqual(result.checks[1].source, "explicit")

    def test_missing_optional_uses_fallback(self):
        result = evaluate_readiness(POLICY, {"unit-tests": "PASS"})

        self.assertTrue(result.ready)
        self.assertEqual(
            [(item.name, item.status, item.source) for item in result.checks],
            [
                ("unit-tests", "PASS", "explicit"),
                ("documentation", "PASS", "fallback"),
            ],
        )

    def test_fallback_failure_is_not_ready(self):
        policy = ReleasePolicy(
            version=1,
            checks=(
                CheckPolicy("unit-tests", required=True),
                CheckPolicy("documentation", required=False, fallback="FAIL"),
            ),
        )

        result = evaluate_readiness(policy, {"unit-tests": "PASS"})

        self.assertFalse(result.ready)
        self.assertEqual(result.checks[1].source, "fallback")
        self.assertEqual(result.checks[1].status, "FAIL")

    def test_missing_required_status_is_an_error(self):
        with self.assertRaisesRegex(MissingStatusError, "unit-tests"):
            evaluate_readiness(POLICY, {"documentation": "PASS"})

    def test_missing_optional_without_fallback_is_an_error(self):
        with self.assertRaisesRegex(MissingStatusError, "documentation"):
            evaluate_readiness(NO_FALLBACK_POLICY, {"unit-tests": "PASS"})

    def test_unsupported_explicit_status_is_an_error(self):
        with self.assertRaisesRegex(ValueError, "unsupported status for documentation: SKIP"):
            evaluate_readiness(
                POLICY, {"unit-tests": "PASS", "documentation": "SKIP"}
            )

    def test_unsupported_fallback_status_is_an_error(self):
        invalid_policy = ReleasePolicy(
            version=1,
            checks=(
                CheckPolicy("unit-tests", required=True),
                CheckPolicy("documentation", required=False, fallback="SKIP"),
            ),
        )

        with self.assertRaisesRegex(ValueError, "unsupported status for documentation: SKIP"):
            evaluate_readiness(invalid_policy, {"unit-tests": "PASS"})


if __name__ == "__main__":
    unittest.main()
