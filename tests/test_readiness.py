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
    def test_all_explicit_statuses_are_preserved(self):
        result = evaluate_readiness(
            FALLBACK_POLICY, {"unit-tests": "PASS", "documentation": "PASS"}
        )
        self.assertTrue(result.ready)
        self.assertEqual(
            [(item.name, item.status, item.source) for item in result.checks],
            [
                ("unit-tests", "PASS", "explicit"),
                ("documentation", "PASS", "explicit"),
            ],
        )

    def test_mixed_explicit_and_fallback_statuses_are_ready(self):
        result = evaluate_readiness(FALLBACK_POLICY, {"unit-tests": "PASS"})
        self.assertTrue(result.ready)
        self.assertEqual(
            [(item.name, item.status, item.source) for item in result.checks],
            [
                ("unit-tests", "PASS", "explicit"),
                ("documentation", "PASS", "fallback"),
            ],
        )

    def test_explicit_failure_overrides_fallback_and_is_not_ready(self):
        result = evaluate_readiness(
            FALLBACK_POLICY, {"unit-tests": "PASS", "documentation": "FAIL"}
        )
        self.assertFalse(result.ready)
        self.assertEqual(result.checks[1].status, "FAIL")
        self.assertEqual(result.checks[1].source, "explicit")

    def test_missing_required_status_is_an_error(self):
        with self.assertRaisesRegex(MissingStatusError, "unit-tests"):
            evaluate_readiness(FALLBACK_POLICY, {"documentation": "PASS"})

    def test_required_check_never_uses_fallback(self):
        policy = ReleasePolicy(
            version=1,
            checks=(CheckPolicy("unit-tests", required=True, fallback="PASS"),),
        )
        with self.assertRaisesRegex(MissingStatusError, "unit-tests"):
            evaluate_readiness(policy, {})

    def test_optional_check_without_fallback_still_requires_status(self):
        with self.assertRaisesRegex(MissingStatusError, "documentation"):
            evaluate_readiness(POLICY, {"unit-tests": "PASS"})


if __name__ == "__main__":
    unittest.main()
