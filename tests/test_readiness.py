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
            FALLBACK_POLICY, {"unit-tests": "PASS", "documentation": "PASS"}
        )

        self.assertTrue(result.ready)
        self.assertTrue(all(item.source == "explicit" for item in result.checks))

    def test_all_explicit_input_preserves_statuses_and_sources(self):
        result = evaluate_readiness(
            FALLBACK_POLICY, {"unit-tests": "PASS", "documentation": "FAIL"}
        )

        self.assertFalse(result.ready)
        self.assertEqual(
            [(item.name, item.status, item.source) for item in result.checks],
            [
                ("unit-tests", "PASS", "explicit"),
                ("documentation", "FAIL", "explicit"),
            ],
        )

    def test_mixed_explicit_and_fallback_input_is_ready(self):
        result = evaluate_readiness(FALLBACK_POLICY, {"unit-tests": "PASS"})

        self.assertTrue(result.ready)
        self.assertEqual(
            [(item.name, item.status, item.source) for item in result.checks],
            [
                ("unit-tests", "PASS", "explicit"),
                ("documentation", "PASS", "fallback"),
            ],
        )

    def test_failing_fallback_makes_evaluation_not_ready(self):
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

    def test_missing_required_status_is_an_error(self):
        with self.assertRaisesRegex(MissingStatusError, "unit-tests"):
            evaluate_readiness(FALLBACK_POLICY, {"documentation": "PASS"})

    def test_optional_status_without_fallback_is_still_an_error(self):
        with self.assertRaisesRegex(MissingStatusError, "documentation"):
            evaluate_readiness(POLICY, {"unit-tests": "PASS"})

    def test_required_check_never_uses_fallback(self):
        policy = ReleasePolicy(
            version=1,
            checks=(CheckPolicy("unit-tests", required=True, fallback="PASS"),),
        )

        with self.assertRaisesRegex(MissingStatusError, "unit-tests"):
            evaluate_readiness(policy, {})

    def test_rejects_unsupported_explicit_or_fallback_status(self):
        invalid_fallback = ReleasePolicy(
            version=1,
            checks=(
                CheckPolicy(
                    "documentation", required=False, fallback="UNKNOWN"
                ),
            ),
        )
        cases = (
            (POLICY, {"unit-tests": "PASS", "documentation": "UNKNOWN"}),
            (invalid_fallback, {}),
        )

        for policy, statuses in cases:
            with self.subTest(statuses=statuses):
                with self.assertRaisesRegex(ValueError, "unsupported status"):
                    evaluate_readiness(policy, statuses)

    def test_rejects_statuses_for_checks_outside_policy(self):
        with self.assertRaisesRegex(ValueError, "unknown checks: release-notes"):
            evaluate_readiness(
                FALLBACK_POLICY,
                {
                    "unit-tests": "PASS",
                    "documentation": "PASS",
                    "release-notes": "PASS",
                },
            )


if __name__ == "__main__":
    unittest.main()
