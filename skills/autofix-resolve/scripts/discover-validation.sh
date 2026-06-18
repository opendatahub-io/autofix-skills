#!/usr/bin/env bash
set -euo pipefail

# Discovers lint, build, and test commands from repo docs and standard patterns.
# Outputs tmp/validation-commands.json with commands the implement agent should run.

OUTPUT_DIR="tmp"
OUTPUT_FILE="${OUTPUT_DIR}/validation-commands.json"
mkdir -p "${OUTPUT_DIR}"

lint_cmd=""
build_cmd=""
test_cmd=""
source_doc=""

# --- Check repo docs for documented commands ---
for doc in CLAUDE.md AGENTS.md CONTRIBUTING.md; do
  if [ -f "$doc" ]; then
    source_doc="$doc"
    break
  fi
done

# --- Detect language ---
language="unknown"
if [ -f "go.mod" ]; then
  language="go"
elif [ -f "pyproject.toml" ] || [ -f "setup.py" ] || [ -f "setup.cfg" ]; then
  language="python"
elif [ -f "package.json" ]; then
  language="node"
elif [ -f "Cargo.toml" ]; then
  language="rust"
fi

# --- Discover Makefile targets ---
makefile_lint=""
makefile_build=""
makefile_test=""
if [ -f "Makefile" ] || [ -f "makefile" ] || [ -f "GNUmakefile" ]; then
  targets=$(grep -Eh '^[[:alnum:]_.%/@+-]+:' Makefile makefile GNUmakefile 2>/dev/null \
    | sed 's/:.*//' | sort -u)

  for t in lint vet check-lint golangci-lint; do
    if echo "${targets}" | grep -qx "$t"; then
      makefile_lint="make $t"
      break
    fi
  done

  for t in build compile; do
    if echo "${targets}" | grep -qx "$t"; then
      makefile_build="make $t"
      break
    fi
  done

  for t in test unit-test test-unit tests; do
    if echo "${targets}" | grep -qx "$t"; then
      makefile_test="make $t"
      break
    fi
  done
fi

# --- Language-specific fallbacks ---
case "${language}" in
  go)
    [ -z "${lint_cmd}" ] && lint_cmd="${makefile_lint:-golangci-lint run}"
    [ -z "${build_cmd}" ] && build_cmd="${makefile_build:-go build ./...}"
    [ -z "${test_cmd}" ] && test_cmd="${makefile_test:-go test ./...}"
    ;;
  python)
    if [ -f "tox.ini" ]; then
      [ -z "${test_cmd}" ] && test_cmd="tox"
    elif [ -f "pytest.ini" ] || [ -d "tests" ] || [ -d "test" ]; then
      [ -z "${test_cmd}" ] && test_cmd="pytest"
    fi
    for linter in ruff.toml .flake8 pyproject.toml; do
      if [ -f "$linter" ]; then
        if [ "$linter" = "ruff.toml" ] || ([ "$linter" = "pyproject.toml" ] && grep -q '\[tool.ruff\]' pyproject.toml 2>/dev/null); then
          [ -z "${lint_cmd}" ] && lint_cmd="ruff check"
        elif [ "$linter" = ".flake8" ]; then
          [ -z "${lint_cmd}" ] && lint_cmd="flake8"
        fi
        break
      fi
    done
    [ -z "${lint_cmd}" ] && lint_cmd="${makefile_lint:-}"
    [ -z "${build_cmd}" ] && build_cmd="${makefile_build:-}"
    [ -z "${test_cmd}" ] && test_cmd="${makefile_test:-}"
    ;;
  node)
    if [ -f "package.json" ]; then
      npm_lint=$(python3 -c "
import json, sys
try:
    s = json.load(open('package.json')).get('scripts', {})
    for k in ['lint', 'check']:
        if k in s: print(f'npm run {k}'); sys.exit(0)
except Exception: pass
" 2>/dev/null || true)
      npm_build=$(python3 -c "
import json, sys
try:
    s = json.load(open('package.json')).get('scripts', {})
    for k in ['build', 'compile']:
        if k in s: print(f'npm run {k}'); sys.exit(0)
except Exception: pass
" 2>/dev/null || true)
      npm_test=$(python3 -c "
import json, sys
try:
    s = json.load(open('package.json')).get('scripts', {})
    for k in ['test', 'test:unit']:
        if k in s: print(f'npm run {k}'); sys.exit(0)
except Exception: pass
" 2>/dev/null || true)
      [ -z "${lint_cmd}" ] && lint_cmd="${npm_lint:-${makefile_lint:-}}"
      [ -z "${build_cmd}" ] && build_cmd="${npm_build:-${makefile_build:-}}"
      [ -z "${test_cmd}" ] && test_cmd="${npm_test:-${makefile_test:-}}"
    fi
    ;;
  rust)
    [ -z "${lint_cmd}" ] && lint_cmd="cargo clippy"
    [ -z "${build_cmd}" ] && build_cmd="cargo build"
    [ -z "${test_cmd}" ] && test_cmd="cargo test"
    ;;
esac

# --- Write JSON output via jq (avoids shell-variable injection into python3 -c) ---
jq -n \
  --arg language "$language" \
  --arg lint_cmd "$lint_cmd" \
  --arg build_cmd "$build_cmd" \
  --arg test_cmd "$test_cmd" \
  --arg source_doc "$source_doc" \
  '{
    language: $language,
    lint_cmd: (if $lint_cmd == "" then null else $lint_cmd end),
    build_cmd: (if $build_cmd == "" then null else $build_cmd end),
    test_cmd: (if $test_cmd == "" then null else $test_cmd end),
    source_doc: (if $source_doc == "" then null else $source_doc end)
  }' > "${OUTPUT_FILE}"

echo "Validation commands written to ${OUTPUT_FILE}"
