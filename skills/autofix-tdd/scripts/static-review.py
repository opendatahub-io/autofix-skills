#!/usr/bin/env python3
"""Static review: mechanical checks + coverage analysis.

Replaces the LLM review agent with deterministic static analysis.
Runs the same checks the review-agent.md prescribes (debug prints,
TODO markers, commented-out code blocks) plus pytest coverage analysis
if available. Writes .autofix-context/review-findings.json.

Usage:
    python3 static-review.py
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def get_changed_files() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only"],
        capture_output=True,
        text=True,
    )
    return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]


def get_added_lines(files: list[str]) -> list[str]:
    if not files:
        return []
    try:
        result = subprocess.run(
            ["git", "diff", "-U0", "--"] + files,
            capture_output=True,
            text=True,
        )
        return [
            line
            for line in result.stdout.split("\n")
            if line.startswith("+") and not line.startswith("+++")
        ]
    except OSError:
        return []


def check_debug_prints(added_lines: list[str]) -> list[dict]:
    pattern = re.compile(
        r"console\.log|(?<!\w)print\(|fmt\.Print|System\.out|log\.Debug",
        re.IGNORECASE,
    )
    findings = []
    for line in added_lines:
        content = line[1:].strip()
        if pattern.search(content):
            findings.append(
                {
                    "severity": "minor",
                    "description": f"Possible debug print left behind: {content[:120]}",
                    "file": "",
                    "line": 0,
                }
            )
    return findings


def check_todo_markers(added_lines: list[str]) -> list[dict]:
    pattern = re.compile(r"\bTODO\b|\bFIXME\b|\bHACK\b|\bXXX\b", re.IGNORECASE)
    findings = []
    for line in added_lines:
        content = line[1:].strip()
        if pattern.search(content):
            findings.append(
                {
                    "severity": "nitpick",
                    "description": f"TODO/FIXME marker in new code: {content[:120]}",
                    "file": "",
                    "line": 0,
                }
            )
    return findings


def check_commented_out_code(added_lines: list[str]) -> list[dict]:
    comment_pattern = re.compile(r"^\+\s*(//|#|/\*|\*)")
    streak = 0
    found = False
    for line in added_lines:
        if comment_pattern.match(line):
            streak += 1
            if streak >= 3:
                found = True
        else:
            streak = 0
    if found:
        return [
            {
                "severity": "minor",
                "description": (
                    "Large block of commented-out code (3+ consecutive comment lines added)"
                ),
                "file": "",
                "line": 0,
            }
        ]
    return []


def run_coverage(files: list[str]) -> list[dict]:
    source_files = [f for f in files if f.endswith(".py") and "test" not in f.lower()]
    if not source_files:
        return []
    cov_json = Path("tmp/coverage.json")
    try:
        subprocess.run(
            ["pytest", "--cov", "--cov-report", f"json:{cov_json}", "-q"],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []
    if not cov_json.exists():
        return []
    try:
        cov = json.loads(cov_json.read_text())
    except (json.JSONDecodeError, OSError):
        return []
    findings = []
    for filepath in source_files:
        for cov_path, data in cov.get("files", {}).items():
            if cov_path.endswith(filepath) or filepath in cov_path:
                missing = data.get("missing_lines", [])
                if missing:
                    findings.append(
                        {
                            "severity": "minor",
                            "description": f"Untested execution paths on lines {missing}",
                            "file": filepath,
                            "line": missing[0],
                        }
                    )
                break
    return findings


def main() -> int:
    files = get_changed_files()
    if not files:
        findings: list[dict] = []
    else:
        added_lines = get_added_lines(files)
        findings = []
        findings.extend(check_debug_prints(added_lines))
        findings.extend(check_todo_markers(added_lines))
        findings.extend(check_commented_out_code(added_lines))
        findings.extend(run_coverage(files))

    output = Path(".autofix-context/review-findings.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(findings, indent=2, ensure_ascii=False))
    print(f"Static review: {len(findings)} finding(s) written to {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
