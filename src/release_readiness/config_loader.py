"""Strict JSON policy loading."""

from __future__ import annotations

import json
from pathlib import Path

from .models import CheckPolicy, ReleasePolicy


def load_policy(path: str | Path) -> ReleasePolicy:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or set(raw) != {"version", "checks"}:
        raise ValueError("policy must contain only version and checks")
    if raw["version"] != 1:
        raise ValueError("unsupported policy version")
    if not isinstance(raw["checks"], list) or not raw["checks"]:
        raise ValueError("checks must be a non-empty list")

    checks: list[CheckPolicy] = []
    seen: set[str] = set()
    for item in raw["checks"]:
        if not isinstance(item, dict) or set(item) not in (
            {"name", "required"},
            {"name", "required", "severity"},
        ):
            raise ValueError(
                "each check must contain only name and required, with optional severity"
            )
        name = item["name"]
        required = item["required"]
        severity = item.get("severity", "blocker")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("check name must be a non-empty string")
        if name in seen:
            raise ValueError(f"duplicate check: {name}")
        if not isinstance(required, bool):
            raise ValueError(f"required must be boolean for {name}")
        if not isinstance(severity, str) or severity not in {"blocker", "advisory"}:
            raise ValueError(
                f"severity must be 'blocker' or 'advisory' for {name}"
            )
        seen.add(name)
        checks.append(
            CheckPolicy(name=name, required=required, severity=severity)
        )
    return ReleasePolicy(version=1, checks=tuple(checks))
