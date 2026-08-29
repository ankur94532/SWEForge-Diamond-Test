from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).parent
STATE = ROOT / "state"

REQUIRED_DONE = {
    "A": ("A",),
    "B": ("A", "B"),
    "C": ("A", "C"),
    "D": ("A", "B", "C", "D"),
}


def read_state(task: str) -> str:
    return (STATE / f"{task}.txt").read_text(encoding="utf-8").strip()


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in REQUIRED_DONE:
        print("usage: python verify.py <A|B|C|D>", file=sys.stderr)
        return 2

    task = sys.argv[1]
    failures = [
        name for name in REQUIRED_DONE[task] if read_state(name) != "DONE"
    ]
    if failures:
        print(
            f"{task} validation failed; expected DONE for: {', '.join(failures)}",
            file=sys.stderr,
        )
        return 1

    print(f"{task} validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
