"""JSON-compatible release-readiness reports."""

from __future__ import annotations

from .models import ReadinessEvaluation


def build_report(evaluation: ReadinessEvaluation) -> dict[str, object]:
    status_counts = {"PASS": 0, "FAIL": 0}
    checks = []
    for item in evaluation.checks:
        checks.append({"name": item.name, "status": item.status})
        status_counts[item.status] += 1

    return {
        "ready": evaluation.ready,
        "checks": checks,
        "status_counts": status_counts,
    }
