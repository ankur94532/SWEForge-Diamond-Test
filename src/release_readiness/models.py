"""Stable value objects used by release-readiness components."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CheckPolicy:
    name: str
    required: bool


@dataclass(frozen=True, slots=True)
class ReleasePolicy:
    version: int
    checks: tuple[CheckPolicy, ...]


@dataclass(frozen=True, slots=True)
class CheckResult:
    name: str
    status: str


@dataclass(frozen=True, slots=True)
class ReadinessEvaluation:
    ready: bool
    checks: tuple[CheckResult, ...]
