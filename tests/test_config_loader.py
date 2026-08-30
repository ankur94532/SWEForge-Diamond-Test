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
        self.assertEqual([item.fallback for item in policy.checks], [None, None])

    def test_loads_optional_check_fallback(self):
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
                            "unexpected": "PASS",
                        }
                    ],
                }
            )

    def test_rejects_fallback_for_required_check(self):
        with self.assertRaisesRegex(ValueError, "required check unit-tests"):
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

    def test_rejects_unsupported_or_malformed_fallback(self):
        for fallback in ("UNKNOWN", 1, None, ["PASS"]):
            with self.subTest(fallback=fallback):
                with self.assertRaisesRegex(ValueError, "unsupported fallback"):
                    self.load(
                        {
                            "version": 1,
                            "checks": [
                                {
                                    "name": "documentation",
                                    "required": False,
                                    "fallback": fallback,
                                }
                            ],
                        }
                    )


if __name__ == "__main__":
    unittest.main()
