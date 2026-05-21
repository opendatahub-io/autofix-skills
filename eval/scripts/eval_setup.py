#!/usr/bin/env python3
"""Commit workspace files seeded by the eval harness.

Called as a SessionStart hook before the skill runs. The harness copies
source files, autofix-context/, AGENTS.md, etc. from the case's files/
directory into the workspace. This script commits them so they don't
appear in collect.py's git diff (which tracks agent modifications).
"""
from __future__ import annotations

import os
import subprocess


def main() -> None:
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "eval-setup",
        "GIT_AUTHOR_EMAIL": "eval@setup",
        "GIT_COMMITTER_NAME": "eval-setup",
        "GIT_COMMITTER_EMAIL": "eval@setup",
    }
    subprocess.run(
        ["git", "add", "-A"],
        check=True, capture_output=True,
    )
    subprocess.run(
        ["git", "commit", "-q", "-m", "case setup", "--allow-empty"],
        check=True, capture_output=True, env=env,
    )
    print("eval_setup: workspace committed")


if __name__ == "__main__":
    main()
