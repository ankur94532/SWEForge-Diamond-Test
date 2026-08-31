"""Release-readiness business rules."""

from __future__ import annotations

from collections.abc import Mapping

from .models import CheckResult, ReadinessEvaluation, ReleasePolicy

SUPPORTED_STATUSES = frozenset({"PASS", "FAIL"})


class MissingStatusError(ValueError):
    """Raised when a configured check has no explicit status."""


def evaluate_readiness(
    policy: ReleasePolicy, statuses: Mapping[str, str]
) -> ReadinessEvaluation:
    configured = {item.name for item in policy.checks}
    unknown = sorted(set(statuses) - configured)
    if unknown:
        raise ValueError(f"statuses contain unknown checks: {', '.join(unknown)}")

    results: list[CheckResult] = []
    for check in policy.checks:
        if check.name not in statuses:
            raise MissingStatusError(f"missing status for {check.name}")
        status = statuses[check.name]
        if status not in SUPPORTED_STATUSES:
            raise ValueError(f"unsupported status for {check.name}: {status}")
        results.append(
            CheckResult(
                name=check.name,
                status=status,
                severity=check.severity,
            )
        )
    return ReadinessEvaluation(
        ready=all(
            item.status == "PASS" or item.severity == "advisory"
            for item in results
        ),
        checks=tuple(results),
    )
