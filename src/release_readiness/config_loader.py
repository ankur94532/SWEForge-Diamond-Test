"""Strict JSON policy loading."""

from __future__ import annotations

import json
from pathlib import Path

from .models import CheckPolicy, ReleasePolicy


def load_policy(path: str | Path) -> ReleasePolicy:
    policy_path = Path(path)
    raw = json.loads(policy_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or set(raw) != {"version", "checks"}:
        raise ValueError("policy must contain only version and checks")
    if raw["version"] != 1:
        raise ValueError("unsupported policy version")
    if not isinstance(raw["checks"], list) or not raw["checks"]:
        raise ValueError("checks must be a non-empty list")

    checks: list[CheckPolicy] = []
    seen: set[str] = set()
    for item in raw["checks"]:
        if not isinstance(item, dict) or set(item) != {"name", "required"}:
            raise ValueError("each check must contain only name and required")
        name = item["name"]
        required = item["required"]
        if not isinstance(name, str) or not name.strip():
            raise ValueError("check name must be a non-empty string")
        if name in seen:
            raise ValueError(f"duplicate check: {name}")
        if not isinstance(required, bool):
            raise ValueError(f"required must be boolean for {name}")
        seen.add(name)
        checks.append(CheckPolicy(name=name, required=required))
    return ReleasePolicy(
        version=1,
        checks=tuple(checks),
        source_path=str(policy_path),
    )
