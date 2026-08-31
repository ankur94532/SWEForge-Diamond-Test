"""Stable value objects used by release-readiness components."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Severity = Literal["blocker", "advisory"]


@dataclass(frozen=True, slots=True)
class CheckPolicy:
    name: str
    required: bool
    severity: Severity = "blocker"


@dataclass(frozen=True, slots=True)
class ReleasePolicy:
    version: int
    checks: tuple[CheckPolicy, ...]


@dataclass(frozen=True, slots=True)
class CheckResult:
    name: str
    status: str
    severity: Severity = "blocker"


@dataclass(frozen=True, slots=True)
class ReadinessEvaluation:
    ready: bool
    checks: tuple[CheckResult, ...]
