# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Post-validation for branch-resolve verdicts.

Enforces cross-field invariants that JSON Schema cannot express:
- target_branch must not contain the refs/heads/ prefix
- target_branch must not be empty after stripping whitespace

Usage:
    uv run --script validate_verdict.py <verdict-json>

Exit codes:
    0  All invariants hold
    1  Semantic validation failed
    2  Usage error (bad arguments, missing file, bad JSON)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_verdict.py <verdict-json>", file=sys.stderr)
        return 2

    verdict_path = Path(sys.argv[1])
    if not verdict_path.exists():
        print(f"File not found: {verdict_path}", file=sys.stderr)
        return 2

    try:
        data = json.loads(verdict_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"Cannot read verdict: {e}", file=sys.stderr)
        return 2

    target = data.get("target_branch", "")

    if not target.strip():
        print("Semantic error: target_branch is empty or whitespace-only", file=sys.stderr)
        return 1

    if target.startswith("refs/heads/"):
        print(
            f"Semantic error: target_branch '{target}' should not include "
            f"the 'refs/heads/' prefix -- use the bare branch name instead",
            file=sys.stderr,
        )
        return 1

    print("Verdict semantics valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
