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

    def test_loads_policy_without_fallbacks(self):
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
            [(item.name, item.required, item.fallback) for item in policy.checks],
            [("unit-tests", True, None), ("documentation", False, None)],
        )

    def test_loads_optional_fallback(self):
        policy = self.load(
            {
                "version": 1,
                "checks": [
                    {"name": "unit-tests", "required": True},
                    {"name": "documentation", "required": False, "fallback": "PASS"},
                ],
            }
        )
        self.assertEqual(policy.checks[1].fallback, "PASS")

    def test_rejects_unknown_check_fields(self):
        with self.assertRaisesRegex(ValueError, "optional fallback"):
            self.load(
                {
                    "version": 1,
                    "checks": [
                        {
                            "name": "unit-tests",
                            "required": True,
                            "unexpected": True,
                        }
                    ],
                }
            )

    def test_rejects_fallback_on_required_check(self):
        with self.assertRaisesRegex(ValueError, "required check cannot define fallback: unit-tests"):
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
        with self.assertRaisesRegex(ValueError, "unsupported fallback for documentation: UNKNOWN"):
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


if __name__ == "__main__":
    unittest.main()
