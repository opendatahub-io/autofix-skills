#!/usr/bin/env python3
"""Merge core review findings with extension findings.

Reads .autofix-context/review-findings.json and any files in
.autofix-context/extension-findings/*.json, concatenates them,
tags each with a 'source' field, and writes the result to
.autofix-context/all-findings.json.

If no extensions exist and no extension-findings/ directory is present,
copies review-findings.json as-is.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def merge(work_dir: Path | None = None) -> int:
    if work_dir is None:
        work_dir = Path(".")

    ctx_dir = work_dir / ".autofix-context"
    review_path = ctx_dir / "review-findings.json"
    ext_dir = ctx_dir / "extension-findings"
    output_path = ctx_dir / "all-findings.json"

    all_findings: list[dict] = []

    # Core review findings
    if review_path.exists():
        try:
            core = json.loads(review_path.read_text(encoding="utf-8"))
            if isinstance(core, list):
                for f in core:
                    f["source"] = "review"
                all_findings.extend(core)
        except (json.JSONDecodeError, OSError) as e:
            print(f"WARNING: Could not read review-findings.json: {e}", file=sys.stderr)

    # Extension findings
    if ext_dir.is_dir():
        for ext_file in sorted(ext_dir.glob("*.json")):
            skill_name = ext_file.stem
            try:
                ext_findings = json.loads(ext_file.read_text(encoding="utf-8"))
                if isinstance(ext_findings, list):
                    for f in ext_findings:
                        f["source"] = skill_name
                    all_findings.extend(ext_findings)
            except (json.JSONDecodeError, OSError) as e:
                print(f"WARNING: Could not read {ext_file}: {e}", file=sys.stderr)

    # Write merged output
    ctx_dir.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(all_findings, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Merged {len(all_findings)} finding(s) into {output_path}")
    return 0


if __name__ == "__main__":
    work_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    sys.exit(merge(work_dir))
