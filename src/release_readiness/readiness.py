"""Release-readiness business rules."""

from __future__ import annotations

from collections.abc import Mapping

from .models import CheckResult, ReadinessEvaluation, ReleasePolicy

SUPPORTED_STATUSES = frozenset({"PASS", "FAIL"})


class MissingStatusError(ValueError):
    """Raised when a configured check has no usable status."""


def evaluate_readiness(
    policy: ReleasePolicy, statuses: Mapping[str, str]
) -> ReadinessEvaluation:
    configured = {item.name for item in policy.checks}
    unknown = sorted(set(statuses) - configured)
    if unknown:
        raise ValueError(f"statuses contain unknown checks: {', '.join(unknown)}")

    results: list[CheckResult] = []
    for check in policy.checks:
        if check.name in statuses:
            status = statuses[check.name]
            source = "explicit"
        elif not check.required and check.fallback is not None:
            status = check.fallback
            source = "fallback"
        else:
            raise MissingStatusError(f"missing status for {check.name}")
        if status not in SUPPORTED_STATUSES:
            raise ValueError(f"unsupported status for {check.name}: {status}")
        results.append(CheckResult(name=check.name, status=status, source=source))
    return ReadinessEvaluation(
        ready=all(item.status == "PASS" for item in results),
        checks=tuple(results),
    )
