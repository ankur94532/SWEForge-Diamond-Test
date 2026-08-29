"""JSON-compatible release-readiness reports."""

from __future__ import annotations

from .models import ReadinessEvaluation


def build_report(evaluation: ReadinessEvaluation) -> dict[str, object]:
    checks: list[dict[str, str]] = []
    for item in evaluation.checks:
        check = {"name": item.name, "status": item.status}
        if item.source is not None:
            check["source"] = item.source
        checks.append(check)
    return {
        "ready": evaluation.ready,
        "checks": checks,
    }
