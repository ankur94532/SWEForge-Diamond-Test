from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from src.release_readiness.config_loader import load_policy
from src.release_readiness.models import CheckPolicy, CheckResult, ReleasePolicy
from src.release_readiness.readiness import MissingStatusError, evaluate_readiness
from src.release_readiness.report import build_report

ROOT = Path(__file__).parent
STAGES = ("baseline", "model", "loader", "readiness", "report-contract")


def verify_baseline() -> None:
    subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=ROOT,
        check=True,
    )


def verify_model() -> None:
    policy = CheckPolicy("optional-docs", required=False, fallback="PASS")
    assert policy.fallback == "PASS"
    explicit = CheckResult("unit-tests", "PASS", source="explicit")
    fallback = CheckResult("optional-docs", "PASS", source="fallback")
    assert explicit.source == "explicit"
    assert fallback.source == "fallback"


def policy_file(checks: list[dict[str, object]]) -> Path:
    handle = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
    with handle:
        json.dump({"version": 1, "checks": checks}, handle)
    return Path(handle.name)


def verify_loader() -> None:
    valid = policy_file(
        [
            {"name": "unit-tests", "required": True},
            {"name": "optional-docs", "required": False, "fallback": "PASS"},
        ]
    )
    try:
        policy = load_policy(valid)
        assert policy.checks[1].fallback == "PASS"
    finally:
        valid.unlink()

    for checks in (
        [{"name": "required", "required": True, "fallback": "PASS"}],
        [{"name": "optional", "required": False, "fallback": "UNKNOWN"}],
    ):
        invalid = policy_file(checks)
        try:
            try:
                load_policy(invalid)
            except ValueError:
                pass
            else:
                raise AssertionError("invalid fallback configuration was accepted")
        finally:
            invalid.unlink()


def fallback_policy():
    path = policy_file(
        [
            {"name": "unit-tests", "required": True},
            {"name": "optional-docs", "required": False, "fallback": "PASS"},
        ]
    )
    try:
        return load_policy(path)
    finally:
        path.unlink()


def verify_readiness() -> None:
    policy = ReleasePolicy(
        version=1,
        checks=(
            CheckPolicy("unit-tests", required=True),
            CheckPolicy("optional-docs", required=False, fallback="PASS"),
        ),
    )
    mixed = evaluate_readiness(policy, {"unit-tests": "PASS"})
    assert mixed.ready is True
    assert [(item.name, item.status, item.source) for item in mixed.checks] == [
        ("unit-tests", "PASS", "explicit"),
        ("optional-docs", "PASS", "fallback"),
    ]
    try:
        evaluate_readiness(policy, {"optional-docs": "PASS"})
    except MissingStatusError as exc:
        assert "unit-tests" in str(exc)
    else:
        raise AssertionError("missing required check did not fail")


def verify_report() -> None:
    policy = fallback_policy()
    all_explicit = build_report(
        evaluate_readiness(
            policy, {"unit-tests": "PASS", "optional-docs": "FAIL"}
        )
    )
    assert all_explicit == {
        "ready": False,
        "checks": [
            {"name": "unit-tests", "status": "PASS", "source": "explicit"},
            {"name": "optional-docs", "status": "FAIL", "source": "explicit"},
        ],
    }
    mixed = build_report(evaluate_readiness(policy, {"unit-tests": "PASS"}))
    assert mixed["checks"][1] == {
        "name": "optional-docs",
        "status": "PASS",
        "source": "fallback",
    }
    verify_baseline()


VERIFY = {
    "baseline": verify_baseline,
    "model": verify_model,
    "loader": verify_loader,
    "readiness": verify_readiness,
    "report-contract": verify_report,
}


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in VERIFY:
        print(f"usage: python verify.py <{'|'.join(STAGES)}>", file=sys.stderr)
        return 2
    try:
        VERIFY[sys.argv[1]]()
    except Exception as exc:
        print(f"{sys.argv[1]} verification failed: {exc}", file=sys.stderr)
        return 1
    print(f"{sys.argv[1]} verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
