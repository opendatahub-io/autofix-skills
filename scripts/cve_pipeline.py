#!/usr/bin/env python3
"""CVE pipeline state machine.

Deterministic state machine for the CVE resolve orchestrator. Each state
is a function that reads state from disk, determines the next action, and
returns the next state transition.

States:
    parse       → Extract CVE ID, package, repos from ticket context
    scan        → Call /scan-agent for the next unscanned repo/branch
    route       → Route based on scan verdict (present → fix, absent → vex)
    fix         → Call /fix-agent for the current repo/branch
    verify      → Call /verify-agent after fix
    review      → Call review agent on the diff
    vex         → Call /vex-agent for absent CVEs
    pr          → Create PR for verified fixes
    finalize    → Aggregate results and write verdict

Usage (from orchestrator SKILL.md):
    python3 ${CLAUDE_SKILL_DIR}/../../scripts/cve_pipeline.py next <state-file>
    python3 ${CLAUDE_SKILL_DIR}/../../scripts/cve_pipeline.py transition <state-file> <event>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml

    def _load(p: Path) -> dict:
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}

    def _save(p: Path, d: dict) -> None:
        p.write_text(yaml.dump(d, default_flow_style=False, sort_keys=False), encoding="utf-8")
except ImportError:

    def _load(p: Path) -> dict:
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}

    def _save(p: Path, d: dict) -> None:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")


# Valid state transitions
TRANSITIONS = {
    "parse": {"parsed": "scan", "ignore": "finalize"},
    "scan": {"present": "route", "absent": "route", "scan_done": "finalize"},
    "route": {"fix": "fix", "vex": "vex", "skip": "scan"},
    "fix": {"fixed": "verify", "fix_failed": "scan"},
    "verify": {"verified": "review", "still_present": "scan", "verify_failed": "scan"},
    "review": {"approved": "pr", "rejected": "fix", "cap_reached": "pr"},
    "vex": {"justified": "scan", "needs_human": "scan"},
    "pr": {"created": "scan", "pr_failed": "scan"},
    "finalize": {},
}


def init_state(state_file: Path, ticket_data: dict | None = None) -> dict:
    """Initialize a fresh CVE pipeline state."""
    state = {
        "phase": "parse",
        "cve_id": "",
        "package": "",
        "container": "",
        "jira_key": "",
        "severity": "",
        "repos": [],
        "current_repo_idx": -1,
        "current_branch_idx": -1,
        "results": [],
        "prs_created": [],
        "skipped": [],
        "iteration_count": 0,
        "max_iterations": 3,
        "last_event": "",
    }
    if ticket_data:
        state.update(ticket_data)
    _save(state_file, state)
    return state


def get_next_action(state: dict) -> dict:
    """Given current state, return what the orchestrator should do next.

    Returns:
        {
            "action": str,          # human-readable action description
            "prompt_file": str,     # which prompt file to read/execute
            "args": dict,           # arguments for the action
            "phase": str,           # current phase
        }
    """
    phase = state.get("phase", "parse")

    if phase == "parse":
        return {
            "action": "Parse ticket context to extract CVE ID, package, and repos",
            "prompt_file": None,
            "args": {},
            "phase": phase,
        }

    if phase == "scan":
        # Find next unprocessed repo/branch
        next_repo, next_branch = _find_next_unprocessed(state)
        if next_repo is None:
            return {
                "action": "All repos/branches scanned. Move to finalize.",
                "prompt_file": None,
                "args": {"event": "scan_done"},
                "phase": phase,
            }
        return {
            "action": f"Scan {next_repo['name']}:{next_branch} for CVE {state.get('cve_id', '?')}",
            "prompt_file": "prompts/scan-agent.md",
            "args": {"repo": next_repo["name"], "branch": next_branch},
            "phase": phase,
        }

    if phase == "route":
        return {
            "action": "Route based on scan verdict",
            "prompt_file": None,
            "args": {},
            "phase": phase,
        }

    if phase == "fix":
        repo_name = _current_repo_name(state)
        return {
            "action": f"Apply CVE fix for {repo_name}",
            "prompt_file": "prompts/fix-agent.md",
            "args": {"repo": repo_name},
            "phase": phase,
        }

    if phase == "verify":
        repo_name = _current_repo_name(state)
        return {
            "action": f"Verify CVE fix for {repo_name}",
            "prompt_file": "prompts/verify-agent.md",
            "args": {"repo": repo_name},
            "phase": phase,
        }

    if phase == "review":
        repo_name = _current_repo_name(state)
        iteration = state.get("iteration_count", 0)
        return {
            "action": f"Review fix for {repo_name} (iteration {iteration})",
            "prompt_file": "prompts/review-agent.md",
            "args": {"repo": repo_name, "iteration": iteration},
            "phase": phase,
        }

    if phase == "vex":
        repo_name = _current_repo_name(state)
        return {
            "action": f"Assess VEX justification for {repo_name}",
            "prompt_file": "prompts/vex-agent.md",
            "args": {"repo": repo_name},
            "phase": phase,
        }

    if phase == "pr":
        repo_name = _current_repo_name(state)
        return {
            "action": f"Create PR for {repo_name}",
            "prompt_file": None,
            "args": {"repo": repo_name},
            "phase": phase,
        }

    if phase == "finalize":
        return {
            "action": "Write final verdict",
            "prompt_file": None,
            "args": {},
            "phase": phase,
        }

    return {
        "action": f"Unknown phase: {phase}",
        "prompt_file": None,
        "args": {},
        "phase": phase,
    }


def transition(state_file: Path, event: str) -> dict:
    """Apply event to current state, write new state, return it."""
    state = _load(state_file)
    phase = state.get("phase", "parse")

    valid_events = TRANSITIONS.get(phase, {})
    if event not in valid_events:
        raise ValueError(
            f"Invalid transition: phase={phase}, event={event}. "
            f"Valid events: {list(valid_events.keys())}"
        )

    next_phase = valid_events[event]
    state["phase"] = next_phase
    state["last_event"] = event

    _save(state_file, state)
    return state


def _find_next_unprocessed(state: dict) -> tuple[dict | None, str | None]:
    """Find the next repo/branch pair that hasn't been processed yet."""
    repos = state.get("repos", [])
    results = state.get("results", [])
    processed = {(r.get("repo"), r.get("branch")) for r in results}

    for repo in repos:
        name = repo.get("name", "")
        for branch in repo.get("branches", []):
            if (name, branch) not in processed:
                return repo, branch
    return None, None


