"""JSON-compatible release-readiness reports."""

from __future__ import annotations

from .models import ReadinessEvaluation


def build_report(evaluation: ReadinessEvaluation) -> dict[str, object]:
    total = len(evaluation.checks)
    passed = sum(1 for item in evaluation.checks if item.status == "PASS")
    failed = sum(1 for item in evaluation.checks if item.status == "FAIL")
    failed_names = [item.name for item in evaluation.checks if item.status == "FAIL"]

    return {
        "ready": evaluation.ready,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "failed_names": failed_names,
        },
        "checks": [
            {"name": item.name, "status": item.status} for item in evaluation.checks
        ],
    }
