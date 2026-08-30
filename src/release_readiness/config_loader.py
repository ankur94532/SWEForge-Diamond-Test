"""Strict JSON policy loading."""

from __future__ import annotations

import json
from pathlib import Path

from .models import CheckPolicy, ReleasePolicy
from .readiness import SUPPORTED_STATUSES


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
        required_keys = {"name", "required"}
        allowed_keys = required_keys | {"fallback"}
        if (
            not isinstance(item, dict)
            or not required_keys.issubset(item)
            or not set(item).issubset(allowed_keys)
        ):
            raise ValueError(
                "each check must contain name and required, with optional fallback"
            )
        name = item["name"]
        required = item["required"]
        if not isinstance(name, str) or not name.strip():
            raise ValueError("check name must be a non-empty string")
        if name in seen:
            raise ValueError(f"duplicate check: {name}")
        if not isinstance(required, bool):
            raise ValueError(f"required must be boolean for {name}")

        fallback = None
        if "fallback" in item:
            fallback = item["fallback"]
            if required:
                raise ValueError(f"fallback is not allowed for required check {name}")
            if not isinstance(fallback, str) or fallback not in SUPPORTED_STATUSES:
                raise ValueError(f"unsupported fallback for {name}: {fallback}")

        seen.add(name)
        checks.append(CheckPolicy(name=name, required=required, fallback=fallback))
    return ReleasePolicy(version=1, checks=tuple(checks))