def _current_repo_name(state: dict) -> str:
    repos = state.get("repos", [])
    idx = state.get("current_repo_idx", -1)
    if 0 <= idx < len(repos):
        return repos[idx].get("name", "unknown")
    return "unknown"


def cmd_next(state_file: Path) -> int:
    """Print the next action for the orchestrator."""
    state = _load(state_file)
    if not state:
        print("ERROR: State file not found or empty", file=sys.stderr)
        return 1

    action = get_next_action(state)
    print(json.dumps(action, indent=2))
    return 0


def cmd_transition(state_file: Path, event: str) -> int:
    """Apply an event transition and print new state."""
    try:
        new_state = transition(state_file, event)
        print(f"Transitioned to phase: {new_state['phase']}")
        return 0
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


def cmd_init(state_file: Path) -> int:
    """Initialize a new CVE pipeline state file."""
    init_state(state_file)
    print(f"Initialized CVE pipeline state: {state_file}")
    return 0


def main() -> int:
    if len(sys.argv) < 3:
        print(
            "Usage:\n"
            "  cve_pipeline.py init <state-file>\n"
            "  cve_pipeline.py next <state-file>\n"
            "  cve_pipeline.py transition <state-file> <event>",
            file=sys.stderr,
        )
        return 1

    command = sys.argv[1]
    state_file = Path(sys.argv[2])

    if command == "init":
        return cmd_init(state_file)
    elif command == "next":
        return cmd_next(state_file)
    elif command == "transition":
        if len(sys.argv) < 4:
            print("Usage: cve_pipeline.py transition <state-file> <event>", file=sys.stderr)
            return 1
        return cmd_transition(state_file, sys.argv[3])
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
