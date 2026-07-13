# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Post-validation for repo-resolve verdicts.

Enforces cross-field invariants that JSON Schema cannot express:
- Exactly one candidate must be classified as 'target'
- target_url must match that candidate's url

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

    candidates = data.get("candidates", [])
    target_candidates = [c for c in candidates if c.get("classification") == "target"]

    if len(target_candidates) != 1:
        print(
            f"Semantic error: expected exactly 1 candidate classified as "
            f"'target', found {len(target_candidates)}",
            file=sys.stderr,
        )
        return 1

    if data.get("target_url") != target_candidates[0].get("url"):
        print(
            f"Semantic error: target_url '{data.get('target_url')}' does not "
            f"match the candidate classified as 'target' "
            f"('{target_candidates[0].get('url')}')",
            file=sys.stderr,
        )
        return 1

    print("Verdict semantics valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
