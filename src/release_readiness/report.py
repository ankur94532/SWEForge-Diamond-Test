"""JSON-compatible release-readiness reports."""

from __future__ import annotations

from .models import ReadinessEvaluation


SUPPORTED_SEVERITIES = ("blocker", "advisory")


def build_report(evaluation: ReadinessEvaluation) -> dict[str, object]:
    severity_counts = {
        severity: sum(item.severity == severity for item in evaluation.checks)
        for severity in SUPPORTED_SEVERITIES
    }
    return {
        "ready": evaluation.ready,
        "checks": [
            {
                "name": item.name,
                "status": item.status,
                "severity": item.severity,
            }
            for item in evaluation.checks
        ],
        "severity_counts": severity_counts,
    }
