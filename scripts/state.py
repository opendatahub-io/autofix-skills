#!/usr/bin/env python3
"""State persistence utility for autofix orchestrator skills.

Provides read/write access to orchestrator state files and a
dispatch-context subcommand for context-compression recovery.

All I/O through Python (no cat/echo that trigger auth prompts in sandbox).

Subcommands:
    get <state-file> <key>          Read a value from the state file
    set <state-file> <key> <value>  Write a value to the state file
    init <state-file>               Initialize a new state file
    dispatch-context <state-file>   Print dispatch instructions for context recovery

State files use YAML for readability and are written to the workspace
directory (the cloned repo working dir), which persists across context
compression.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


def _load_state(path: Path) -> dict:
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8")
    if yaml:
        return yaml.safe_load(raw) or {}
    return json.loads(raw)


def _save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if yaml:
        path.write_text(
            yaml.dump(state, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )
    else:
        path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


def cmd_init(state_file: Path) -> int:
    """Initialize an empty state file."""
    initial = {
        "phase": "start",
        "ticket_key": "",
        "iteration": 0,
        "max_iterations": 3,
        "skill_name": "",
        "repos_processed": [],
        "repos_remaining": [],
        "findings_count": 0,
        "last_action": "",
    }
    _save_state(state_file, initial)
    print(f"Initialized state file: {state_file}")
    return 0


def cmd_get(state_file: Path, key: str) -> int:
    """Read a value from the state file."""
    state = _load_state(state_file)
    value = state.get(key)
    if value is None:
        print(f"Key not found: {key}", file=sys.stderr)
        return 1
    if isinstance(value, (list, dict)):
        print(json.dumps(value, indent=2))
    else:
        print(value)
    return 0


def cmd_set(state_file: Path, key: str, value: str) -> int:
    """Write a value to the state file."""
    state = _load_state(state_file)

    # Auto-detect type
    if value.lower() in ("true", "false"):
        state[key] = value.lower() == "true"
    elif value.isdigit():
        state[key] = int(value)
    elif value.startswith("[") or value.startswith("{"):
        try:
            state[key] = json.loads(value)
        except json.JSONDecodeError:
            state[key] = value
    else:
        state[key] = value

    _save_state(state_file, state)
    return 0


def cmd_dispatch_context(state_file: Path) -> int:
    """Print human-readable dispatch instructions for context recovery.

    Called by the SessionStart hook after context compression.
    Reads the state file and tells the LLM exactly what to do next.
    """
    state = _load_state(state_file)

    if not state:
        print("No state file found. Starting fresh.")
        return 0

    phase = state.get("phase", "unknown")
    ticket_key = state.get("ticket_key", "unknown")
    iteration = state.get("iteration", 0)
    max_iterations = state.get("max_iterations", 3)
    skill_name = state.get("skill_name", "")
    last_action = state.get("last_action", "")
    repos_remaining = state.get("repos_remaining", [])
    repos_processed = state.get("repos_processed", [])
    findings_count = state.get("findings_count", 0)

    print("=" * 60)
    print("CONTEXT RECOVERY — State restored from disk")
    print("=" * 60)
    print()
    print(f"Ticket:     {ticket_key}")
    print(f"Skill:      {skill_name}")
    print(f"Phase:      {phase}")
    print(f"Iteration:  {iteration}/{max_iterations}")
    print(f"Last action: {last_action}")
    print()

    if repos_processed:
        print(f"Repos processed ({len(repos_processed)}):")
        for r in repos_processed:
            print(f"  ✓ {r}")

    if repos_remaining:
        print(f"Repos remaining ({len(repos_remaining)}):")
        for r in repos_remaining:
            print(f"  → {r}")

    if findings_count:
        print(f"Findings so far: {findings_count}")

    print()

    # Dispatch instructions based on phase
    if phase == "implement":
        print(f"NEXT: Call the implement agent (iteration {iteration + 1}).")
        print("Read autofix-context/ticket.json for context.")
        if findings_count > 0:
            print("Read autofix-context/all-findings.json for findings to address.")
    elif phase == "review":
        print("NEXT: Call the review agent to check the implementation.")
        print("It will write findings to autofix-context/review-findings.json.")
    elif phase == "evaluate":
        print("NEXT: Read autofix-context/review-findings.json and decide:")
        print("  - critical/minor → iterate (call implement again)")
        print("  - nitpick/empty → proceed to verdict")
        cap_status = "can iterate" if iteration < max_iterations else "HARD CAP REACHED"
        print(f"  - iteration {iteration}/{max_iterations} — {cap_status}")
    elif phase == "scan":
        if repos_remaining:
            next_repo = repos_remaining[0]
            print(f"NEXT: Call /cve-scan for repo: {next_repo}")
        else:
            print("NEXT: All repos scanned. Move to fix phase.")
    elif phase == "fix":
        if repos_remaining:
            next_repo = repos_remaining[0]
            print(f"NEXT: Call /cve-fix-apply for repo: {next_repo}")
        else:
            print("NEXT: All fixes applied. Move to verify phase.")
    elif phase == "verify":
        if repos_remaining:
            next_repo = repos_remaining[0]
            print(f"NEXT: Call /cve-verify for repo: {next_repo}")
        else:
            print("NEXT: All verifications complete. Move to review phase.")
    elif phase == "done":
        print("DONE: Pipeline completed. Write the verdict file.")
    else:
        print(f"NEXT: Unknown phase '{phase}'. Read the state file at {state_file} for details.")

    print()
    print("=" * 60)
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: state.py <command> <state-file> [args...]", file=sys.stderr)
        print("Commands: init, get, set, dispatch-context", file=sys.stderr)
        return 1

    command = sys.argv[1]
    if command == "init":
        if len(sys.argv) < 3:
            print("Usage: state.py init <state-file>", file=sys.stderr)
            return 1
        return cmd_init(Path(sys.argv[2]))
    elif command == "get":
        if len(sys.argv) < 4:
            print("Usage: state.py get <state-file> <key>", file=sys.stderr)
            return 1
        return cmd_get(Path(sys.argv[2]), sys.argv[3])
    elif command == "set":
        if len(sys.argv) < 5:
            print("Usage: state.py set <state-file> <key> <value>", file=sys.stderr)
            return 1
        return cmd_set(Path(sys.argv[2]), sys.argv[3], sys.argv[4])
    elif command == "dispatch-context":
        if len(sys.argv) < 3:
            print("Usage: state.py dispatch-context <state-file>", file=sys.stderr)
            return 1
        return cmd_dispatch_context(Path(sys.argv[2]))
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
