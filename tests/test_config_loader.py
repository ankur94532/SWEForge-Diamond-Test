from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.release_readiness.config_loader import load_policy


class ConfigLoaderTests(unittest.TestCase):
    def load(self, document: object):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as file:
            json.dump(document, file)
            path = Path(file.name)
        try:
            return load_policy(path)
        finally:
            path.unlink()

    def test_loads_strict_version_one_policy(self):
        policy = self.load(
            {
                "version": 1,
                "checks": [
                    {"name": "unit-tests", "required": True},
                    {"name": "documentation", "required": False},
                ],
            }
        )
        self.assertEqual(
            [item.name for item in policy.checks], ["unit-tests", "documentation"]
        )
        self.assertIsNone(policy.checks[0].fallback)
        self.assertIsNone(policy.checks[1].fallback)

    def test_rejects_unknown_check_fields(self):
        with self.assertRaisesRegex(ValueError, "name, required"):
            self.load(
                {
                    "version": 1,
                    "checks": [
                        {
                            "name": "unit-tests",
                            "required": True,
                            "extra": "nope",
                        }
                    ],
                }
            )

    def test_loads_optional_check_with_fallback(self):
        policy = self.load(
            {
                "version": 1,
                "checks": [
                    {"name": "unit-tests", "required": True},
                    {
                        "name": "documentation",
                        "required": False,
                        "fallback": "PASS",
                    },
                ],
            }
        )
        self.assertIsNone(policy.checks[0].fallback)
        self.assertEqual(policy.checks[1].fallback, "PASS")

    def test_rejects_fallback_on_required_check(self):
        with self.assertRaisesRegex(
            ValueError, "fallback is not allowed for required check"
        ):
            self.load(
                {
                    "version": 1,
                    "checks": [
                        {
                            "name": "unit-tests",
                            "required": True,
                            "fallback": "PASS",
                        }
                    ],
                }
            )

    def test_rejects_unsupported_fallback_value(self):
        with self.assertRaisesRegex(ValueError, "unsupported fallback"):
            self.load(
                {
                    "version": 1,
                    "checks": [
                        {
                            "name": "documentation",
                            "required": False,
                            "fallback": "UNKNOWN",
                        }
                    ],
                }
            )

    def test_rejects_non_string_fallback_value(self):
        with self.assertRaisesRegex(ValueError, "unsupported fallback"):
            self.load(
                {
                    "version": 1,
                    "checks": [
                        {
                            "name": "documentation",
                            "required": False,
                            "fallback": 1,
                        }
                    ],
                }
            )


if __name__ == "__main__":
    unittest.main()
