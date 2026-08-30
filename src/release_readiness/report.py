"""JSON-compatible release-readiness reports."""

from __future__ import annotations

from .models import ReadinessEvaluation


def build_report(evaluation: ReadinessEvaluation) -> dict[str, object]:
    checks = [
        {"name": item.name, "status": item.status, "source": item.source}
        for item in evaluation.checks
    ]
    failed_checks = [item.name for item in evaluation.checks if item.status == "FAIL"]
    return {
        "ready": evaluation.ready,
        "summary": {
            "total": len(evaluation.checks),
            "passed": sum(item.status == "PASS" for item in evaluation.checks),
            "failed": len(failed_checks),
        },
        "failed_checks": failed_checks,
        "checks": checks,
    }
