from __future__ import annotations

import unittest

from src.release_readiness.models import CheckPolicy, ReleasePolicy
from src.release_readiness.readiness import MissingStatusError, evaluate_readiness


POLICY_WITHOUT_FALLBACK = ReleasePolicy(
    version=1,
    checks=(
        CheckPolicy("unit-tests", required=True),
        CheckPolicy("documentation", required=False),
    ),
)

POLICY_WITH_FALLBACK = ReleasePolicy(
    version=1,
    checks=(
        CheckPolicy("unit-tests", required=True),
        CheckPolicy("documentation", required=False, fallback="PASS"),
    ),
)

POLICY_WITH_FAIL_FALLBACK = ReleasePolicy(
    version=1,
    checks=(
        CheckPolicy("unit-tests", required=True),
        CheckPolicy("documentation", required=False, fallback="FAIL"),
    ),
)


class ReadinessTests(unittest.TestCase):
    def test_all_explicit_pass_is_ready(self):
        result = evaluate_readiness(
            POLICY_WITH_FALLBACK, {"unit-tests": "PASS", "documentation": "PASS"}
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
            POLICY_WITH_FALLBACK, {"unit-tests": "PASS", "documentation": "FAIL"}
        )

        self.assertFalse(result.ready)
        self.assertEqual(result.checks[1].source, "explicit")

    def test_missing_optional_uses_fallback(self):
        result = evaluate_readiness(POLICY_WITH_FALLBACK, {"unit-tests": "PASS"})

        self.assertTrue(result.ready)
        self.assertEqual(
            [(item.name, item.status, item.source) for item in result.checks],
            [
                ("unit-tests", "PASS", "explicit"),
                ("documentation", "PASS", "fallback"),
            ],
        )

    def test_missing_required_status_is_an_error(self):
        with self.assertRaisesRegex(MissingStatusError, "unit-tests"):
            evaluate_readiness(POLICY_WITH_FALLBACK, {"documentation": "PASS"})

    def test_missing_optional_without_fallback_is_an_error(self):
        with self.assertRaisesRegex(MissingStatusError, "documentation"):
            evaluate_readiness(POLICY_WITHOUT_FALLBACK, {"unit-tests": "PASS"})

    def test_unknown_status_key_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unknown checks"):
            evaluate_readiness(
                POLICY_WITH_FALLBACK,
                {"unit-tests": "PASS", "documentation": "PASS", "extra": "PASS"},
            )

    def test_unsupported_explicit_status_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsupported status"):
            evaluate_readiness(
                POLICY_WITH_FALLBACK,
                {"unit-tests": "PASS", "documentation": "UNKNOWN"},
            )

    def test_fallback_fail_makes_not_ready(self):
        result = evaluate_readiness(POLICY_WITH_FAIL_FALLBACK, {"unit-tests": "PASS"})

        self.assertFalse(result.ready)
        self.assertEqual(result.checks[1].source, "fallback")
        self.assertEqual(result.checks[1].status, "FAIL")


if __name__ == "__main__":
    unittest.main()
