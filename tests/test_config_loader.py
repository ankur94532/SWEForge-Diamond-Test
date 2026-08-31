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

    def test_sets_source_path_to_loaded_file_path(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as file:
            json.dump(
                {
                    "version": 1,
                    "checks": [{"name": "unit-tests", "required": True}],
                },
                file,
            )
            path = Path(file.name)
        try:
            policy = load_policy(path)
            self.assertEqual(policy.source_path, str(path))
        finally:
            path.unlink()

    def test_rejects_unknown_check_fields(self):
        with self.assertRaisesRegex(ValueError, "only name and required"):
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


if __name__ == "__main__":
    unittest.main()
