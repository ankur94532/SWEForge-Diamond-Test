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

FALLBACK_POLICY = ReleasePolicy(
    version=1,
    checks=(
        CheckPolicy("unit-tests", required=True),
        CheckPolicy("documentation", required=False, fallback="PASS"),
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

    def test_missing_status_is_an_error(self):
        with self.assertRaisesRegex(MissingStatusError, "documentation"):
            evaluate_readiness(POLICY, {"unit-tests": "PASS"})

    def test_optional_check_uses_configured_fallback(self):
        result = evaluate_readiness(FALLBACK_POLICY, {"unit-tests": "PASS"})
        self.assertTrue(result.ready)
        self.assertEqual(
            [(item.name, item.status, item.source) for item in result.checks],
            [
                ("unit-tests", "PASS", "explicit"),
                ("documentation", "PASS", "fallback"),
            ],
        )

    def test_explicit_status_overrides_fallback(self):
        result = evaluate_readiness(
            FALLBACK_POLICY, {"unit-tests": "PASS", "documentation": "FAIL"}
        )
        self.assertFalse(result.ready)
        self.assertEqual(
            (result.checks[1].status, result.checks[1].source), ("FAIL", "explicit")
        )

    def test_missing_required_check_is_still_an_error_even_with_fallbacks_nearby(
        self,
    ):
        with self.assertRaisesRegex(MissingStatusError, "unit-tests"):
            evaluate_readiness(FALLBACK_POLICY, {"documentation": "PASS"})

    def test_rejects_unsupported_configured_fallback_value(self):
        invalid_policy = ReleasePolicy(
            version=1,
            checks=(
                CheckPolicy("unit-tests", required=True),
                CheckPolicy("documentation", required=False, fallback="MAYBE"),
            ),
        )
        with self.assertRaisesRegex(ValueError, "unsupported status for documentation"):
            evaluate_readiness(invalid_policy, {"unit-tests": "PASS"})


if __name__ == "__main__":
    unittest.main()
