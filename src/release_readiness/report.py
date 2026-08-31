"""JSON-compatible release-readiness reports."""

from __future__ import annotations

from .models import ReadinessEvaluation


def build_report(evaluation: ReadinessEvaluation) -> dict[str, object]:
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
    }
